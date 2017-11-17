#!/usr/bin/env/python

#
# Calculate some station metrics - noise floor, power at different frequencies, Nspikes...
# Note, the RMS metrics are not being written out in this version.  :-/

import sys
from obspy import read
import numpy as np
from obspy.clients.fdsn import Client
listname = "LIST"
if ( listname[0:3] == "IRI" ):
    clientname = "IRIS"
if ( listname[0:3] == "SCE" ):
    clientname = "SCEDC"
if ( listname[0:3] == "NCE" ):
    clientname = "NCEDC"
try:
    client = Client(clientname)
except:
    client = Client("IRIS")
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
from scipy import signal
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.dates import DateFormatter

#------ set up local Earthworm client to read new CN data
from obspy.clients.earthworm import Client as ClientEW
from obspy import read_inventory
host = "ewXX.ess.washington.edu"
port = 16XXX
clientEWS1 = ClientEW(host,port,timeout=5)

#--------- to plot or not to plot, that is the question
iplot = 0
ifullresp = IFULLRESP
if ( ifullresp == 0 ):
    ifullresptxt = "GAIN"
else:
    ifullresptxt = "FULLRESP"

#--------------------------

def detect_peaks(x, mph=None, mpd=1, threshold=0, edge='rising',kpsh=False, valley=False, show=False, ax=None):
    x = np.atleast_1d(x).astype('float64')
    if x.size < 3:
        return np.array([], dtype=int)
    if valley:
        x = -x
    # find indices of all peaks
    dx = x[1:] - x[:-1]
    # handle NaN's
    indnan = np.where(np.isnan(x))[0]
    if indnan.size:
        x[indnan] = np.inf
        dx[np.where(np.isnan(dx))[0]] = np.inf
    ine, ire, ife = np.array([[], [], []], dtype=int)
    if not edge:
        ine = np.where((np.hstack((dx, 0)) < 0) & (np.hstack((0, dx)) > 0))[0]
    else:
        if edge.lower() in ['rising', 'both']:
            ire = np.where((np.hstack((dx, 0)) <= 0) & (np.hstack((0, dx)) > 0))[0]
        if edge.lower() in ['falling', 'both']:
            ife = np.where((np.hstack((dx, 0)) < 0) & (np.hstack((0, dx)) >= 0))[0]
    ind = np.unique(np.hstack((ine, ire, ife)))
    # handle NaN's
    if ind.size and indnan.size:
        # NaN's and values close to NaN's cannot be peaks
        ind = ind[np.in1d(ind, np.unique(np.hstack((indnan, indnan-1, indnan+1))), invert=True)]
    # first and last values of x cannot be peaks
    if ind.size and ind[0] == 0:
        ind = ind[1:]
    if ind.size and ind[-1] == x.size-1:
        ind = ind[:-1]
    # remove peaks < minimum peak height
    if ind.size and mph is not None:
        ind = ind[x[ind] >= mph]
    # remove peaks - neighbors < threshold
    if ind.size and threshold > 0:
        dx = np.min(np.vstack([x[ind]-x[ind-1], x[ind]-x[ind+1]]), axis=0)
        ind = np.delete(ind, np.where(dx < threshold)[0])
    # detect small peaks closer than minimum peak distance
    if ind.size and mpd > 1:
        ind = ind[np.argsort(x[ind])][::-1]  # sort ind by peak height
        idel = np.zeros(ind.size, dtype=bool)
        for i in range(ind.size):
            if not idel[i]:
                # keep peaks with the same height if kpsh is True
                idel = idel | (ind >= ind[i] - mpd) & (ind <= ind[i] + mpd) \
                    & (x[ind[i]] > x[ind] if kpsh else True)
                idel[i] = 0  # Keep current peak
        # remove the small peaks and sort back the indices by their occurrence
        ind = np.sort(ind[~idel])
    if show:
        if indnan.size:
            x[indnan] = np.nan
        if valley:
            x = -x
        _plot(x, mph, mpd, threshold, edge, valley, ax, ind)
    return ind

#--------------------------

timeclient=0
timeloop=0
timeplot=0

begintime = timeit.default_timer()
now = datetime.datetime.utcnow()
print ("Current UTC time: " + str(now))

stalen = 0.05
ltalen = 5.0

#------- 1 hour of recent data
tbuffer = stalen+stalen+ltalen   #--- add at least 1 extra sec to ensure PSD can be calculated
tbuffer = max(tbuffer,0.2)
MINUTE = 0
SECOND = 0
now = datetime.datetime(YEAR,MONTH,DAY,HOUR,MINUTE,SECOND)

