from __future__ import print_function
from datetime import datetime
import pytz
import math

def latency_gaps_completeness(filelist, starttime0, endtime0, penalty=30):
    """
        Reads output files from sniffwave_tally and produces eew_stationreport metrics 
        percent_latency_good, gaps_per_hour, percent_completeness, percent_completeness_w_penalty

        Args:
            filelist ([string]): list of filenames, output files from sniffwave_tally, 
                                 they have to be in time order:
                                 i.e. filelist[i] created earlier than filelist[i+1]
            starttime (datetime obj): start date + time of requested window
            endtime (datetime obj): end date + time of requested window
            penalty (float): number of seconds that get added per gap in completeness_w_penalty
                             calculation (default=30s)
        Returns:
            dict: key'd on net.sta.loc.chan, nested dictionary has keys:
                  measurement_start:		UTC starttime of the first packet in measurement window
                  measurement_end:		UTC endtime of the last packet in measurement window
                  measurement_gap:		number of seconds between sniffwave runs, where no data was collected
                  data_timewindow_length:	total number of seconds processed during measuring window
                  percent_latency_good:		percentage of packets that had a latency < 3.5s
                  gaps_per_hour:		3600 * (number of gaps/data_timewindow_length in s)
                  percent_completeness:         100*(data_timewindow_length - total gap duration)/data_timewindow_length
                  percent_completeness_w_penalty: 100*(data_timewindow_length - (total gap duration + ngaps*penalty))/data_timewindow_length
                   
    """
    sep = ","
    totaldict = {}
    if type(filelist) != list:
        filelist = [filelist]
    starttime0 = pytz.utc.localize(starttime0)   #--- starttime0 passed through is PST :-/
    startUtime = starttime0.timestamp()  #--- use Unix time, more direct comparison = faster
    endtime0 = pytz.utc.localize(endtime0)
    endUtime = endtime0.timestamp()
    endminusstart = endUtime - startUtime
    for filename in filelist:
        scnldict = {}
        with open(filename,"r") as input:
            for line in input:
                line = line.strip()
                if not len(line) == 0:
                    if line[0] == "#":
                        header_line = line
                        field_names = header_line.split(sep)
                    else:
                        fields = line.split(sep)
                        scnl = fields[0].strip()
