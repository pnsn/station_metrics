#!/usr/bin/env python

# Calculate some station metrics - noise floor, power at different frequencies, Nspikes...

from __future__ import print_function

# import std packages
import os
import sys
import datetime
from datetime import date
import time
import timeit

# import third party packages
import numpy as np
from obspy import read
from obspy.clients.fdsn import Client
from obspy import UTCDateTime
from obspy.signal.util import smooth
from obspy.signal.trigger import z_detect
from obspy.signal.trigger import classic_sta_lta
from obspy.signal.filter import envelope 
from obspy.signal.filter import bandpass
from obspy.signal import PPSD
from obspy import Stream
try:
    from ConfigParser import SafeConfigParser
except:
    from configparser import SafeConfigParser

# import station_metrics packages
from station_metrics.io.get_data_metadata import *
from station_metrics.metrics.preprocessing import *
from station_metrics.metrics.noise_metrics import *
from station_metrics.plotting.plot_station import make_station_figure
from config.parse_and_validate_args import validate_args_and_get_times, parse_args
from station_metrics.db.database_read_write import *

#----- read config file

parser = SafeConfigParser()
parser.read("config/config.db")

FDSNtimeout = float(parser.get('SectionOne','FDSNtimeout'))
tpadding = float(parser.get('SectionOne','tpadding'))
sta = float(parser.get('SectionOne','sta'))
lta = float(parser.get('SectionOne','lta'))
tbuffer = sta + lta
freqBP1 = float(parser.get('SectionOne','freqBP1'))
freqBP2 = float(parser.get('SectionOne','freqBP2'))
freqBP3 = float(parser.get('SectionOne','freqBP3'))
freqBP4 = float(parser.get('SectionOne','freqBP4'))
freqHP = float(parser.get('SectionOne','freqHP'))
mpd = float(parser.get('SectionOne','mpd'))
RMSlen = float(parser.get('SectionOne','RMSlen'))
GainOrFullResp = parser.get('SectionOne','GainOrFullResp')
PSDperiods = (parser.get('SectionOne','PSDperiods'))[1:-1].split(",")
PSDperiods = [float(i) for i in PSDperiods]
iplot = parser.get('SectionOne','iplot')
dbname = parser.get('SectionOne','dbname')
hostname = parser.get('SectionOne','hostname')
try:
    dbuser = os.environ['POSTGRES_USER']
    dbpass = os.environ['POSTGRES_PASSWD']
except:
    dbuser = None
    dbpass = None

#----- read input arguments

args = parse_args()
[ starttime, endtime, durationinhours, durationinsec ] = validate_args_and_get_times(args)
infile = args.infile
datacenter = args.datacenter

if ( "esp" in GainOrFullResp or "ESP" in GainOrFullResp ):
    ifullresp = 1
else: 
    ifullresp = 0

#----- Set up the FDSN client
try:
    client = Client(datacenter,timeout = FDSNtimeout)
except:
    print ("Failed client connection" )
    exit()

#----- Read the database SNCL and METRIC tables to make ID lists

if ( dbname is not None and dbpass is not None ):
    try:
        [sncl_list,sncl_id_list,metric_list,metric_id_list,dbconnection] = read_database(dbname,hostname,dbuser,dbpass)
        db = True
    except:
        db = False
else:
    db = False

#----- Download waveforms using channel list
tbuffer = sta + lta
Time1padded = starttime - datetime.timedelta(0,tbuffer+tpadding)
stAll = download_fdsn_bulk(infile,Time1padded,durationinsec+tbuffer+(2*tpadding),client)

#----- Get the time slices we want for analysis.
Time1 = starttime - datetime.timedelta(0,tbuffer)
Time2 = starttime + datetime.timedelta(0,durationinsec)
lenrequested = (Time2-Time1).total_seconds()

#----- Loop over stations.  If a station has gaps, a stream of that sncl will 
#-----      be made from all the traces.

itrace = 0
T0 = timeit.default_timer()
Tsum = 0
for i in range(0,len(stAll)):
    T1 = timeit.default_timer()
    ntr = 1
    iduplicate = 0
    if ( stAll[i].stats.location == "" ):
        sncl = stAll[i].stats.network + "." + stAll[i].stats.station + ".--." + stAll[i].stats.channel
    else:
        sncl = stAll[i].stats.network + "." + stAll[i].stats.station + "." + stAll[i].stats.location + "." + stAll[i].stats.channel
    if ( db == True ):
        sncl_id = sncl_list.index(sncl) + 1   #--- make sure you add 1
        datasrc_id = 1