#------ pad the request a bit since the broadband filter has a low freq corner of 50sec
T1 = now - datetime.timedelta(0,tbuffer+60+1)
T2 = T1 + datetime.timedelta(0,3600+120+tbuffer)
T1notaper = T1 + datetime.timedelta(0,60)
T2notaper = T2 - datetime.timedelta(0,60)

t1 = datetime.datetime(T1.year,T1.month,T1.day,T1.hour,T1.minute,T1.second) - datetime.timedelta(seconds=10)
t2 = datetime.datetime(T2.year,T2.month,T2.day,T2.hour,T2.minute,T2.second) + datetime.timedelta(seconds=10)
timediffinsec = (t2-t1).total_seconds()
ttitle = t1 + datetime.timedelta(seconds=timediffinsec*0.15)
lenrequested = (T2notaper-T1notaper).seconds

T3 = now - datetime.timedelta(0,3600*7)
iday = date.weekday(T3)
DoW = [ "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun" ]

print str( 'Time range: ' + str(T1) + ' ' + str(T2) + ' Pacific Time: ' + str(T3) + ' day of week: ' + DoW[iday] )

#----- read station list
f1 = open('ShakeAlertList.LIST')
lines = f1.readlines()
f1.close()

#----- set up output file
filename = 'IGORMETRICS.' + ifullresptxt + "." + str(ttitle.year) + '.' + str(ttitle.month) + '.' + str(ttitle.day) + '.' + str(ttitle.hour) + '.LIST.txt'
f2 = open(filename,'w')
#psdfilename = 'PSD.' + str(ttitle.year) + '.' + str(ttitle.month) + '.' + str(ttitle.day) + '.' + str(ttitle.hour) + '.LIST.txt'
#f3 = open(psdfilename,'w')

#----- set up filters
filtermetrics = (0.93, 1.0, 5.0, 5.3 )  #--- this is the band for metrics for measuring noise, RMS, spikes...
filterbroad = (0.01,0.02,45.0,49.9)

