#!/usr/bin/env python

import datetime
from obspy import UTCDateTime
import timeit

def download_waveform_single_trace(net,stat,loc,chan,starttime,duration,client):
    """
    Uses ObsPy get_waveforms to download from an FDSN WS.
    The FDSN client passed through needs to already be open.
    Request will start at yr/mo/dyThr:mi:sc and be (duration) sec long.
    starttime is a datetime object
    """
    T1 = UTCDateTime(starttime)
    T2 = UTCDateTime(starttime + datetime.timedelta(0,duration))
    try:
        st = client.get_waveforms(net,stat,loc,chan,UTCDateTime(T1),UTCDateTime(T2))
    except:
        st = []
        print ("Failed download request or no data for: " + net + "." + stat + "." + loc + "." + chan + " " + str(T1) + " to " + str(T2) )
    return st


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
    snclrequested = []
    snclreturned = []
    for i in range(0,len(lines)):
        net = lines[i].split()[0]
        stat = lines[i].split()[1]
        loc = lines[i].split()[2]
        chan = lines[i].split()[3]
        snclrequested.append(net + "." + stat + "." + loc + "." + chan)
        requestline = (net,stat,loc,chan,T1,T2)
        bulkrequest.append(requestline)
#        print ( "REQ " + str(i) + " " + str(requestline) )
#        print (str(requestline))
    try:
        Timer0 = timeit.default_timer()
        st = client.get_waveforms_bulk(bulkrequest)
        Timer2 = timeit.default_timer()
        nptstot = 0
        #---- in case you want to be informed of a requested seismogram not returned
        for i in range(0,len(st)):
           nptstot = nptstot + st[i].stats.npts
           loctemp = st[i].stats.location
           if ( st[i].stats.location == "" ):
               loctemp = "--"
           sncltemp = str(st[i].stats.network) + "." + str(st[i].stats.station) + "." + str(loctemp) + "." + str(st[i].stats.channel)
           snclreturned.append(sncltemp)
        for i in range(0,len(lines)):
            ireturned = 0
            for j in range(0,len(st)):
                if ( snclrequested[i] == snclreturned[j] ):
                    ireturned = 1
            if ( ireturned == 0 ):
                print (snclrequested[i] + " No_data_returned" )
         #---- in case you want to know the time/size of returned bulk data request
#        print ("TIME bulk download: " +  str(Timer2-Timer0) + " sec  Nstreams: " + str(len(st)) + "  Approx size: " + str(nptstot/1048576) + " MB" )
    except:
        Timer2 = timeit.default_timer()
        print ( "Failed download request or no data for: " + chanfile + " " + str(T1) + " to " + str(T2) + "  request took: " + str(Timer2-Timer0) + " sec" )
        print ( bulkrequest )
        st = []
    return st


def download_metadata_fdsn(net,stat,loc,chan,starttime,client):
    try:
        T1 = UTCDateTime(starttime)
        T2 = UTCDateTime(starttime + datetime.timedelta(0,1))
        inventory = client.get_stations(network=net,station=stat,location=loc,channel=chan,starttime=T1,endtime=T2, level='response')
    except:
        print ( "Inventory not available for: " + net + "." + stat + "." + loc +"." + chan + str(starttime) + " to " + str(endtime) )
        inventory = []
    return inventory