#                        print ("FIELDS : " + str(fields) )
                        sniffstartUtime = float(fields[1])
                        sniffendUtime = float(fields[2])
                        if ( sniffstartUtime >= startUtime and sniffendUtime <= endUtime ):
                            if scnl not in totaldict:
                                #first time we see this channel
                                scnldict[scnl] = {}
                                totaldict[scnl] = {}
                                # populate the dict
                                i = 1
                                for name in field_names[1:]:
                                    scnldict[scnl][name] = fields[i].strip('\n')
                                    i += 1
                                totaldict[scnl]['nmeasurements'] = 1
                                totaldict[scnl]['no_data'] = 0.
                                totaldict[scnl]['first'] = float(scnldict[scnl]['starttime'])
                                # in case there's only one measurement period for this channe also set lastl
                                totaldict[scnl]['last'] = float(scnldict[scnl]['endtime'])
                                totaldict[scnl]['prev_starttime'] = float(scnldict[scnl]['starttime'])
                                totaldict[scnl]['prev_endtime'] = float(scnldict[scnl]['endtime'])
                                totaldict[scnl]['total_duration'] = float(scnldict[scnl]['duration'])
                                totaldict[scnl]['total_packets'] = int(scnldict[scnl]['npackets'])
                                totaldict[scnl]['total_late'] = int(scnldict[scnl]['nlate'])
                                totaldict[scnl]['total_gaps'] = int(scnldict[scnl]['ngap'])
                                totaldict[scnl]['total_gap_dur'] = float(scnldict[scnl]['gap_dur'])
                                totaldict[scnl]['total_overlaps'] = int(scnldict[scnl]['noverlap'])
                                totaldict[scnl]['total_overlap_dur'] = float(scnldict[scnl]['overlap_dur'])
                                totaldict[scnl]['total_oo'] = int(scnldict[scnl]['n_oo'])
                                totaldict[scnl]['total_oo_dur'] = float(scnldict[scnl]['oo_dur'])
                            else:
                                if scnl not in scnldict:
                                    # if the scnl in totaldict but not in scnldict, it means the channel was available
                                    # for an earlier sniffwave run, but not this one.
                                    scnldict[scnl] = {}
                                i = 1
                                for name in field_names[1:]:
                                    scnldict[scnl][name] = fields[i].strip("\n")
                                    i += 1
                                totaldict[scnl]['nmeasurements'] += 1
                                totaldict[scnl]['no_data'] += float(scnldict[scnl]['starttime'])-float(totaldict[scnl]['prev_endtime'])
                                totaldict[scnl]['last'] = float(scnldict[scnl]['endtime'])
                                totaldict[scnl]['total_duration'] += float(scnldict[scnl]['duration'])
                                totaldict[scnl]['total_packets'] += int(scnldict[scnl]['npackets'])
                                totaldict[scnl]['total_late'] += int(scnldict[scnl]['nlate'])
                                totaldict[scnl]['total_gaps'] += int(scnldict[scnl]['ngap'])
                                totaldict[scnl]['total_gap_dur'] += float(scnldict[scnl]['gap_dur'])
                                totaldict[scnl]['total_overlaps'] += int(scnldict[scnl]['noverlap'])
                                totaldict[scnl]['total_overlap_dur'] += float(scnldict[scnl]['overlap_dur'])
                                totaldict[scnl]['total_oo'] += int(scnldict[scnl]['n_oo'])
                                totaldict[scnl]['total_oo_dur'] += float(scnldict[scnl]['oo_dur'])
                                totaldict[scnl]['prev_starttime'] = float(scnldict[scnl]['starttime'])
                                totaldict[scnl]['prev_endtime'] = float(scnldict[scnl]['endtime'])
 


    # calculate metrics
    metrics = {}
    for scnl in totaldict:
        # re-order channel identifiers to be consistent with eew_stationreport (IRIS DMC)
        [s,c,n,l] = scnl.split(".")
        nslc = ".".join([n,s,l,c])
        if nslc not in metrics:
            metrics[nslc] = {}
        d = totaldict[scnl]
        latency_metric = 100 * (d['total_packets']-d['total_late'])/d['total_packets'] # % data good latency
        gap_metric = 3600.0 * d['total_gaps']/d['total_duration'] # gaps/hour
#        completeness = 100 * (endminusstart - d['total_gap_dur'])/endminusstart # % data available
#        completeness_incl_penalty = 100 * (endminusstart - (d['total_gap_dur'] + d['total_gaps']*penalty))/endminusstart # % data available
        completeness = 100 * (d['total_duration'] - d['total_gap_dur'])/d['total_duration'] # % data available
        completeness_incl_penalty = 100 * (d['total_duration'] - (d['total_gap_dur'] + d['total_gaps']*penalty))/d['total_duration'] # % data available
        metrics[nslc]["measurement_start"] = datetime.fromtimestamp(d["first"])
        metrics[nslc]["measurement_end"] = datetime.fromtimestamp(d["last"])
        metrics[nslc]["measurement_gap"] = d["no_data"]
#        metrics[nslc]["data_timewindow_length"] = d["total_duration"]
        metrics[nslc]["data_timewindow_length"] = math.floor(d["total_duration"])  #--- truncate the microseconds
        metrics[nslc]["percent_latency_good"] = latency_metric
        metrics[nslc]["gaps_per_hour"] = gap_metric
        metrics[nslc]["percent_completeness"] = completeness
        metrics[nslc]["percent_completeness_w_penalty"] = completeness_incl_penalty
        metrics[nslc]["total_duration_of_gaps_incl_penalty"] = d['total_gap_dur'] + d['total_gaps']*penalty

    return metrics

if __name__ == "__main__":
    import glob
    # input files are the output from sniffwave_tally
    inputdir = "../test-data/" # read input files from this directory
    filelist = glob.glob(inputdir + "*.csv")
    filelist = sorted(filelist)
    # move to processed directory after done.
    savedir = "processed/"
    metrics = latency_gaps_completeness(filelist)
    for scnl in metrics:
        print(scnl, metrics[scnl])
