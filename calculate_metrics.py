#!/usr/bin/env python

# Calculate some station metrics - noise floor, power at different frequencies, Nspikes...

import os
import sys
from obspy import read
import numpy as np
from obspy.clients.fdsn import Client
from obspy import UTCDateTime
from obspy.signal.util import smooth
import datetime
from datetime import date
import time
import timeit
from obspy.signal.trigger import z_detect
from obspy.signal.trigger import classic_sta_lta
from obspy.signal.filter import envelope 
from obspy.signal.filter import bandpass
from obspy.signal import PPSD
from get_data_metadata import *
from noise_metrics import *
from plot_station import *
from obspy import Stream
from database_read_write import *

#----- Set up variables
chanfile = "CHANFILE"
datacenter = "DATACENTER"
sta = STA
lta = LTA
padding = PADDING
duration = DURATION
starttime = datetime.datetime(YEAR,MONTH,DAY,HOUR,MINUTE,SECOND)
endtime = starttime + datetime.timedelta(0,duration)
print "Starttime: " + str(starttime)
freqBP1 = fBP1
freqBP2 = fBP2
freqBP3 = fBP3
freqBP4 = fBP4
freqBB1 = fBB1
freqBB2 = fBB2
mpd = MPD
RMSlen = RMSLEN
GainOrFullResp = "GAINORFULLRESP"
#PSDperiods = [100,90,80,70,60,50,40,30,20,15,12,10,9,8,7,6,5,4,3,2,1,0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1,0.09,0.08,0.07,0.06,0.05,0.04,0.03,0.02,0.01 ]
PSDperiods = [50, 30, 20, 12, 10, 5, 1, 0.2, 0.1, 0.05, 0.02 ]

if ( "esp" in GainOrFullResp or "ESP" in GainOrFullResp ):
    ifullresp = 1
else: 
    ifullresp = 0
iplot = IPLOT   #---- careful: of order 25sec/channel for 1 hr long traces
dbname = "DBNAME"
hostname = "HOSTNAME"
dbuser = os.environ['POSTGRES_USER']
dbpass = os.environ['POSTGRES_PASSWD']

#----- Set up the FDSN client
try:
    client = Client(datacenter,timeout=300)
except:
    print "Failed client connection"
    exit()

#----- Read the database SNCL and METRIC tables to make ID lists

[sncl_list,sncl_id_list,metric_list,metric_id_list,dbconnection] = read_database(dbname,hostname,dbuser,dbpass)

#----- Download waveforms using channel list
tbuffer = sta + lta
Time1padded = starttime - datetime.timedelta(0,tbuffer+PADDING)
stAll = download_waveforms_fdsn_bulk(chanfile,Time1padded,duration+tbuffer+(2*padding),client)

#----- Get the time slices we want for analysis.
Time1 = starttime - datetime.timedelta(0,tbuffer)
Time2 = starttime + datetime.timedelta(0,duration)
lenrequested = (Time2-Time1).seconds

#----- Loop over stations.  If a station has gaps, a stream of that sncl will 
#-----      be made from all the traces.

itrace = 0
T0 = timeit.default_timer()
Tsum = 0
for i in range(0,len(stAll)):
    ntr = 1
    iduplicate = 0
    if ( stAll[i].stats.location == "" ):
        sncl = stAll[i].stats.network + "." + stAll[i].stats.station + ".--." + stAll[i].stats.channel
    else:
        sncl = stAll[i].stats.network + "." + stAll[i].stats.station + "." + stAll[i].stats.location + "." + stAll[i].stats.channel
    sncl_id = sncl_list.index(sncl)
    datasrc_id = 1
#    print "SNCL " + sncl + "  sncl_id " + str(sncl_id)
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
        trAccBroad = []
        trAccFilt = []
        trVelFilt = []
        stalta = []
        dataraw = []
        dataAccBroad = []
        dataAccFilt = []
        dataVelFilt = []
        datastalta = []
        nptstotal = 0
        inv = download_metadata_fdsn(stAll[i].stats.network, stAll[i].stats.station, stAll[i].stats.location, stAll[i].stats.channel, Time1, client)
        dt = stAll[j].stats.delta
        freqBB3 = 0.9 * (1/(2*dt))
        freqBB4 = 0.99 * (1/(2*dt))

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
            trAccBroad = raw_trace_to_ground_motion_filtered_pruned(trPadded,Time1,Time2,"Acc",0,freqBB1,freqBB2,freqBB3,freqBB4,inv).copy()
            trAccFilt = raw_trace_to_ground_motion_filtered_pruned(trPadded,Time1,Time2,"Acc",0,freqBP1,freqBP2,freqBP3,freqBP4,inv).copy()
            trVelFilt = raw_trace_to_ground_motion_filtered_pruned(trPadded,Time1,Time2,"Vel",0,freqBP1,freqBP2,freqBP3,freqBP4,inv).copy()
            stalta = trAccBroad.copy()
            dataraw = np.concatenate((dataraw,trRaw.data),axis=0)
            dataAccBroad = np.concatenate((dataAccBroad,trAccBroad.data),axis=0)
            dataAccFilt = np.concatenate((dataAccFilt,trAccFilt.data),axis=0)
            dataVelFilt = np.concatenate((dataVelFilt,trVelFilt.data),axis=0)

            if ( npts*dt > tbuffer ):
                stalta = z_detect(trAccBroad,int(1.0/dt))                      #--- of order 0.1 sec/trace 