#----- loop over stations.  Download and process one at a time = good FDSNWS user behavior.
for i in range(0,len(lines)):
    time.sleep(0.05)
    starttimeloop = timeit.default_timer()
    net = lines[i].split()[0]
    stat = lines[i].split()[1]
    loc = lines[i].split()[2]
    chan = lines[i].split()[3]
    SNCL = net + '.' + stat + '.' + loc + '.' + chan
    st = []
    if ( len(st) > 0 ):
        st.clear()
        stV.clear()
        stA.clear()
        filtA2.clear()
        stalta.clear()

    #----- try the (faster) FDSNWS client first
    try:
        availability = client.get_stations(network=net,station=stat,channel=chan,starttime=UTCDateTime(T1),endtime=UTCDateTime(T2),level='station')
        if ( len(availability) > 0 ):
            try:
                starttimeclient = timeit.default_timer()
                st = client.get_waveforms(net,stat,loc,chan,UTCDateTime(T1),UTCDateTime(T2))
                inventory = client.get_stations(network=net,station=stat,channel=chan,starttime=UTCDateTime(T1),endtime=UTCDateTime(T2),level='response')
                endtimeclient = timeit.default_timer()
                timeclient=timeclient+(endtimeclient-starttimeclient)
            except:
                ijunk = 1
    except:
        ijunk = 1

    #----- then try the slower internal ewserver1 for stations that are internal only
    if ( len(st) == 0 ):
        try:
            availability = clientEWS1.get_availability(network=net,station=stat,channel=chan)
            if ( len(availability) > 0 ):
                try:
                    starttimeclient = timeit.default_timer()
                    st = clientEWS1.get_waveforms(net,stat,loc,chan,UTCDateTime(T1),UTCDateTime(T2))
                    try:  #---- try first to get metadata from FDSN WS
                        inventory = client.get_stations(network=net,station=stat,channel=chan,starttime=UTCDateTime(T1),endtime=UTCDateTime(T2),level='response')
                    except:
                        if ( net == "CN" ):
                            inventory = inv = read_inventory("/home/ahutko/STATION_REPORT/CN.xml")
                    endtimeclient = timeit.default_timer()
                    timeclient=timeclient+(endtimeclient-starttimeclient)
                except:
                    ijunk = 1
        except:
            ijunk = 1

    indexlocalmax = []
    numstring = "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"   # 34 zeros
    if ( len(st) > 0 ):
        iflag = 0
        stV = st.copy()
        stA = st.copy()
        iflag = 1
        stV.detrend(type='demean')
        stA.detrend(type='demean')
        iflag = 2
        try:
            #---- Use this to get rid of long period noise
            filt3 = 0.9*(st[0].stats.sampling_rate/2.)
            filt4 = 0.999*(st[0].stats.sampling_rate/2.)
            filterbroad = (0.01,0.02,filt3,filt4)
            iflag = 3
            #---- Get Velocity and Acceleration versions of each trace
            #-- Remove the full response (~5sec/hour long trace)
            if ( ifullresp == 1 ):
                iflag = 4
                stV.remove_response(inventory=inventory, output='VEL', pre_filt=filtermetrics)
                stA.remove_response(inventory=inventory, output='ACC', pre_filt=filterbroad)
                iflag = 5
                st = st.slice(UTCDateTime(T1notaper),UTCDateTime(T2notaper))
                stV = stV.slice(UTCDateTime(T1notaper),UTCDateTime(T2notaper))
                stA = stA.slice(UTCDateTime(T1notaper),UTCDateTime(T2notaper))
                iflag = 6
            #-- Convert to ground motion using just the gain factor
            else:
                iflag = 7
                stV.remove_sensitivity(inventory)
                stA.remove_sensitivity(inventory)
                iflag = 8
                stV.filter("bandpass",freqmin = 1.0, freqmax = 5.0)
                stA.filter("bandpass",freqmin = 0.02, freqmax = filt3)
                iflag = 9
                st = st.slice(UTCDateTime(T1notaper),UTCDateTime(T2notaper))
                stV = stV.slice(UTCDateTime(T1notaper),UTCDateTime(T2notaper))
                stA = stA.slice(UTCDateTime(T1notaper),UTCDateTime(T2notaper))
                iflag = 10
                stV.detrend(type='polynomial',order=3)
                stA.detrend(type='polynomial',order=3)
                iflag = 11
                if ( chan[1:2] == "N" ):
                    stV.integrate(method='cumtrapz')
                    iflag = 12
                else:
                    stA.differentiate(method='gradient')
                    iflag = 13
        except:
            #----- Couldn't get response/gain factor, so dump the trace.
            print ( "NUKING TRACE " + SNCL + " iflag: " + str(iflag) ) 
            st.clear()
            stV.clear()
            stA.clear()
            st = []
            stV = []
            stA = []
    if ( len(st) > 0 ):
      if ( len(stA) > 0 ):
        stV.detrend(type='polynomial',order=3) 
        stA.detrend(type='polynomial',order=3)
        dt = stA[0].stats.delta
        stalta = stA.copy()
        dataraw = []
        datafilt = []
        datafiltA0 = []
        datafiltA = []
        datafiltV = []
        datastalta = []
        nptstotal = 0
        rawrange = 0
        rawrms = 0
        rawmean = 0
        rawmin = 0
        rawmax = 0
        segmentshort = 1e6
        segmentlong = 0
        for j in range(0,len(stA)):
            tr = stA[j]
            nptstotal = nptstotal + tr.stats.npts
            if ( tr.stats.npts*dt > segmentlong ):
                segmentlong = tr.stats.npts*dt
            if ( tr.stats.npts*dt < segmentshort ):
                segmentshort = tr.stats.npts*dt 
            dataraw = np.concatenate((dataraw,st[j].data),axis=0)
            datafiltA0 = np.concatenate((datafiltA0,stA[j].data),axis=0)
            #----- generate a trigger function timeseries
            if ( (dt*tr.stats.npts)  > ltalen+stalen ):
                #---- this is ObsPy Z-detector = fast and good.  This uses a 1.0 sec window.
                stalta[j].data = z_detect(tr,int(1.0/dt))
                #---- slower traditional STA/LTA, simple, but less discriminating
#                stalta[j].data = classic_sta_lta(stalta[j].data,int(stalen/dt),int(ltalen/dt))
                datastalta = np.concatenate((datastalta,stalta[j].data),axis=0)
            else:
                stalta[j].data = st[j].data*0.
                datastalta = np.concatenate((datastalta,np.ones(tr.stats.npts)*0),axis=0)

