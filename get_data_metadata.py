#!/usr/bin/env python

import datetime
from obspy import UTCDateTime
import timeit

def download_waveforms_fdsn_bulk(chanfile,starttime,duration,client):
    """
    Uses ObsPy get_waveforms_bulk to download from an FDSN WS.
    The FDSN client passed through needs to already be open.
    Request will start at yr/mo/dyThr:mi:sc and be (duration) sec long.
    starttime is a datetime object
    Chanfile should look like:
    AZ BZN -- HHZ
    AZ CPE -- HHZ
    AZ CRY -- HHZ
    """
    # Build the bulkrequest
    f1 = open(chanfile)
    lines = f1.readlines()
    f1.close()
    T1 = UTCDateTime(starttime)
    T2 = UTCDateTime(starttime + datetime.timedelta(0,duration))
    bulkrequest = []
    for i in range(0,len(lines)):
        net = lines[i].split()[0]
        stat = lines[i].split()[1]
        loc = lines[i].split()[2]
        chan = lines[i].split()[3]
        requestline = (net,stat,loc,chan,T1,T2)
        bulkrequest.append(requestline)
#        print "REQ " + str(i) + " " + str(requestline)
#        print str(requestline)
    try:
        Timer0 = timeit.default_timer()
        st = client.get_waveforms_bulk(bulkrequest)
        Timer2 = timeit.default_timer()
        nptstot = 0
        for i in range(0,len(st)):
           nptstot = nptstot + st[i].stats.npts
        print "TIME bulk download: " +  str(Timer2-Timer0) + " sec  Nstreams: " + str(len(st)) + "  Approx size: " + str(nptstot/1048576) + " MB" 
    except:
        Timer2 = timeit.default_timer()
        print  "Failed download request or no data for: " + chanfile + " " + str(T1) + " to " + str(T2) + "  request took: " + str(Timer2-Timer0) + " sec"
        print bulkrequest
        st = []
    return st


def download_metadata_fdsn(net,stat,loc,chan,starttime,client):
    try:
        T1 = UTCDateTime(starttime)
        T2 = UTCDateTime(starttime + datetime.timedelta(0,1))
        inventory = client.get_stations(network=net,station=stat,location=loc,channel=chan,starttime=T1,endtime=T2, level='response')
    except:
        print "Inventory not available for: " + net + "." + stat + "." + loc +"." + chan + str(starttime) + " to " + str(endtime)
        inventory = []
    return inventory


def raw_trace_to_ground_motion_filtered_pruned(TraceOrig,T1,T2,AccVelDisp,FullResponse,f1,f2,f3,f4,inv):

#  Input is an ObsPy trace that will get demeaned, converted to ACC/VEL/DISP, and then filtered.
#  FullResponse = 0: only apply gain correction.  
#  FullResponse = 1: remove the full response.  Warning: this is slow, about 5sec/hour long trace.

    if ( "cc" in AccVelDisp or "CC" in AccVelDisp ):
        GM = "ACC"
    elif ( "V" in AccVelDisp or "v" in AccVelDisp ):
        GM = "VEL"
    else:
        GM = "DISP"
    trace = TraceOrig.copy()
    trace.detrend(type='demean')
    if ( len(inv) == 0 ):
        print "No metadata"
    else:
        #----- correct for gain factor only
        if ( FullResponse == 0 ):
            trace.remove_sensitivity(inv)
            trace.filter("bandpass", freqmin = f2, freqmax = f3)
            trace = trace.slice(UTCDateTime(T1),UTCDateTime(T2))
#            trace.detrend(type='polynomial',order=3)  #--- of order 0.08 sec/trace
#            trace.detrend(type='linear')              #--- of order 0.027 sec/trace
#            trace.detrend(type='demean')              #--- of order 0.002 sec/trace
            if ( trace.stats.channel[1:2] == "N" ):
                GMnative = "ACC"
            else:
                GMnative = "VEL"
            if ( GMnative == GM ):
                idonothing = 1
            elif ( GMnative == "ACC" and GM == "VEL" and trace.stats.npts > 2 ):
                trace.integrate(method='cumtrapz')
            elif ( GMnative == "ACC" and GM == "DISP" ):
                trace.integrate(method='cumtrapz')
                trace.integrate(method='cumtrapz')
            elif ( GMnative == "VEL" and GM == "ACC" and trace.stats.npts > 2 ):
                trace.differentiate(method='gradient')
        #----- remove the full response
        elif ( FullResponse == 1 ):
            trace.remove_response(inventory=inv, output=GM, pre_filt=(f1,f2,f3,f4))
            trace = trace.slice(UTCDateTime(T1),UTCDateTime(T2))

#        trace.detrend(type='polynomial',order=3)
        trace.detrend(type='demean')              #--- of order 0.002 sec/trace

    return trace


