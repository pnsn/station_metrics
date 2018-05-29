#!/usr/bin/env python
from __future__ import print_function
from datetime import datetime

def latency_gaps_completeness(filelist, penalty=30):
    """
        to do: docstring
    """
    sep = ","
    scnldict = {}
    totaldict = {}
    if type(filelist) != list:
        filelist = [filelist]

    for filename in filelist:
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
                        if scnl not in totaldict:
                            #first time we see this channel
                            scnldict[scnl] = {}
                            totaldict[scnl] = {}
                            # populate the dict
                            i = 1
                            for name in field_names[1:]:
                                scnldict[scnl][name] = fields[i].strip('\n')
                                #print(i,scnl,name,scnldict[scnl][name])
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
            completeness = 100 * (d['total_duration'] - d['total_gap_dur'])/d['total_duration'] # % data available
            completeness_incl_penalty = 100 * (d['total_duration'] - (d['total_gap_dur'] + d['total_gaps']*penalty))/d['total_duration'] # % data available
            metrics[nslc]["measurement_start"] = datetime.fromtimestamp(d["first"]).strftime('%Y-%m-%dT%H:%M:%S.%f')
            metrics[nslc]["measurement_end"] = datetime.fromtimestamp(d["last"]).strftime('%Y-%m-%dT%H:%M:%S.%f')
            metrics[nslc]["measurement_gap"] = d["no_data"]
            metrics[nslc]["data_timewindow_length"] = d["total_duration"]
            metrics[nslc]["percent_latency_good"] = latency_metric
            metrics[nslc]["gaps_per_hour"] = gap_metric
            metrics[nslc]["percent_completeness"] = completeness
            metrics[nslc]["percent_completeness_w_penalty"] = completeness_incl_penalty

        return metrics

if __name__ == "__main__":
    import glob
    # input files are the output from sniffwave_tally
    inputdir = "../test-data/" # read input files from this directory
    filelist = glob.glob(inputdir + "*.csv")
    # move to processed directory after done.
    savedir = "processed/"
    metrics = latency_gaps_completeness(filelist)
    for scnl in metrics:
        print(scnl, metrics[scnl])
