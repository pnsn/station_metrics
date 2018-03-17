#!/home/ahutko/anaconda3/bin/python
##!/usr/bin/env python

# Calculate some station metrics - noise floor, power at different frequencies, Nspikes...

import argparse
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
from obspy import Stream
from get_data_metadata import *
from noise_metrics import *
########from plot_station import *

from plot_station2 import *
#from plot_station import *

from parse_and_validate_args import *

#----- hardwired parameters for ShakeAlert acceptance
FDSNtimeout = 24   #--- FDSN client timeout
tpadding = 120
sta = 0.05
lta = 5.0
tbuffer = sta + lta
freqBP1 = 0.25
freqBP2 = 0.3
freqBP3 = 15.0
freqBP4 = 17.0
freqBB1 = 0.01
freqBB2 = 0.02
mpd = 10.0
RMSlen = 5.0
GainOrFullResp = "Gain"
PSDperiods = [50, 30, 20, 12, 10, 5, 1, 0.2, 0.1, 0.05, 0.02]
iplot = 0

T0 = timeit.default_timer()

#----- read input arguments

args = parse_args()
[ starttime, endtime, durationinhours, durationinsec ] = validate_args_and_get_times(args)
infile = args.infile
network = args.network
station = args.station
channel = args.channel
location = args.location
datacenter = args.datacenter
iplot = args.iplot

#print ("start " + str(starttime) + " " + str(endtime) + " " + str(durationinhours) + " " + str(durationinsec) + " " + datacenter + " " + str(type(durationinhours)) + " " + str(type(durationinsec))  )

#----- Set up the FDSN client

try:
    client = Client(datacenter,timeout = FDSNtimeout)
except:
    print ( "Failed to connect to FDSN client. Used a timeout of " + str(FDSNtimeout) )

#----- Download waveform(s) 

Time1padded = starttime - datetime.timedelta(0,tbuffer+tpadding)

if ( infile is None ):
    stAll = download_waveform_single_trace(network,station,location,channel,Time1padded,durationinsec+tbuffer+(2*tpadding),client)
else:
    stAll = download_waveforms_fdsn_bulk(infile,Time1padded,durationinsec+tbuffer+(2*tpadding),client)
print("")

#----- Get the time slices to analyze.

Time1 = starttime - datetime.timedelta(0,tbuffer)
Time2 = starttime + datetime.timedelta(0,durationinsec)
lenrequested = (Time2-Time1).seconds

#----- Loop over seismograms.  If a station has gaps, a stream of that sncl will 
#----- be made from all the traces.

itrace = 0
T1 = timeit.default_timer()
Tsum = 0
for i in range(0,len(stAll)):
    ntr = 1
    iduplicate = 0
    if ( stAll[i].stats.location == "" ):
        sncl = stAll[i].stats.network + "." + stAll[i].stats.station + ".--." + stAll[i].stats.channel
    else:
        sncl = stAll[i].stats.network + "." + stAll[i].stats.station + "." + stAll[i].stats.location + "." + stAll[i].stats.channel
#    print "SNCL " + sncl 
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
#                stalta = z_detect(trAccBroad,int(1.0/dt))                      #--- of order 0.1 sec/trace 
                stalta = classic_sta_lta(trAccBroad,int(sta/dt),int(lta/dt))  #--- of order 0.4 sec/trace
                datastalta = np.concatenate((datastalta,stalta),axis=0)
            else:
                datastalta = np.concatenate((datastalta,np.zeros(trAccBroad.stats.npts)),axis=0)
            T3 = timeit.default_timer()
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
#                    AccBroadlabel = "Acc " + str(freqBB2) + "-" + str(freqBB3) + " Hz (cm/s^2)"
#                    AccFiltlabel = "Acc " + str(freqBP2) + "-" + str(freqBP3) + " Hz (cm/s^2)"
#                    VelFiltlabel = "Vel " + str(freqBP2) + "-" + str(freqBP3) + " Hz (cm/s)"
                    AccBroadlabel = str(freqBB2) + "-" + str(freqBB3) + "Hz RMS Acc (cm/s^2)"
                    AccFiltlabel =  str(freqBP2) + "-" + str(freqBP3) + "Hz Spikes Acc (cm/s^2)"
                    VelFiltlabel =  str(freqBP2) + "-" + str(freqBP3) + "Hz Vel (cm/s)"
                    for ij in range(0,len(stAccBroadplot)):
                        stAccBroadplot[ij].data = stAccBroadplot[ij].data*100
                        stAccFiltplot[ij].data = stAccFiltplot[ij].data*100
                        stVelFiltplot[ij].data = stVelFiltplot[ij].data*100



                    from obspy.signal.util import smooth
                    iRMSwinlen = int(5.0/dt)
                    rmsthing = np.sqrt(smooth(((stAccFiltplot[ij].data*100)**2),iRMSwinlen))