#    print ("SNCL " + sncl + "  sncl_id " + str(sncl_id) )
    for j in range(0,len(stAll)):
        if ( stAll[j].stats.location == "" ):
            sncl2 = stAll[j].stats.network + "." + stAll[j].stats.station + ".--." + stAll[j].stats.channel
        else:
            sncl2 = stAll[j].stats.network + "." + stAll[j].stats.station + "." + stAll[j].stats.location + "." + stAll[j].stats.channel
        if ( sncl == sncl2 and i != j ):
            if ( j < i ):
                iduplicate = 1
                break
            else:
                ntr = ntr + 1
    if ( iduplicate == 0 ):
        itrace = itrace + 1
        tr = []
        trRaw = []
        trVelHighPass = []
        trAccFilt = []
        trVelFilt = []
        stalta = []
        dataraw = []
        dataVelHighPass = []
        dataAccFilt = []
        dataVelFilt = []
        datastalta = []
        nptstotal = 0
        inv = download_metadata_fdsn(client,stAll[i].stats.network, stAll[i].stats.station, stAll[i].stats.location, stAll[i].stats.channel, Time1)
        dt = stAll[i].stats.delta

        powers = np.zeros(len(PSDperiods))
        segmentlong = 0
        segmentshort = 9e6
        for j in range(i,i+ntr):
            trRaw = stAll[j].copy()
            trRaw = trRaw.slice(UTCDateTime(Time1),UTCDateTime(Time2))
            npts = trRaw.stats.npts
            nptstotal = nptstotal + npts
            trPadded = stAll[j].copy()
            trPadded = trPadded.detrend(type='polynomial',order=3)
            if ( dt*npts > segmentlong ):
                segmentlong = dt*npts
            if ( dt*npts < segmentshort ):
                segmentshort = dt*npts
            trVelHighPass = raw_trace_to_ground_motion_filtered_pruned(trPadded,Time1,Time2,"Vel",ifullresp,0,freqHP,0,0,inv).copy()
            trAccFilt = raw_trace_to_ground_motion_filtered_pruned(trPadded,Time1,Time2,"Acc",ifullresp,freqBP1,freqBP2,freqBP3,freqBP4,inv).copy()
            trVelFilt = raw_trace_to_ground_motion_filtered_pruned(trPadded,Time1,Time2,"Vel",ifullresp,freqBP1,freqBP2,freqBP3,freqBP4,inv).copy()
            stalta = trVelHighPass.copy()
            dataraw = np.concatenate((dataraw,trRaw.data),axis=0)
            dataVelHighPass = np.concatenate((dataVelHighPass,trVelHighPass.data),axis=0)
            dataAccFilt = np.concatenate((dataAccFilt,trAccFilt.data),axis=0)
            dataVelFilt = np.concatenate((dataVelFilt,trVelFilt.data),axis=0)

            if ( npts*dt > tbuffer ):
#                stalta = z_detect(trVelHighPass,int(0.05/dt))                   #--- of order 0.1 sec/trace. changed to VelHP 07/2018
                stalta = classic_sta_lta(trVelHighPass,int(sta/dt),int(lta/dt))  #--- of order 0.5 sec/trace
                datastalta = np.concatenate((datastalta,stalta),axis=0)
            else:
                datastalta = np.concatenate((datastalta,np.zeros(trVelHighPass.stats.npts)),axis=0)
            if ( dt*npts > 3600.05 ):
                powers = get_power(trRaw,inv,PSDperiods)

            T2 = timeit.default_timer()
            if ( iplot == 1 ):
                if ( j == i ):
                    strawplot = Stream(traces=[trRaw])
                    stVelHighPassplot = Stream(traces=[trVelHighPass])
                    stAccFiltplot = Stream(traces=[trAccFilt])
                    stVelFiltplot = Stream(traces=[trVelFilt])
                else:
                    strawplot += Stream(traces=[trRaw])
                    stVelHighPassplot += Stream(traces=[trVelHighPass])
                    stAccFiltplot += Stream(traces=[trAccFilt])
                    stVelFiltplot += Stream(traces=[trVelFilt])
                if ( j == i + ntr -1 ):
                    VelHighPasslabel = "cm/s " + ">" + str(freqHP) + " Hz"
                    AccFiltlabel = "cm/s^2 " + str(freqBP2) + "-" + str(freqBP3) + " Hz"
                    VelFiltlabel = "cm/s " + str(freqBP2) + "-" + str(freqBP3) + " Hz"
                    for ij in range(0,len(stVelHighPassplot)):
                        stVelHighPassplot[ij].data = stVelHighPassplot[ij].data*100
                        stAccFiltplot[ij].data = stAccFiltplot[ij].data*100
                        stVelFiltplot[ij].data = stVelFiltplot[ij].data*100
                    make_station_figure(strawplot,stVelHighPassplot,stAccFiltplot,stVelFiltplot,datastalta,"Raw",VelHighPasslabel,AccFiltlabel,VelFiltlabel,"Sta/Lta")  #--- of order 25sec/channel for 1 hr long traces
            T3 = timeit.default_timer()

        pow50sec = powers[0]
        pow30sec = powers[1]
        pow20sec = powers[2]
        pow12sec = powers[3]
        pow10sec = powers[4]
        pow5sec = powers[5]
        pow1Hz = powers[6]
        pow5Hz = powers[7]
        pow10Hz = powers[8]
        pow20Hz = powers[9]
        pow50Hz = powers[10]

        rawrange = float(np.ptp(dataraw))
        rawmean = np.mean(dataraw)
