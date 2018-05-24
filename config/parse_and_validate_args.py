#!/usr/bin/env python

import argparse
import sys
from uuid import uuid4
import datetime

def parse_args():
    """
    Parse input arguments and make an extended help menu.
    If Loc = "--", change it to a token string and then back to a string.
    """
    sentinel_dict = {}

    def _preprocess_sysargv(argv):
        inputs = []
        for arg in argv[1:]:
            # handles case where values contain --, otherwise they will
            # be interpreted as arguments.
            if '--,' in arg or ',--' in arg or arg == '--':
                sentinel = uuid4().hex
                key = '%s' % sentinel
                sentinel_dict[key] = arg
                inputs.append(sentinel)
            else:
                inputs.append(arg)
        return inputs

    def _postprocess_sysargv(v):
        if v in sentinel_dict:
            return sentinel_dict.get(v)
        else:
            return v

    #----- read input arguments
    for i, arg in enumerate(sys.argv):
       if (arg[0] == '-') and arg[1].isdigit(): sys.argv[i] = ' ' + arg
    parser = argparse.ArgumentParser()

    parser.add_argument('-u', action='store_true', dest='helpmenu',help='extended HELP MENU with examples')
    parser.add_argument('-i','--infile',action='store', dest='infile',help='name of file where lines are: NET STAT LOC CHAN')
    parser.add_argument('-N','--net', action='store', dest='network',help='network')
    parser.add_argument('-S','--sta', action='store', dest='station',help='station')
    #parser.add_argument('-C','--cha', action='store', dest='channel',help='channel')
    #parser.add_argument('-L','--loc', action='store', dest='location',help='location',  type=_postprocess_sysargv)
    parser.add_argument('-s','--start', action='store', dest='startstring',help='start time YYYY-MM-DDTHH:MM:SS')
    parser.add_argument('-e','--end', action='store', dest='endstring',help='end time YYYY-MM-DDTHH:MM:SS')
    parser.add_argument('-d','--duration', action='store', dest='durationinhours',help='duration in hours')
    parser.add_argument('-dc','--dc','--datacenter', action='store', dest='datacenter',help='FDSN data center (e.g. IRIS, SCEDC, NCEDC)')
    parser.add_argument('-p','--plot',action='store_true',dest='iplot',help='make plots of each hourly trace (NOTE: can be slow)')

    helpextended = parser.parse_args(_preprocess_sysargv(sys.argv)).helpmenu
    if ( helpextended is True  ):
        print ('')
        print ('calculate_metrics_for_acceptance: calculate those metrics able to be measured')
        print ('with archived data (i.e. no latency info)')
        print ('')
        print ('Usage: calculate_metrics_for_acceptance.py [options]')
        print ('')
        print ('EXAMPLES:')
        print ('calculate_metrics_for_acceptance.py --infile My_NSLC_List.txt --start 2018-01-01T00:00:00 --end 2018-01-14T00:00:00 --datacenter IRIS')
        print ('calculate_metrics_for_acceptance.py -i My_NSLC_List.txt -s 2018-01-01T00:00:00 -e 2018-01-14T00:00:00 --dc SCEDC')
        print ('calculate_metrics_for_acceptance.py -i My_NSLC_List.txt -s 2018-01-01T00:00:00 --duration 24 -dc NCEDC')
        print ('calculate_metrics_for_acceptance.py -N UW -S WISH -L -- -C BHZ -s 2018-01-01T00:00:00 -d 336 -dc IRIS -p')
        print ('')
        print ('Mandatory inputs:')
        print ('-dc, --datacenter     Name of FDSN data center, e.g. IRIS, SCEDC, NCEDC')
        print ('-s,  --starttime      Trace start time (YYYY-MM-DD,HH:MM:SS)')
        print ('')
        print ('One of these:')
        print ('  -e,  --endtime      Trace end time (YYYY-MM-DD,HH:MM:SS)')
        print ('  -d,  --duration     Duration in hours from starttime')
        print ('                      Note: if duration is neg, starttime becomes endtime')
        print (' ')
        print ('One of these:')
        print ('  -I,  --infile       Name of file whose lines are: Net Sta Loc Cha')
        print ('or:')
        print ('  -N,  --net          Network code')
        print ('  -S,  --sta          Station code')
        print ('  -L,  --loc          Location code (use -- for null)')
        print ('  -C,  --cha          Channel code')
        print (' ')
        print ('Optional flags:')
        print ('-P,  --plot           Flag to make a figure for each hour.  Note: can be slow.')
        print ('-u                    Print this extended help menu')
        print ('')


    return parser.parse_args(_preprocess_sysargv(sys.argv))