#------- get power at different frequencies

            pow50sec = 0
            pow30sec = 0
            pow20sec = 0
            pow10sec = 0
            pow5sec = 0
            pow1Hz = 0
            pow5Hz = 0
            pow10Hz = 0
            pow20Hz = 0
            pow50Hz = 0
            pct1 = 0
            pct5 = 0
            pct10 = 0
            pct50 = 0
            pct90 = 0
            pct95 = 0
            pct99 = 0
            pctmed = 0
            if ( dt*tr.stats.npts > 3600.05 ):
                try:
                    #---- ObsPy PPSD will only work on >3600s data
                    ppsd = PPSD(st[j].stats, metadata=inventory)
                    ppsd.add(st)
                    psd_periods = ppsd._period_binning[2]
                    psd_power = []
                    psd_power = ppsd._binned_psds[0]
                    pow50sec = psd_power[np.argmin(abs(psd_periods-50.))]
                    pow30sec = psd_power[np.argmin(abs(psd_periods-30.))]
                    pow20sec = psd_power[np.argmin(abs(psd_periods-20.))]
                    pow10sec = psd_power[np.argmin(abs(psd_periods-10.))]
                    pow5sec = psd_power[np.argmin(abs(psd_periods-5.))]
                    pow1Hz = psd_power[np.argmin(abs(psd_periods-1.0))]
                    pow5Hz = psd_power[np.argmin(abs(psd_periods-0.2))]
                    pow10Hz = psd_power[np.argmin(abs(psd_periods-0.1))]
                    pow20Hz = psd_power[np.argmin(abs(psd_periods-0.05))]
                    pow50Hz = psd_power[np.argmin(abs(psd_periods-0.02))]
                    powstring = "%s %s %s %s %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g " % (net, stat, loc, chan, pow50sec, pow30sec, pow20sec, pow10sec, pow5sec, pow1Hz, pow5Hz, pow10Hz, pow20Hz, pow50Hz )
#                    f3.write(powstring + '\n')
                except:
                    iskipPSD = 1

        rawrange = float(np.ptp(dataraw))
        rawmean = np.mean(dataraw)
#        rawrms = np.sqrt(np.vdot(dataraw, dataraw)/dataraw.size)
        rawrms = np.sqrt(np.mean((dataraw-rawmean)**2))
        rawmin = min(dataraw)
        rawmax = max(dataraw)

#------ Count spikes in trigger function  exceeding a threshold amplitude. Triggers 
#------   counting uses filtered accel. trigger function (datastalta), amp 
#------   amplitude measuring uses broadly filtered accel data (datafiltA0).
#------   This uses a 10. sec min separation bw spikes (mpd) and minimum peak
#------   height of 5 (mph). 

        if ( len(datastalta) > int((stalen+ltalen)/dt) ):
            indexlocalmax = detect_peaks(datastalta,mpd=int(10./dt),mph=5.0) 
        peaksnr = np.zeros(len(indexlocalmax))
        peakamp = np.zeros(len(indexlocalmax))
        iwin = int((stalen+ltalen)/dt)
        i20win = int(20./dt)
        for j in range(0,len(indexlocalmax)):
            j1 = max(0,indexlocalmax[j]-iwin)
            j2 = min(indexlocalmax[j]+iwin,len(datafiltA0))
            jm1 = max(0,indexlocalmax[j]-i20win-iwin)
            jm2 = min(indexlocalmax[j]-iwin,len(datafiltA0))
            peaksnr[j] = max(datastalta[j1:j2])
            peakamp[j] = max(abs(datafiltA0[j1:j2]-np.mean(datafiltA0[jm1:jm2])))
        peakamp10 = peakamp[np.where(peaksnr>10)]
        peakamp20 = peakamp[np.where(peaksnr>20)]
        snr5_01cm = (abs(peakamp)>0.001).sum()
        snr5_05cm = (abs(peakamp)>0.005).sum()
        snr10_05cm = (abs(peakamp10)>0.005).sum()
        snr20_05cm = (abs(peakamp20)>0.005).sum()
        snr5_1cm = (abs(peakamp)>0.01).sum()
        snr10_1cm = (abs(peakamp10)>0.01).sum()
        snr20_1cm = (abs(peakamp20)>0.01).sum()
        snr5_2cm = (abs(peakamp)>0.02).sum()
        snr10_2cm = (abs(peakamp10)>0.02).sum()
        snr20_2cm = (abs(peakamp20)>0.02).sum()
        snr5_5cm = (abs(peakamp)>0.05).sum()
        snr10_5cm = (abs(peakamp10)>0.05).sum()
        snr20_5cm = (abs(peakamp20)>0.05).sum()

