

# Overview

These are the collection of scripts to calculate station metrics.  calculate_metrics.py is built to operate in near-real time and is being run hourly at the PNSN and writing results to a PostgreSQL database.  eew_stationreport is a similar script being run on a server at PNSN for one-at-a-time ShakeAlert station acceptance and accessible to select users <a href="http://eewreport.pnsn.org">here</a>.  eew_stationreport includes Pass/Fail criteria set by the ShakeAlert Regional Coordinators group and writes nicely formatted .html and .pdf files for their use.  Summary figures showing the trace analyzed along with derivative traces (e.g. STA/LTA function, filtered versions) are available with both scripts.

*NOTE:  A few things are still needed.  eew_stationreport is clean, but calculate_metrics.py still needs to be cleaned up a bit.*

# Installation

These python scripts run on Python 2.7 and Python 3.5 with the following major package dependencies:
<a href="http://www.numpy.org/">numpy</a>, <a href="https://github.com/obspy/obspy/wiki">obspy</a>, <a href="https://matplotlib.org">matplotlib</a>.  Pip_squeak.py additionally requires: <a href="https://weasyprint.org">weasyprint</a> and <a href="https://anaconda.org/anaconda/jinja2">jinja2</a>.

These can easily be added via command line using <a href="https://www.anaconda.com/">Anaconda</a>.  It is recommended you not use your system python, rather use a virtual environment.

```
>> conda create -n stationmetrics python=3.5     (OR "python=2.7" also works)
>> conda activate stationmetrics
>> conda install -c anaconda numpy
>> conda install -c conda-forge matplotlib
>> conda install obspy

If running eew_stationreport these are also needed:
>> conda install -c anaconda jinja2
>> pip install weasyprint

If running calculate_metrics and writing to a postgreSQL database these are also needed:
<<<<<<< HEAD
pip install psycopg2
pip install pgcopy
=======
>> pip install psycopg2
>> pip install pgcopy
>>>>>>> babf0317b513c94007f353610fa233464628edbe
```

# Files

- *calculate_metrics.py*       This is the main ObsPy based python script for calculating metrics for a list of stations.  Writes to a db. 
- *eew_stationreport*          This is a one-off script made for the ShakeAlert station acceptance group. (still in testing/flux) 
- *get_data_metadata.py*       This uses ObsPy bulkrequests to download data.  Also gets metadata/response/gain factors.
- *noise_metrics.py*           These are functions to calculate metrics such as noise floor, N spikes, duration of RMS > threshold.
- *preprocessing.py*           Converts raw traces ground motion (ACC/VEL/DISP) with either full response or just gain, also filters and prunes.
- *TestDownloadingSpeed.py*    Simple script to test downloading speed at FDSN data centers. Choose either serial or bulk download.

Used only by eew_stationreport:
- *config.eew_stationreport*   Simple config file for eew_stationreport to input parameters, defaults are for ShakeAlert station acceptance.
- *parse_and_validate_args.py* Used by eew_stationreport to read, pase and validate input arguments.
- *external.py*                Reads output files from sniffwave_tally and produces eew_stationreport metrics:  - percent_latency_good, gaps_per_hour, percent_completeness, percent_completeness_w_penalty.
- *plot_eew_stationreport.py*  Makes a simple .png figure of the seismogram being analyzed, raw trace, STA/LTA trace, ShakeAlert station acceptance thresholds etc.
- *run_metrics.csh*            This is the shell script that runs the python code, it's set up on an hourly cron.

Used only by calculate_metrics (for database):
- *config.db*                  Simple config file for calculate_metrics.py, includes database name and host machine.
- *ShakeAlertList.IRISZ, ShakeAlertList.NCEDCZ, ShakeAlertList.SCEDCZ* These are the (outdated) channel lists for the three data centers.
*plot_station.py*            Makes a simple .png figure of the seismogram being analyzed.
- *database_read_write.py*     Reads and writes to the postgres database.  NOTE: needs to change INSERT to UPSERT.
- *make_sql_tables*            SQL commands to make various station metrics database tables.
- *metrics.csv*                CSV file that includes the metric name, units and description.
- *phase1.htm, report.htm*     Templates for html/pdf output.

# Station Metrics

<a href="https://github.com/pnsn/station_metrics/tree/master/station_metrics/metrics">Documentation for available metrics.</a>

# Speed

Using calculate_metrics.py, calculating hourly metrics for 400 channels takes around 20 minutes on a single CPU when data are downloaded from an FDSNWS such as IRIS.

eew_stationreport takes about 5 sec to connect to an FDSNWS, then about 1 sec per hour per trace of calculations.  Running for 336 hours (2 weeks) takes of order 30 min, depending on sampling rate and how noisy a trace is.  Hourly plots take about a minute each.

# eew_stationreport for one-off ShakeAlert station assessment

Metrics calculated are:

-*Spikes*  Number of spikes with SNR > 20 and amplitude exceeding 0.34 cm/s^2.  For both broadband and strong motion instruments, this metric uses two traces derived from the raw trace.  The SNR function is calculated on velocity traces high-pass filtered above 3 Hz.  The STA/LTA lengths are 0.05/5.0 sec long.  The local peak of the STA/LTA function is the reference time.  Amplitudes are measured on gain-corrected acceleration traces filtered 0.075 - 15 Hz.  If the absolute value of any ampilitude within 5.05 sec (STA+LTA) of the reference time exceeds 0.34 cm/s^2, a spike is counted.  The minimum trace length is 10 sec.  The minimum distance between peaks to count in the STA/LTA function is 10 sec.  Passing is no more than 1.0 spike per hour on average.