def validate_args_and_get_times(args):
    """
    Validate arguments and pass back start/end times and durations.
    """
    infile = args.infile
    network = args.network
    station = args.station
    #channel = args.channel
    #location = args.location
    startstring = args.startstring
    endstring = args.endstring
    durationinhours = args.durationinhours
    datacenter = args.datacenter

    #----- validate start/end time
    if ( startstring is None and ( endstring is not None or durationinhours is not None ) ):
        print ("Error: need a starttime and [endtime or duraiton]")
        exit()
    else:
        try:
            starttime = datetime.datetime.strptime(startstring, "%Y-%m-%dT%H:%M:%S")
        except:
            print ("Error: invalid starttime.  Use format: 2018-01-31T23:59:01  or  2018-1-31T23:59:1")
            exit()
        if ( durationinhours is not None ):
            try:
                if ( float(durationinhours) > 0 ):
                    durationinhours = float(durationinhours) 
                    durationinsec = durationinhours * 3600.
                    endtime = starttime + datetime.timedelta(seconds=durationinsec)
                else:
                    durationinhours = abs(float(durationinhours))
                    durationinsec = durationinhours * 3600.
                    endtime = starttime
                    starttime = endtime - datetime.timedelta(seconds=durationinsec)
            except:
                print ("Error: invalid durationinhours; requires integer")
                exit()
        else:
            try:
                endtime = datetime.datetime.strptime(endstring, "%Y-%m-%dT%H:%M:%S")
                durationinsec = (endtime - starttime).total_seconds()
                durationinhours = durationinsec / 3600.
            except:
                print ("Error: invalid endtime.  Use format: 2018-01-31T23:59:01  or  2018-1-31T23:59:1")
                exit()

    #----- make sure there is either an entire SNCL or an input file of SNCLs
    if ( ( network is None or station is None ) and infile is None ):
        print ("Error:  need either network + station  OR a file with SNCLs")
        exit()

#    #----- validate channel input
#    instsampling_list = ['H','B','S','E','L']
#    insttype_list = ['N','H','X','C']
#    component_list = ['0','1','2','3','Z','N','E','R','T','Q']
#    if ( channel is not None ):
#        if ( len(channel) != 3 ):
#           print ("Error: invalid channel " + channel )
#           exit()
#        else:
#            if ( channel[0] not in instsampling_list or channel[1] not in insttype_list or channel[2] not in component_list ):
#                print ("Error: invalid channel " + channel )
#
    #----- read and do minimal validation of the infile if there is one
    if ( infile is not None ):
        f = open(infile,'r')
        instsampling_list = ['H','B','S','E','L']
        insttype_list = ['N','H','X']
        component_list = ['0','1','2','3','Z','N','E','R','T']
        for line in f:
            fields = line.split()
            if ( len(fields) != 4 ):
                print ("Error: infile needs to have 4 fields:  network station location")
                exit()
            else:
                network = fields[0]
                station = fields[1]
                location = fields[2]
                channel = fields[3]
                if ( len(network) < 1 or len(network) > 2 or len(station) < 1 or len(station) > 5 or len(location) < 1 or len(location) > 2 or channel[0] not in instsampling_list or channel[1] not in insttype_list or channel[2] not in component_list ):
                    print ("Error: infile needs to have 4 valid fields: network station location channel. You have: " + line )
                    exit()

    #----- validate the FDSN data center against a list
    if (datacenter is not None):
        if (datacenter not in [ "IRIS", "NCEDC", "SCEDC", "BGR", "EMSC", "ETH", "GEONET", "GFZ", "ICGC", "INGV", "IPGP", "ISC", "KOERI", "LMU", "NIEP", "NOA", "ODC", "ORFEUS", "RESIF", "TEXNET", "USGS", "USP" ]):
            print ("Error: need a valid FDSN data center")
            exit()

    return [starttime, endtime, durationinhours, durationinsec]


