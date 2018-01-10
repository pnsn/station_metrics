
<a href="https://drive.google.com/drive/u/1/folders/0B8N_TOtFCLuyOVNUUmVuTzJTNHc">Google drive folder for Station_Metrics</a>

# Files

- *calculate_metrics.py*    This is the main ObsPy based python script for calculating metrics. 
- *get_data_metadata.py*    This uses ObsPy bulkrequests to download data.  Also gets metadata/response/gain factors.
- *noise_metrics.py*        These are functions to calculate metrics such as noise floor, N spikes, duration of RMS > threshold.
- *plot_station.py*         Makes a simple .png figure of the seismogram being analyzed.
- *database_read_write.py*  Reads and writes to the postgres database.  NOTE: needs to change INSERT to UPSERT.
- *TestDownloadingSpeed.py* Simple script to test downloading speed at FDSN data centers. Choose either serial or bulk download.
- *run_metrics.csh*  This is the shell script that runs the python code, it's set up on an hourly cron.
- *ShakeAlertList.IRISZ, ShakeAlertList.NCEDCZ, ShakeAlertList.SCEDCZ* These are the (outdated) channel lists for the three data centers.

# Station Metrics

These are the collection of scripts to calculate near-real time station metrics which are being calculated hourly.

## metrics of completeness

- *pctavailable* Percentage of data returned of data requested.
- *ngaps* Number of gaps.
- *segmentshort*  Duration in seconds of the shortest segment.
- *segmentlong*  Duration in seconds of the longest segment.

## simple first-order metrics

- *rawrange*  Range in counts.
- *rawmean*  Mean in counts.
- *rawrms*  RMS in counts.
- *rawmin*  Minimum amplitude in counts.
- *rawmax*  Maximum amplitude in counts.

## metrics of noise (do we want the full PSD?)

- *pow50sec* Power in db at 50 seconds.
- *pow30sec* Power in db at 30 seconds.
- *pow20sec* Power in db at 20 seconds.
- *pow10sec* Power in db at 10 seconds.
- *pow5sec* Power in db at 5 seconds.
- *pow1Hz* Power in db at 1 Hertz.
- *pow5Hz* Power in db at 5 Hertz.
- *pow10Hz* Power in db at 10 Hertz.
- *pow20Hz* Power in db at 20 Hertz.
- *pow50Hz* Power in db at 50 Hertz.
- *RMS0p01cm* Total duration in seconds of RMS acceleration amplitude exceeding 0.01 cm/s^2 using a 5 sec RMS window.
- *RMS0p035cm* Total duration in seconds of RMS acceleration amplitude exceeding 0.035 cm/s^2 using a 5 sec RMS window. This was the proposed ShakeAlert threshold, but has since been doubled to 0.07 cm/s^2.
- *RMS0p1cm* Total duration in seconds of RMS acceleration amplitude exceeding 0.1 cm/s^2 using a 5 sec RMS window.
- *RMS1cm* Total duration in seconds of RMS acceleration amplitude exceeding 1 cm/s^2 using a 5 sec RMS window.
- *NoiseFloorVel* Range in cm/s of the 2nd to 98th percentile of sorted velocity amplitudes, which approximates median envelope amplitude.
- *NoiseFloorAcc* Range of cm/s^2 the 2nd to 98th percentile of sorted acceleration amplitudes, which approximates median envelope amplitude.

## metrics of spikes/triggers

What I've been calculating.  Uses ObsPy z_detect trigger with 1 sec window.
- *snr10_0p01cm* Number of spikes with SNR > 10 and amplitude exceeding 0.01 cm/s^2 using acceleration data filtered 0.3-15 Hz.  Good for looking for very good stations.
- *snr20_0p05cm* Number of spikes with SNR > 20 and amplitude exceeding 0.05 cm/s^2 using acceleration data filtered 0.3-15 Hz.
- *snr20_0p17cm* Number of spikes with SNR > 20 and amplitude exceeding 0.17 cm/s^2 using acceleration data filtered 0.3-15 Hz.  This was the proposed ShakeAlert threshold, but has since been doubled to 0.35 cm/s^2.
- *snr20_1cm* Number of spikes with SNR > 20 and amplitude exceeding 1 cm/s^2 using acceleration data filtered 0.3-15 Hz.  Good for looking for bad stations.
- *snr20_3cm* Number of spikes with SNR > 20 and amplitude exceeding 3 cm/s^2 using acceleration data filtered 0.3-15 Hz.
- *snr20_5cm* Number of spikes with SNR > 20 and amplitude exceeding 5 cm/s^2 using acceleration data filtered 0.3-15 Hz.  Good for looking for terrible stations.

## Some outstanding questions
- *0.75-20 Hz or 0.3-15 Hz* filtering, both have been thrown around.
- Should metrics use *acceleration* or *acceleration/velocity (native ground motion units)*?
- Are the suggested thresholds for RMS and Nspikes metrics appropriate/complete? 
- Should we use an sta/lta (ObsPy: classic_sta_lta) ratio where sta = 0.5s and lta = 5.0 s (0.4 sec/trace), rather than the faster z_detect (0.1sec)?

## Groups of metrics
- completness
- noise
- ShakeAlert_acceptance = pctavailable, ngaps, rawmean, rawrange, RMS0p035cm, snr20_0p17cm
- health = pctavailable, ngaps, rawmean