-*RMS*  This metric is derived from an RMS function based on the gain-corrected acceleration traces from each channel filtered between 0.075 - 15 Hz.  The RMS function is calculated using a sliding 5 second window at each point.  The metric is computed by determining the total duration (in sec) of the RMS function exceeding the threshold of 0.07 cm/s^2.  Passing is no more than 60 sec per hour on average.

*Percent data with latency < 3.5 sec*  This is measured using sniffwave on local earthworm machines at the various contributing institutions.  <a href="https://github.com/pnsn/sniffwave_tally">sniffwave_tally</a> runs sniffwave and tallies the results.  Passing is at least 98% of the data have latency < 3.5 sec.  
Note:  only sniffwave_tally results are considered if the entire sniffing period falls within the (eew_stationreport) requested time period.  For example, if sniffwave_tally has a duration of 600 seconds (10min) and is ran at minutes 0,10,20... and the eew_stationreport request is for T00:05:00 to T00:25:00, then the results from only one sniffwave_tally run (from T00:10:00 to T00:19:59.99) will be considered/read.

*Percent completeness*  This is the percent of waveform data returned in the time that sniffwave sniffs.  Passing is at least 98% completeness.

*Percent completeness including gap penalties*  This is the percent of waveform data returned in the time that sniffwave sniffs and includes a 30 sec penalty following every gap in data.  This mimicks ShakeAlert which requires at least 30 sec of continuous data before making a measurement.  Passing is at least 98% completeness.

*Number of gaps per hour*  Passing is no more than 1 gap per hour on average.

*Percentage of data with acceptable clock locking/quality*  This uses the values of the LCQ channel (clock quality).  Passing is at least 98% of the sample points recorded must have a value of at least 60 (%).  Note: this requires Q330 dataloggers.  Currently this metric will be ignored for Obsidians, Basalts, Centaurs, Titans, RT130s.

*Percentage of data with acceptable clock drift/phase*  This uses the LCE channel (clock phase, i.e. drift).  Passing is at least 98% of the samples must have an absolute value of less than 0.005 (sec).  Note: this requires Q330 dataloggers.  Currently this metric will be ignored for Obsidians, Basalts, Centaurs, Titans, RT130s.

Notes: All PASS/FAIL results are hourly averaged.  All PASS/FAIL results are over the time window specified by the user.

# Examples of running eew_stationreport

Run for a duration (-d) of 1 hour:
```
>> ./eew_stationreport  -N UW -S REED -C HNZ -L -- -dc IRIS -s 2018-01-03T22:00:00 -d 1
>> UW.REED.--.HNZ  download: 0.33s calculate: 1.17s plot: 0.00s ngaps_PASS: 0.000  rms_FAIL: 738.525  nspikes_FAIL: 23.000  pctavailable_PASS: 100.0001   Nsegments: 1  segmentlong: 3605.055  segmentshort: 3605.055 
``` 

Same thing, but use an endtime (-e) instead.  And add a figure (-p).  Note, plotting is SLOW (64sec):
```
>> ./eew_stationreport  -N UW -S REED -C HNZ -L -- -dc IRIS -s 2018-01-03T22:00:00 -e 2018-01-03T23:00:00 -p
>> UW.REED.--.HNZ  download: 0.34s calculate: 1.14s plot: 64.28s ngaps_PASS: 0.000  rms_FAIL: 738.525  nspikes_FAIL: 23.000  pctavailable_PASS: 100.0001   Nsegments: 1  segmentlong: 3605.055  segmentshort: 3605.055 
```

Now use a list of station (-i) and run it for two weeks.  Note: a datacenter (-dc) is still needed.
```
>> cat MyStationList 
UW ALKI -- ENZ
UW ALST -- ENZ
UW BABE -- ENZ
UW BABR -- BHZ
UW REED -- HNZ
>> ./eew_stationreport -i MyStationList -dc IRIS -s 2018-01-03T22:00:00 -d 336
UW.ALKI.--.ENZ No_data_returned

UW.ALST.--.ENZ  download: 27.96s calculate: 176.58s plot: 0.00s ngaps_PASS: 0.012  rms_PASS: 0.000  nspikes_PASS: 0.000  pctavailable_PASS: 99.9521   Nsegments: 5  segmentlong: 487084.600  segmentshort: 1566.760 
UW.BABE.--.ENZ  download: 27.96s calculate: 351.37s plot: 0.00s ngaps_PASS: 0.030  rms_FAIL: 151.445  nspikes_FAIL: 2.521  pctavailable_PASS: 99.9949   Nsegments: 11  segmentlong: 499481.000  segmentshort: 4548.000 
UW.BABR.--.BHZ  download: 27.96s calculate: 415.10s plot: 0.00s ngaps_PASS: 0.003  rms_PASS: 0.000  nspikes_PASS: 0.000  pctavailable_PASS: 99.9540   Nsegments: 2  segmentlong: 774467.750  segmentshort: 434581.475 
UW.REED.--.HNZ  download: 27.96s calculate: 840.27s plot: 0.00s ngaps_PASS: 0.065  rms_FAIL: 334.611  nspikes_FAIL: 15.613  pctavailable_PASS: 99.9902   Nsegments: 23  segmentlong: 170661.830  segmentshort: 0.860 
>> 
>>
```

Example of plotting output from eew_stationreport:
<img src="https://github.com/pnsn/station_metrics/blob/master/station_metrics/img/WAVEFORMS.2018.1.3.22.UW.REED..HNZ.png" width=800 alt="Metric: Noise Floor" />

