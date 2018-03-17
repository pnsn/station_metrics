
<a href="https://drive.google.com/drive/u/1/folders/0B8N_TOtFCLuyOVNUUmVuTzJTNHc">Google drive folder for Station_Metrics</a>

These are the collection of scripts to calculate near-real time station metrics which are being calculated hourly at the PNSN.

# Files

- *calculate_metrics.py*    This is the main ObsPy based python script for calculating metrics for a list of stations.  Writes to a db. 
- *calculate_metrics_for_acceptance.py* This is a one-off script made for the ShakeAlert station acceptance group. (still in testing/flux) 
- *get_data_metadata.py*    This uses ObsPy bulkrequests to download data.  Also gets metadata/response/gain factors.
- *noise_metrics.py*        These are functions to calculate metrics such as noise floor, N spikes, duration of RMS > threshold.
- *plot_station.py*         Makes a simple .png figure of the seismogram being analyzed.
- *database_read_write.py*  Reads and writes to the postgres database.  NOTE: needs to change INSERT to UPSERT.
- *TestDownloadingSpeed.py* Simple script to test downloading speed at FDSN data centers. Choose either serial or bulk download.
- *run_metrics.csh*  This is the shell script that runs the python code, it's set up on an hourly cron.
- *ShakeAlertList.IRISZ, ShakeAlertList.NCEDCZ, ShakeAlertList.SCEDCZ* These are the (outdated) channel lists for the three data centers.

# Station Metrics

<a href="https://github.com/pnsn/station_metrics/tree/master/station_metrics/metrics">Documentation for available metrics.</a>

# Speed

Using calculate_metrics.py, calculating hourly metrics for 400 channels takes around 20 minutes on a single CPU when data are downloaded from an FDSNWS such as IRIS.

# Some usage examples



