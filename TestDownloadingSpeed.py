#!/usr/bin/env python

#
# This is a simple script to test download speeds.
#

import datetime
from obspy import UTCDateTime
import timeit
from obspy.clients.fdsn import Client

###########  Here are the parameters to play around with ######
datacenter = "SCEDC"   #  IRIS, NCEDC, SCEDC
chanfile = "ShakeAlertList.SCEDCZ"
duration = 3726
starttime = datetime.datetime(2018,1,8,9,57,54)
bulk = 1     #  0 = serial downloading, 1 = bulkdownloading
##########

client = Client(datacenter)
endtime = starttime + datetime.timedelta(0,duration)

f1 = open(chanfile)
lines = f1.readlines()
f1.close()
T1 = UTCDateTime(starttime)
T2 = UTCDateTime(starttime + datetime.timedelta(0,duration))

if ( bulk == 0 ):
    for i in range(0,len(lines)):
        bulkrequest = []
        net = lines[i].split()[0]
        stat = lines[i].split()[1]
        loc = lines[i].split()[2]
        chan = lines[i].split()[3]
        requestline = (net,stat,loc,chan,T1,T2)
        bulkrequest.append(requestline)
        try:
            Timer0 = timeit.default_timer()
            st = client.get_waveforms_bulk(bulkrequest)
            Timer2 = timeit.default_timer()
            nptstot = 0
            for i in range(0,len(st)):
                nptstot = nptstot + st[i].stats.npts
            print "TIME one-channel download: " +  str(Timer2-Timer0) + " sec  Nstreams: " + str(len(st)) + "  Approx size: " + str(nptstot/1024) + " KB   " + st[0].stats.network + "." + st[0].stats.station + "." + st[0].stats.channel
        except:
            print "did not work: " + str(requestline)

if ( bulk == 1 ):
    bulkrequest = []
    for i in range(0,len(lines)):
        net = lines[i].split()[0]
        stat = lines[i].split()[1]
        loc = lines[i].split()[2]
        chan = lines[i].split()[3]
        requestline = (net,stat,loc,chan,T1,T2)
        bulkrequest.append(requestline)
#        print "REQ " + str(i) + " " + str(requestline)
    try:
        print str(requestline)
        Timer0 = timeit.default_timer()
        st = client.get_waveforms_bulk(bulkrequest)
        Timer2 = timeit.default_timer()
        nptstot = 0
        for i in range(0,len(st)):
           nptstot = nptstot + st[i].stats.npts
           print "TIME bulk download: " +  str(Timer2-Timer0) + " sec  Nstreams: " + str(len(st)) + "  Approx size: " + str(nptstot/1048576) + " MB   " + st[i].stats.network + "." + st[i].stats.station + "." + st[i].stats.channel
    except:
        print "Bulk request did not work"