#------- Quick and dirty approximation of median envelope amplitude aka "noise floor"
#-------    uses data filtered with "filtermetrics" filter.  The metric uses the
#-------    half range of the 2nd to the 98th percentile amplitudes, empirically found
#-------    to be pretty good (and much faster) estimate of median envelope amplitude
#-------    on data filtered 1-5Hz, which was my original filter.

        stA.filter("bandpass",freqmin=filtermetrics[1],freqmax=filtermetrics[2])
        for j in range(0,len(stA)):
            datafiltA = np.concatenate((datafiltA,stA[j].data),axis=0)
            datafiltV = np.concatenate((datafiltV,stV[j].data),axis=0)
        datafiltAsort = np.sort(datafiltA)
        datafiltVsort = np.sort(datafiltV)
        data_A2 = datafiltAsort[int(len(datafiltAsort)*0.02)]
        data_A98 = datafiltAsort[int(len(datafiltAsort)*0.98)]
        dataArange = (data_A98 - data_A2)/2.
        data_V2 = datafiltVsort[int(len(datafiltVsort)*0.02)]
        data_V98 = datafiltVsort[int(len(datafiltVsort)*0.98)]
        dataVrange = (data_V98 - data_V2)/2.

#------  Glenn's RMS noise level metric to catch something like a loud temporary pump
#------    Specify the RMS window length with iRMSwinlen
#------    *** NOTE:  this is not written to the output in this version of the code ***

        pumpnoise = np.zeros(len(datafiltA0))
        RMS0p01cm = 0
        RMS0p035cm = 0
        RMS0p05cm = 0
        RMS0p1cm = 0
        RMS0p5cm = 0
        RMS1cm = 0
        ij = 0
        timeRMS1 = timeit.default_timer()
        for j in range(0,len(stA)):
            tr = stA[j]
            iRMSwinlen = int(5/tr.stats.delta)
            if ( tr.stats.npts > iRMSwinlen ):
                trsmooth = np.sqrt(smooth((tr.data**2),iRMSwinlen))
                for jj in range(0,len(trsmooth)):
                    pumpnoise[ij] = trsmooth[jj]
                    ij = ij + 1
        timeRMS2 = timeit.default_timer()
        RMS0p01cm = ((pumpnoise>0.0001).sum())*dt
        RMS0p035cm = ((pumpnoise>0.00035).sum())*dt
        RMS0p05cm = ((pumpnoise>0.0005).sum())*dt
        RMS0p1cm = ((pumpnoise>0.001).sum())*dt
        RMS0p5cm = ((pumpnoise>0.005).sum())*dt
        RMS1cm = ((pumpnoise>0.01).sum())*dt

#------ write out results

        ngaps = len(stA) - 1
        pctavailable = 100.*(nptstotal/(lenrequested/dt))

        numstring = "%d %d %d %d %d %d %d %d %d %d %d %d %d %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.4g %.6g %.6g %.4g %d" % ( snr5_01cm, snr5_05cm, snr10_05cm, snr20_05cm, snr5_1cm, snr10_1cm, snr20_1cm, snr5_2cm, snr10_2cm, snr20_2cm, snr5_5cm, snr10_5cm, snr20_5cm, pow50sec, pow30sec, pow20sec, pow10sec, pow5sec, pow1Hz, pow5Hz, pow10Hz, pow20Hz, pow50Hz, dataArange, dataVrange, rawrange, rawmean, rawrms, rawmin, rawmax, segmentshort, segmentlong, pctavailable, ngaps )

    f2.write( net + " " + stat + " " + loc + " " + chan + " " + numstring + '\n' )