#                stalta = classic_sta_lta(trAccBroad,int(sta/dt),int(lta/dt))  #--- of order 0.4 sec/trace
                datastalta = np.concatenate((datastalta,stalta),axis=0)
            else:
                datastalta = np.concatenate((datastalta,np.zeros(trAccBroad.stats.npts)),axis=0)
            if ( dt*npts > 3600.05 ):
                powers = get_power(trRaw,inv,PSDperiods)

            T2 = timeit.default_timer()
            if ( iplot == 1 ):
                if ( j == i ):
                    strawplot = Stream(traces=[trRaw])
                    stAccBroadplot = Stream(traces=[trAccBroad])
                    stAccFiltplot = Stream(traces=[trAccFilt])
                    stVelFiltplot = Stream(traces=[trVelFilt])
                else:
                    strawplot += Stream(traces=[trRaw])
                    stAccBroadplot += Stream(traces=[trAccBroad])
                    stAccFiltplot += Stream(traces=[trAccFilt])
                    stVelFiltplot += Stream(traces=[trVelFilt])
                if ( j == i + ntr -1 ):
                    AccBroadlabel = "cm/s^2 " + str(freqBB2) + "-" + str(freqBB3) + " Hz"
                    AccFiltlabel = "cm/s^2 " + str(freqBP2) + "-" + str(freqBP3) + " Hz"
                    VelFiltlabel = "cm/s " + str(freqBP2) + "-" + str(freqBP3) + " Hz"
                    for ij in range(0,len(stAccBroadplot)):
                        stAccBroadplot[ij].data = stAccBroadplot[ij].data*100
                        stAccFiltplot[ij].data = stAccFiltplot[ij].data*100
                        stVelFiltplot[ij].data = stVelFiltplot[ij].data*100
                    make_station_figure(strawplot,stAccBroadplot,stAccFiltplot,stVelFiltplot,datastalta,"Raw",AccBroadlabel,AccFiltlabel,VelFiltlabel,"Sta/Lta")  #--- of order 25sec/channel for 1 hr long traces
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

        snr10_0p01cm = count_peaks_stalta(dataAccBroad,datastalta,sta,lta,mpd,10,dt,0.0001)
        snr20_0p05cm = count_peaks_stalta(dataAccBroad,datastalta,sta,lta,mpd,20,dt,0.0005)  #--- of order 0.02 sec/trace each
        snr20_0p17cm = count_peaks_stalta(dataAccBroad,datastalta,sta,lta,mpd,20,dt,0.0017)  #--- ShakeAlert stat. acceptance thresh. is now 0.0035
        snr20_1cm = count_peaks_stalta(dataAccBroad,datastalta,sta,lta,mpd,20,dt,0.01)
        snr20_3cm = count_peaks_stalta(dataAccBroad,datastalta,sta,lta,mpd,20,dt,0.03)
        snr20_5cm = count_peaks_stalta(dataAccBroad,datastalta,sta,lta,mpd,20,dt,0.05)

        RMSduration_0p01cm = duration_exceed_RMS(dataAccBroad,0.0001,RMSlen,dt)  #--- of order 0.05 sec/trace each
        RMSduration_0p035cm = duration_exceed_RMS(dataAccBroad,0.00035,RMSlen,dt)  #--- ShakeAlert stat. acceptance thresh. is now 0.0007.
        RMSduration_0p1cm = duration_exceed_RMS(dataAccBroad,0.001,RMSlen,dt)
        RMSduration_1cm = duration_exceed_RMS(dataAccBroad,0.01,RMSlen,dt)

        numstring = "%d %d %d %d %d %d %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.6g %.6g %.4g %d    %.4g %.4g %.4g %.4g " % ( snr10_0p01cm, snr20_0p05cm, snr20_0p17cm, snr20_1cm, snr20_3cm, snr20_5cm, pow50sec, pow30sec, pow20sec, pow10sec, pow5sec, pow1Hz, pow5Hz, pow10Hz, pow20Hz, pow50Hz, NoiseFloorAcc, NoiseFloorVel, rawrange, rawmean, rawrms, rawmin, rawmax, segmentshort, segmentlong, pctavailable, ngaps, RMSduration_0p01cm, RMSduration_0p035cm, RMSduration_0p1cm, RMSduration_1cm )

        metriclist = [ "snr10_0p01cm", "snr20_0p05cm", "snr20_0p17cm", "snr20_1cm", "snr20_3cm", "snr20_5cm", "pow50sec", "pow30sec", "pow20sec", "pow12sec", "pow10sec", "pow5sec", "pow1Hz", "pow5Hz", "pow10Hz", "pow20Hz", "pow50Hz", "NoiseFloorAcc", "NoiseFloorVel", "rawrange", "rawmean", "rawrms", "rawmin", "rawmax", "segmentshort", "segmentlong", "pctavailable", "ngaps", "RMSduration_0p01cm", "RMSduration_0p035cm", "RMSduration_0p1cm", "RMSduration_1cm" ] 
        valuelist = [ snr10_0p01cm, snr20_0p05cm, snr20_0p17cm, snr20_1cm, snr20_3cm, snr20_5cm, pow50sec, pow30sec, pow20sec, pow12sec, pow10sec, pow5sec, pow1Hz, pow5Hz, pow10Hz, pow20Hz, pow50Hz, NoiseFloorAcc, NoiseFloorVel, rawrange, rawmean, rawrms, rawmin, rawmax, segmentshort, segmentlong, pctavailable, ngaps, RMSduration_0p01cm, RMSduration_0p035cm, RMSduration_0p1cm, RMSduration_1cm  ]

        T1 = timeit.default_timer()
        write_database(dbconnection,sncl_id,starttime,endtime,datasrc_id,metriclist,valuelist,metric_list,metric_id_list)
        T2 = timeit.default_timer()
        Tsum = Tsum + T2 - T1

        print sncl + " " + numstring + "          ------" + str(itrace) + " " + str(T2-T1) + "  " + str(T2-T0)

