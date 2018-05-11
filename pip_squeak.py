#!/usr/bin/env python

# Calculate some station metrics - noise floor, power at different frequencies, Nspikes...

# import std packages
from collections import Counter
import datetime
import timeit

# import third party packages
import numpy as np
from obspy.clients.fdsn import Client
from obspy import UTCDateTime
from obspy.signal.trigger import classic_sta_lta
from obspy import Stream
try:
    from ConfigParser import SafeConfigParser
except:
    from configparser import SafeConfigParser

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

# import station_metrics packages
from station_metrics.io.get_data_metadata import download_fdsn_bulk
from station_metrics.io.get_data_metadata import download_metadata_fdsn

from station_metrics.metrics.preprocessing import raw_trace_to_ground_motion_filtered_pruned
from station_metrics.metrics.noise_metrics import noise_floor, count_peaks_stalta
from station_metrics.metrics.noise_metrics import duration_exceed_RMS

from station_metrics.plotting.plot_pip_squeak import make_station_figure_pip_squeak

from config.parse_and_validate_args import validate_args_and_get_times, parse_args

# define which channel codes denote acceptable seismic channels
SEISMIC_CHANNELS = ['BHE', 'BHN', 'BHZ', 'HHE', 'HHN', 'HHZ',
                    'BH1', 'BH2', 'BH3', 'HH1', 'HH2', 'HH3',
                    'ENE', 'ENN', 'ENZ', 'HNE', 'HNN', 'HNZ',
                    'EN1', 'EN2', 'EN3', 'HN1', 'HN2', 'HN3']
# define a few SOH channels we might be interested in
SOH_CHANNELS = ['LCQ', 'LCE']

