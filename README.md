
<a href="https://drive.google.com/drive/u/1/folders/0B8N_TOtFCLuyOVNUUmVuTzJTNHc">Google drive folder for Station_Metrics</a>
# Caution: under reconstruction, expect bugs.
# Overview

These are the collection of scripts to calculate near-real time station metrics which are being calculated hourly at the PNSN.

*NOTE:  A few things are still needed.  pip_squeak.py is clean, but calculate_metrics.py still needs to be cleaned up (as well as making it run from a config file).*

# Installation

These python scripts run on Python 2.7 and Python 3.5 with the following major package dependencies:
<a href="http://www.numpy.org/">numpy</a>, <a href="https://github.com/obspy/obspy/wiki">obspy</a>, <a href="https://matplotlib.org">matplotlib</a>, <a href="https://weasyprint.org">weasyprint</a>.

These can easily be added via command line using <a href="https://www.anaconda.com/">Anaconda</a>.  It is recommended you not use your system python, rather use a virtual environment.

```
>> conda create -n stationmetrics python=3.5
>> source activate stationmetrics
>> conda install obspy
>> conda install -c conda-forge matplotlib
>> conda install -c anaconda numpy
>> pip install weasyprint
```

# Files

- *calculate_metrics.py*       This is the main ObsPy based python script for calculating metrics for a list of stations.  Writes to a db. 
- *pip_squeak.py*              This is a one-off script made for the ShakeAlert station acceptance group. (still in testing/flux) 
- *parse_and_validate_args.py* Used by pip_squeak.py to read, pase and validate input arguments.
- *get_data_metadata.py*       This uses ObsPy bulkrequests to download data.  Also gets metadata/response/gain factors.
- *noise_metrics.py*           These are functions to calculate metrics such as noise floor, N spikes, duration of RMS > threshold.
- *plot_station.py*            Makes a simple .png figure of the seismogram being analyzed.
- *plot_pip_squeak.py*         Makes a simple .png figure of the seismogram being analyzed, raw trace, STA/LTA trace, ShakeAlert station acceptance thresholds etc.
- *database_read_write.py*     Reads and writes to the postgres database.  NOTE: needs to change INSERT to UPSERT.
- *TestDownloadingSpeed.py*    Simple script to test downloading speed at FDSN data centers. Choose either serial or bulk download.
- *run_metrics.csh*            This is the shell script that runs the python code, it's set up on an hourly cron.
- *ShakeAlertList.IRISZ, ShakeAlertList.NCEDCZ, ShakeAlertList.SCEDCZ* These are the (outdated) channel lists for the three data centers.
- *config.pip_squeak*          Simple config file for pip_squeak to input parameters, defaults are for ShakeAlert station acceptance.

# Station Metrics

<a href="https://github.com/pnsn/station_metrics/tree/master/station_metrics/metrics">Documentation for available metrics.</a>

# Speed

Using calculate_metrics.py, calculating hourly metrics for 400 channels takes around 20 minutes on a single CPU when data are downloaded from an FDSNWS such as IRIS.

pip_squeak.py takes about 5 sec to connect to an FDSNWS, then about 1 sec per hour per trace of calculations.  Hourly plots take about a minute each.

# Using pip_squeak for one-off ShakeAlert station assessment

Note: PASS/FAIL results are hourly averaged.

Run for a duration (-d) of 1 hour:
```
>> ./pip_squeak.py  -N UW -S REED -C HNZ -L -- -dc IRIS -s 2018-01-03T22:00:00 -d 1
>> UW.REED.--.HNZ  download: 0.33s calculate: 1.17s plot: 0.00s ngaps_PASS: 0.000  rms_FAIL: 738.525  nspikes_FAIL: 23.000  pctavailable_PASS: 100.0001   Nsegments: 1  segmentlong: 3605.055  segmentshort: 3605.055 
``` 

Same thing, but use an endtime (-e) instead.  And add a figure (-p).  Note, plotting is SLOW (64sec):
```
>> ./pip_squeak.py  -N UW -S REED -C HNZ -L -- -dc IRIS -s 2018-01-03T22:00:00 -e 2018-01-03T23:00:00 -p
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
>> ./pip_squeak.py -i MyStationList -dc IRIS -s 2018-01-03T22:00:00 -d 336
UW.ALKI.--.ENZ No_data_returned

UW.ALST.--.ENZ  download: 27.96s calculate: 176.58s plot: 0.00s ngaps_PASS: 0.012  rms_PASS: 0.000  nspikes_PASS: 0.000  pctavailable_PASS: 99.9521   Nsegments: 5  segmentlong: 487084.600  segmentshort: 1566.760 
UW.BABE.--.ENZ  download: 27.96s calculate: 351.37s plot: 0.00s ngaps_PASS: 0.030  rms_FAIL: 151.445  nspikes_FAIL: 2.521  pctavailable_PASS: 99.9949   Nsegments: 11  segmentlong: 499481.000  segmentshort: 4548.000 
UW.BABR.--.BHZ  download: 27.96s calculate: 415.10s plot: 0.00s ngaps_PASS: 0.003  rms_PASS: 0.000  nspikes_PASS: 0.000  pctavailable_PASS: 99.9540   Nsegments: 2  segmentlong: 774467.750  segmentshort: 434581.475 
UW.REED.--.HNZ  download: 27.96s calculate: 840.27s plot: 0.00s ngaps_PASS: 0.065  rms_FAIL: 334.611  nspikes_FAIL: 15.613  pctavailable_PASS: 99.9902   Nsegments: 23  segmentlong: 170661.830  segmentshort: 0.860 
>> 
>>
```

Example of plotting output from pip_squeak.py:
<img src="https://github.com/pnsn/station_metrics/blob/master/station_metrics/img/WAVEFORMS.2018.1.3.22.UW.REED..HNZ.png" width=800 alt="Metric: Noise Floor" />