#        rawrms = np.sqrt(np.vdot(dataraw, dataraw)/dataraw.size)
        rawrms = np.sqrt(np.mean((dataraw-rawmean)**2))
        rawmin = min(dataraw)
        rawmax = max(dataraw)
        pctavailable = 100.*(nptstotal/(lenrequested/dt))
        ngaps = ntr - 1

        NoiseFloorAcc = noise_floor(dataAccFilt)
        NoiseFloorVel = noise_floor(dataVelFilt)

        snr10_0p01cm = count_peaks_stalta(dataAccFilt,datastalta,sta,lta,mpd,10,dt,0.0001)
        snr20_0p05cm = count_peaks_stalta(dataAccFilt,datastalta,sta,lta,mpd,20,dt,0.0005)  #--- of order 0.02 sec/trace each
        snr20_0p17cm = count_peaks_stalta(dataAccFilt,datastalta,sta,lta,mpd,20,dt,0.0017)  #--- 2017 ShakeAlert stat. acceptance thresh.
        snr20_0p34cm = count_peaks_stalta(dataAccFilt,datastalta,sta,lta,mpd,20,dt,0.0034)  #--- 2018 ShakeAlert stat. acceptance thresh.
        snr20_1cm = count_peaks_stalta(dataAccFilt,datastalta,sta,lta,mpd,20,dt,0.01)
        snr20_3cm = count_peaks_stalta(dataAccFilt,datastalta,sta,lta,mpd,20,dt,0.03)
        snr20_5cm = count_peaks_stalta(dataAccFilt,datastalta,sta,lta,mpd,20,dt,0.05)

        RMSduration_0p01cm = duration_exceed_RMS(dataAccFilt,0.0001,RMSlen,dt)  #--- of order 0.05 sec/trace each
        RMSduration_0p035cm = duration_exceed_RMS(dataAccFilt,0.00035,RMSlen,dt)  #--- 2017 ShakeAlert stat. acceptance thresh.
        RMSduration_0p07cm = duration_exceed_RMS(dataAccFilt,0.0007,RMSlen,dt)  #--- 2018 ShakeAlert stat. acceptance thresh. 
        RMSduration_0p1cm = duration_exceed_RMS(dataAccFilt,0.001,RMSlen,dt)
        RMSduration_1cm = duration_exceed_RMS(dataAccFilt,0.01,RMSlen,dt)

        numstring = "%d %d %d %d %d %d %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.6g %.6g %.4g %d    %.4g %.4g %.4g %.4g  %.4g %d" % ( snr10_0p01cm, snr20_0p05cm, snr20_0p17cm, snr20_1cm, snr20_3cm, snr20_5cm, pow50sec, pow30sec, pow20sec, pow10sec, pow5sec, pow1Hz, pow5Hz, pow10Hz, pow20Hz, pow50Hz, NoiseFloorAcc, NoiseFloorVel, rawrange, rawmean, rawrms, rawmin, rawmax, segmentshort, segmentlong, pctavailable, ngaps, RMSduration_0p01cm, RMSduration_0p035cm, RMSduration_0p1cm, RMSduration_1cm, RMSduration_0p07cm, snr20_0p34cm )

        metriclist = [ "snr10_0p01cm", "snr20_0p05cm", "snr20_0p17cm", "snr20_0p34cm", "snr20_1cm", "snr20_3cm", "snr20_5cm", "pow50sec", "pow30sec", "pow20sec", "pow12sec", "pow10sec", "pow5sec", "pow1Hz", "pow5Hz", "pow10Hz", "pow20Hz", "pow50Hz", "NoiseFloorAcc", "NoiseFloorVel", "rawrange", "rawmean", "rawrms", "rawmin", "rawmax", "segmentshort", "segmentlong", "pctavailable", "ngaps", "RMSduration_0p01cm", "RMSduration_0p035cm", "RMSduration_0p07cm", "RMSduration_0p1cm", "RMSduration_1cm" ] 
        valuelist = [ snr10_0p01cm, snr20_0p05cm, snr20_0p17cm, snr20_0p34cm, snr20_1cm, snr20_3cm, snr20_5cm, pow50sec, pow30sec, pow20sec, pow12sec, pow10sec, pow5sec, pow1Hz, pow5Hz, pow10Hz, pow20Hz, pow50Hz, NoiseFloorAcc, NoiseFloorVel, rawrange, rawmean, rawrms, rawmin, rawmax, segmentshort, segmentlong, pctavailable, ngaps, RMSduration_0p01cm, RMSduration_0p035cm, RMSduration_0p07cm, RMSduration_0p1cm, RMSduration_1cm  ]

#        T1 = timeit.default_timer()
        if ( db == True ):
            write_database(dbconnection,sncl_id,starttime,endtime,datasrc_id,metriclist,valuelist,metric_list,metric_id_list)
        T2 = timeit.default_timer()
        Tsum = Tsum + T2 - T1

        print (sncl + " " + numstring + "          ------" + str(itrace) + " " + str(T2-T1) + "  " + str(T2-T0) )