if __name__ == "__main__":
    """
        Generates Phase1 Station Acceptance Report.
        Requirements:
            config/pipsqueak.cfg --> configuring the metrics
            command-line arguments --> specify station and time period
    """
    # prepare report engine (jinja2)
    env = Environment(
        loader=FileSystemLoader("./templates"),
        autoescape=select_autoescape(['html', 'htm', 'xml'])
    )
    template = env.get_template('phase1.htm')
        
    #----- Read Processing parameters from a config file
    
    parser = SafeConfigParser()
    parser.read("pip_squeak.cfg")
    
    FDSNtimeout = float(parser.get('SectionOne','FDSNtimeout'))
    tpadding = float(parser.get('SectionOne','tpadding'))
    sta = float(parser.get('SectionOne','sta'))
    lta = float(parser.get('SectionOne','lta'))
    tbuffer = sta + lta
    freqBP1 = float(parser.get('SectionOne','freqBP1'))
    freqBP2 = float(parser.get('SectionOne','freqBP2'))
    freqBP3 = float(parser.get('SectionOne','freqBP3'))
    freqBP4 = float(parser.get('SectionOne','freqBP4'))
    freqBB1 = float(parser.get('SectionOne','freqBB1'))
    freqBB2 = float(parser.get('SectionOne','freqBB2'))
    mpd = float(parser.get('SectionOne','mpd'))
    RMSlen = float(parser.get('SectionOne','RMSlen'))
    GainOrFullResp = parser.get('SectionOne','GainOrFullResp')
    #PSDperiods = (parser.get('SectionOne','PSDperiods'))[1:-1].split(",")
    #PSDperiods = [float(i) for i in PSDperiods]
    #iplot = parser.get('SectionOne','iplot')
    
    #----- command-line arguments specify what data to get and where
    # options that influence program structure:
    # infile: 
    #     multiple channels, possibly from multiple stations, are defined in an input file. 
    # command-line arguments -N network, -S station:
    #     pip_squeak is run for the channels of a single station only.
    
    args = parse_args()
    [starttime, endtime, durationinhours, durationinsec] = validate_args_and_get_times(args)

    # get data from a little before starttime to remedy edge effects
    request_starttime = starttime - datetime.timedelta(0,tbuffer+tpadding)
    duration_padded = durationinsec+tbuffer+(2*tpadding)
    request_endtime = request_starttime + datetime.timedelta(seconds=duration_padded)
    
    slice_starttime = starttime - datetime.timedelta(seconds=tbuffer)
    slice_endtime = starttime + datetime.timedelta(seconds=(durationinsec + tbuffer))

    infile = args.infile
    if infile:
        network = None
        station = None
    else: 
        network = args.network
        station = args.station
    #channel = args.channel
    #location = args.location
    datacenter = args.datacenter
    iplot = args.iplot
    
    #----- Set up the FDSN client
    
    Tdc0 = timeit.default_timer()
    try:
        client = Client(datacenter,timeout = FDSNtimeout)
    except Exception as error:
        print ("Error: {}, Failed to connect to FDSN client. Used a timeout of {}".format(error, FDSNtimeout))
    Tdc1 = timeit.default_timer()
    print ("Time to connect to FDSNWS: " + str(Tdc1-Tdc0) )
    
    #----- Download meta-data
    timer_start = timeit.default_timer()
    if infile:
        inv = download_fdsn_bulk(infile,request_starttime,duration_padded,client,type="metadata")
    else:
        inv = download_metadata_fdsn(client,net=network,sta=station,starttime=request_starttime)
    timer_end = timeit.default_timer()
    inv.write("inventory.xml","STATIONXML")
    print ("Time to download metadata from {}: {}".format(datacenter, str(timer_end - timer_start)))

    # Create one report per station in the Inventory file.
    for net_obj in inv:
        for sta_obj in net_obj:

            print("Creating report for time period {} - {}, station: {}.{}".format(starttime,endtime,net_obj.code,sta_obj.code))
    
            # Download waveform for this station 
    
            # construct the bulkrequest list of tuples
            # single network, single station, loop over channels
            bulkrequest = []
            soh_bulkrequest = []
            for chan in sta_obj:
                channel = chan.code
                location = chan.location_code
                if location == "":
                    location = "--"
                if channel in SEISMIC_CHANNELS:
                    bulkrequest.append( \
                        (network, station, location, channel, request_starttime.isoformat(), \
                        request_endtime.isoformat()) \
                        )
                if channel in SOH_CHANNELS:
                    soh_bulkrequest.append( \
                        (network, station, location, channel, request_starttime.isoformat(), \
                        request_endtime.isoformat()) \
                        )

            timer_start = timeit.default_timer()
            stAll = client.get_waveforms_bulk(bulkrequest)
            timer_end = timeit.default_timer()
            stAll.write("waveforms.msd","MSEED")
            print ("Time to download waveforms from {}: {}".format(datacenter, str(timer_end - timer_start)))

            # Now request the SOH channels.
            timer_start = timeit.default_timer()
            stSOH = client.get_waveforms_bulk(soh_bulkrequest)
            timer_end = timeit.default_timer()
            stSOH.write("soh.msd","MSEED")
            print ("Time to download SOH time series from {}: {}".format(datacenter, str(timer_end - timer_start)))
            
            # LCQ channel has distinct values between 0-100, e.g. 20, 60, 100
            lcq = stSOH.select(channel="LCQ")
            # anticipate possible gaps in these data but do not keep track
            lcq_below_60 = 0
            number_of_points = 0
            for trace in lcq:
                value_counts = Counter(trace.data)
                number_of_points = number_of_points + len(trace.data)
                for value, count in value_counts.iteritems():
                    if value < 60:
                        lcq_below_60 = lcq_below_60 + count
            print("Number of LCQ samples below 60: {} out of {}, i.e. {:4.1f}%".format(lcq_below_60, \
                   number_of_points,100*(lcq_below_60/number_of_points)))

            #TO DO: add same for lce channel, but cutoff is abs(lce) < 5000 microseconds

            #----- Get the time slices to analyze.
            
            lenrequested = (slice_endtime - slice_starttime).total_seconds()
            
            #----- Loop over seismograms.  If a station has gaps, a stream of that sncl will 
            #----- be made from all the traces.
            
            # This assumes the data are in the stream ordered by net,sta,loc,chan,starttime, 
            # which is OK for the DMC (per Chad) but is NOT guaranteed by the FDSN dataselect 
            # web service standard. 
            channel_metrics = {}
            itrace = 0
            Tsum = 0
            for i in range(0,len(stAll)):
                ntr = 1
                iduplicate = 0
                if ( stAll[i].stats.location == "" ):
                    sncl = stAll[i].stats.network + "." + stAll[i].stats.station + ".--." + stAll[i].stats.channel
                else:
                    sncl = stAll[i].stats.network + "." + stAll[i].stats.station + "." + stAll[i].stats.location + "." + stAll[i].stats.channel
            #    print ( str(i) + " SNCL " + sncl )
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
                    T2 = timeit.default_timer()
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
                    dt = stAll[i].stats.delta
                    freqBB3 = 0.9 * (1/(2*dt))
                    freqBB4 = 0.99 * (1/(2*dt))
                    segmentlong = 0
                    segmentshort = 9e6
                    for j in range(i,i+ntr):
                        trRaw = stAll[j].copy()
                        trRaw = trRaw.slice(UTCDateTime(slice_starttime),UTCDateTime(slice_endtime))
                        npts = trRaw.stats.npts
                        nptstotal = nptstotal + npts
                        trPadded = stAll[j].copy()
                        trPadded = trPadded.detrend(type='polynomial',order=3)
                        if ( dt*npts > segmentlong ):
                            segmentlong = dt*npts
                        if ( dt*npts < segmentshort ):
                            segmentshort = dt*npts
                        trAccBroad = raw_trace_to_ground_motion_filtered_pruned(trPadded, \
                                     slice_starttime, slice_endtime, "Acc", 0, freqBB1, \
                                     freqBB2, freqBB3, freqBB4, inv)
                        trAccFilt = raw_trace_to_ground_motion_filtered_pruned(trPadded, \
                                    slice_starttime, slice_endtime, "Acc", 0, freqBP1, \
                                    freqBP2, freqBP3, freqBP4, inv)
                        trVelFilt = raw_trace_to_ground_motion_filtered_pruned(trPadded, \
                                    slice_starttime, slice_endtime, "Vel", 0, freqBP1, \
                                    freqBP2, freqBP3, freqBP4, inv)
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
                        T4 = timeit.default_timer()
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
                                AccRMSlabel = str(freqBP2) + "-" + str(freqBP3) + "Hz RMS Acc (cm/s^2)"
                                AccNspikeslabel =  str(freqBP2) + "-" + str(freqBP3) + "Hz Spikes Acc (cm/s^2)"
                                VelFiltlabel =  "   " + str(freqBP2) + "-" + str(freqBP3) + "Hz    Vel (cm/s)"
                                for ij in range(0,len(stAccBroadplot)):
                                    stAccBroadplot[ij].data = stAccBroadplot[ij].data*100
                                    stAccFiltplot[ij].data = stAccFiltplot[ij].data*100
                                    stVelFiltplot[ij].data = stVelFiltplot[ij].data*100
                                make_station_figure_pip_squeak(strawplot,stVelFiltplot,stAccFiltplot,stAccFiltplot,datastalta,"Raw       (counts)",VelFiltlabel,AccRMSlabel,AccNspikeslabel,"     STA/LTA",0,0,0.07,0.34,20,RMSlen)  #--- of order 25sec/channel for 1 hr long traces
                        T5 = timeit.default_timer()
                        Tplot = T5-T4
            
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
                    snr20_0p34cm = count_peaks_stalta(dataAccBroad,datastalta,sta,lta,mpd,20,dt,0.0034)  #--- ShakeAlert stat. acceptance thresh. is now 0.0034 m/s^2 = 0.34cm/s^2.
                    RMSduration_0p07cm = duration_exceed_RMS(dataAccBroad,0.0007,RMSlen,dt)  #--- ShakeAlert stat. acceptance thresh. is now 0.0007 m/s^2 = 0.07cm/s^2.
                    T3 = timeit.default_timer()
            
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
            
                    if ( pctavailable > 95. ):
                        strpctavail = str( "pctavailable_PASS: %.4f " % (100*dt*nptstotal/lenrequested) )
                    else:
                        strpctavail = str( "pctavailable_FAIL: %.4f " % (100*dt*nptstotal/lenrequested) )
            
            #        print ( "%s  download: %.2fs calculate: %.2fs plot: %.2fs %s %s %s %s  Nsegments: %d  segmentlong: %.3f  segmentshort: %.3f " % (sncl, T1-T0, T2-T1-Tplot, Tplot, strngap, strrms, strnspikes, strpctavail, itrace, segmentlong, segmentshort) )
                    print ( "%s calculate: %.2fs plot: %.2fs %s %s %s %s  Nsegments: %d  segmentlong: %.3f  segmentshort: %.3f " % (sncl, T3-T2-Tplot, Tplot, strngap, strrms, strnspikes, strpctavail, ntr, segmentlong, segmentshort) )
                    metric_thresholds = { 
                                "spikes_per_hour_threshold": 1.0, \
                                "rms_exceeded_per_hour_threshold": 60.0, \
                                "clock_lock_lcq_threshold" : None, \
                                "clock_lock_lce_threshold" : 5000
                               }
                    metrics = { 
                               "spikes_total": (snr20_0p34cm, "no_threshold"), \
                               "spikes_per_hour": (snr20_0p34cm/durationinhours, "pass" if snr20_0p34cm/durationinhours < 1.0 else "fail"), \
                               "rms_exceeded_per_hour": (RMSduration_0p07cm/durationinhours, "pass" if RMSduration_0p07cm/durationinhours < 60.0 else "fail"), \
                               "clock_lock_lcq" : (50, "fail"), \
                               "clock_phase_lce" : (5040/1.0E6, "fail"),  \
                               "acceptable_latency" : (97.3, "fail")
                               }
                    if sncl not in channel_metrics:
                        channel_metrics[sncl] = metrics

            with open("./templates/" + net_obj.code + "." + sta_obj.code + ".html", "w") as fh:
                fh.write(template.render(starttime=starttime,endtime=endtime, \
                         network_code=net_obj.code,station=sta_obj,allowed=SEISMIC_CHANNELS, \
                         metrics=channel_metrics))
            HTML("./templates/"+net_obj.code + "." + sta_obj.code+".html").write_pdf(net_obj.code + "." + sta_obj.code + ".pdf")