# for RMS plot

#                    st1 = stAccFiltplot.copy()
#                    import obspy.signal
#                    env = obspy.signal.filter.envelope(st1[0].data)
#                    for ijk in range(0,len(env)):
#                        print (str(st1[0].data[ijk]) + " " + str(env[ijk]))

#                    make_station_figure_talk(strawplot,stVelFiltplot,stAccFiltplot,stAccFiltplot,env,"Raw",VelFiltlabel,AccBroadlabel,AccFiltlabel,"Sta/Lta",0,0,0.07,0.34,0)  #--- of order 25sec/channel for 1 hr long traces
                    make_station_figure_talk(strawplot,stVelFiltplot,stAccFiltplot,stAccFiltplot,datastalta,"Raw",VelFiltlabel,AccBroadlabel,AccFiltlabel,"Sta/Lta",0,0,0.07,0.34,20)  #--- of order 25sec/channel for 1 hr long traces


#                    make_station_figure_wthresholds(strawplot,stVelFiltplot,stAccFiltplot,stAccFiltplot,datastalta,"Raw",VelFiltlabel,AccBroadlabel,AccFiltlabel,"Sta/Lta",0,0,0,0.34,20)  #--- of order 25sec/channel for 1 hr long traces

# default
#                    make_station_figure_wthresholds(strawplot,stVelFiltplot,stAccBroadplot,stAccFiltplot,datastalta,"Raw",VelFiltlabel,AccBroadlabel,AccFiltlabel,"Sta/Lta",0,0,0.07,0.34,20)  #--- of order 25sec/channel for 1 hr long traces

# old one
#                    make_station_figure(strawplot,stVelFiltplot,stAccBroadplot,stAccFiltplot,datastalta,"Raw",VelFiltlabel,AccBroadlabel,AccFiltlabel,"Sta/Lta")  #--- of order 25sec/channel for 1 hr long traces
            T4 = timeit.default_timer()
            Tplot = T4-T3

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
        snr20_0p34cm = count_peaks_stalta(dataAccBroad,datastalta,sta,lta,mpd,20,dt,0.0034)  #--- ShakeAlert stat. acceptance thresh. is now 0.0034
        RMSduration_0p07cm = duration_exceed_RMS(dataAccBroad,0.0007,RMSlen,dt)  #--- ShakeAlert stat. acceptance thresh. is now 0.0007.
        T2 = timeit.default_timer()

        if ( ngaps/durationinhours < 1.0 ):
            strngap = "ngaps_PASS: " + str(ngaps/durationinhours)
            strngap = str( "ngaps_PASS: %.3f " % (ngaps/durationinhours) )
        else:
            strngap = "ngaps_FAIL: " + str(ngaps/durationinhours)
            strngap = str( "ngaps_FAIL: %.3f " % (ngaps/durationinhours) )

        if ( RMSduration_0p07cm/durationinhours < 60. ):
            strrms = "rms_PASS: " + str(RMSduration_0p07cm/durationinhours)
            strrms = str( "rms_PASS: %.3f " % (RMSduration_0p07cm/durationinhours) )
        else:
            strrms = "rms_FAIL: " + str(RMSduration_0p07cm/durationinhours)
            strrms = str( "rms_FAIL: %.3f " % (RMSduration_0p07cm/durationinhours) )

        if ( snr20_0p34cm/durationinhours < 1.0 ):
            strnspikes = "nspikes_PASS: " + str(snr20_0p34cm/durationinhours)
            strnspikes = str( "nspikes_PASS: %.3f " % (snr20_0p34cm/durationinhours) )
        else:
            strnspikes = "nspikes_FAIL: " + str(snr20_0p34cm/durationinhours)
            strnspikes = str( "nspikes_FAIL: %.3f " % (snr20_0p34cm/durationinhours) )

        if ( 100*dt*nptstotal/lenrequested < 95 ):
            strpctavail = str( "pctavailable_PASS: %.4f " % (100*dt*nptstotal/lenrequested) )
        else:
            strpctavail = str( "pctavailable_FAIL: %.4f " % (100*dt*nptstotal/lenrequested) )

#        print ( sncl + " " + " download: " + str(T1-T0) + "s  calculate: " + str(T2-T1) + "s " + " " + strngap + " " + strrms + " " + strnspikes + " " + strpctavail + " Nsegments: " + str(itrace) + " segmentlong: " + str(segmentlong) + "s segmentshort: " + str(segmentshort) + "s" )
#        print ("")
        print ( "%s  download: %.2fs calculate: %.2fs plot: %.2fs %s %s %s %s  Nsegments: %d  segmentlong: %.3f  segmentshort: %.3f " % (sncl, T1-T0, T2-T1-Tplot, Tplot, strngap, strrms, strnspikes, strpctavail, itrace, segmentlong, segmentshort) )
        print ("")