#------ make a summary station figure (meh.... it's been a while, so I'm not sure if this part works)

    if ( iplot == 1 ):
        starttimeplot = timeit.default_timer()
        fig = plt.figure(figsize=(8,8),dpi=80)
        gs1 = gridspec.GridSpec(1,1)
        gs1.update(left=0.13,right=0.91,bottom=0.68,top=0.93,wspace=0.01)
        ax1 = plt.subplot(gs1[:,:])
        gs2 = gridspec.GridSpec(1,1)
        gs2.update(left=0.13,right=0.91,bottom=0.38,top=0.63,wspace=0.01)
        ax2 = plt.subplot(gs2[:,:])
        gs3 = gridspec.GridSpec(1,1)
        gs3.update(left=0.13,right=0.91,bottom=0.08,top=0.33,wspace=0.01)
        ax3 = plt.subplot(gs3[:,:])
        chantype = chan[1:2]
        if ( chantype == "N" ):
            units = "cm/s^2"
        else:
            units = "cm/s"
        for ii in range(0,len(stA)):
            timearray = np.arange(st[ii].stats.npts)*dt
            t = st[ii].stats.starttime
            x = np.array([datetime.datetime(t.year,t.month,t.day,t.hour,t.minute,t.second,t.microsecond) + datetime.timedelta(seconds=jj) for jj in timearray ])
            ax1.plot(x,st[ii].data,color='k')
            ax1.xaxis.set_major_formatter(DateFormatter('%H:%M'))
            ax2.plot(x,stA[ii].data*100.,color='k')
            ax2.xaxis.set_major_formatter(DateFormatter('%H:%M'))
            ax3.plot(x,stalta[ii],color='k')
            ax3.xaxis.set_major_formatter(DateFormatter('%H:%M'))
        t1 = datetime.datetime(T1.year,T1.month,T1.day,T1.hour,T1.minute,T1.second) - datetime.timedelta(seconds=10)
        t2 = datetime.datetime(T2.year,T2.month,T2.day,T2.hour,T2.minute,T2.second) + datetime.timedelta(seconds=10)
        timediffinsec = (t2-t1).total_seconds()
        ttextL = t1 - datetime.timedelta(seconds=timediffinsec*0.15)
        ttextR = t1 + datetime.timedelta(seconds=timediffinsec*1.02)
        ttitle = t1 + datetime.timedelta(seconds=timediffinsec*0.15)
        titletext = str(ttitle.year) + '/' + str(ttitle.month) + '/' + str(ttitle.day) + ' (UTC)         ' + net + '.' + stat + '.' + loc + '.' + chan + '   (raw, gain corr, STALTA)'
        ytitle = ax1.get_ylim()[0] + ( ax1.get_ylim()[1] - ax1.get_ylim()[0] )*1.04
        ax1.text(ttitle,ytitle,titletext)
        ax1.set_xlim([t1,t2])
        ax2.set_xlim([t1,t2])
        ax3.set_xlim([t1,t2])
        ax2.set_ylim([-5.2,5.2])
        ax3.set_ylim([-2,25])
        ytext1 = ax1.get_ylim()[0] + ( ax1.get_ylim()[1] - ax1.get_ylim()[0] )*0.55
        ytext2 = ax2.get_ylim()[0] + ( ax2.get_ylim()[1] - ax2.get_ylim()[0] )*0.55
        ytext3 = ax3.get_ylim()[0] + ( 30 )*0.55
        ax1.text(ttextL,ytext1,"counts",color='k',rotation=90)
        ax2.text(ttextL,ytext2,units,color='k',rotation=90)
        ax3.text(ttextL,ytext3,"STA/LTA",color='k',rotation=90)

        ax3.text(ttitle,-8,numstring,fontsize=8)

        locname = loc
        if ( loc == "--" ):
           locname = ""
        figname = 'WAVEFORMS.' + str(ttitle.year) + '.' + str(ttitle.month) + '.' + str(ttitle.day) + '.' + str(ttitle.hour) + '.' + net + '.' + stat + '.' + locname + '.' + chan + '.png'
        plt.savefig(figname)
        plt.close("all")
        endtimeplot = timeit.default_timer()
        timeplot = timeplot+(endtimeplot-starttimeplot)

    endtimeloop = timeit.default_timer()
    timeloop = timeloop+(endtimeloop-starttimeloop)

    print ( str(i) + '  ' + SNCL + "  Ttotal: " + str(timeloop) + "  Tloop: " + str(timeloop-timeclient-timeplot) + "  Tclient: " + str(timeclient) + '  Tplot: ' + str(timeplot) + '  len(index): ' + str(len(indexlocalmax)) + " " + numstring )

f2.close()
#f3.close()

endtime = timeit.default_timer()
now = datetime.datetime.utcnow()
print ("Current UTC time: " + str(now) + '   duration: ' + str((endtime-begintime)/60) + " min  Ttotal: " + str(timeloop) + "  Tloop: " + str(timeloop-timeclient-timeplot) + "  Tclient: " + str(timeclient) + '  Tplot: ' + str(timeplot)  )


