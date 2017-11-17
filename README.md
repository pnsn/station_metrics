
#Link to google drive:

<a href="https://drive.google.com/drive/u/1/folders/0B8N_TOtFCLuyOVNUUmVuTzJTNHc">Google drive folder for Station_Metrics</a>

https://drive.google.com/drive/u/1/folders/0B8N_TOtFCLuyOVNUUmVuTzJTNHc

# Files

- *MetricsForIgor.py*  This is the main ObsPy based python script for calculating metrics... it's a version I handed off to Igor.  It's pretty similar to what's in production on web4.
- *MetricsForIgor.csh*  This is the shell script that runs the python code, it's set up on an hourly cron.
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
- *RMS0p035cm* Total duration in seconds of RMS acceleration amplitude exceeding 0.035 cm/s^2 using a 5 sec RMS window.
- *RMS0p05cm* Total duration in seconds of RMS acceleration amplitude exceeding 0.05 cm/s^2 using a 5 sec RMS window.
- *RMS0p1cm* Total duration in seconds of RMS acceleration amplitude exceeding 0.1 cm/s^2 using a 5 sec RMS window.
- *RMS0p5cm* Total duration in seconds of RMS acceleration amplitude exceeding 0.5 cm/s^2 using a 5 sec RMS window.
- *RMS1cm* Total duration in seconds of RMS acceleration amplitude exceeding 1 cm/s^2 using a 5 sec RMS window.
- *V2to98* Range in cm/s of the 2nd to 98th percentile of sorted velocity amplitudes, which approximates median envelope amplitude.
- *A2to98* Range of cm/s^2 the 2nd to 98th percentile of sorted acceleration amplitudes, which approximates median envelope amplitude.

## metrics of spikes/triggers

What I've been calculating.  Uses ObsPy z_detect trigger with 1 sec window.
- *snr5_0p1cm* Number of spikes with SNR > 5 and amplitude exceeding 0.1 cm/s^2 using acceleration data filtered 0.3-15 Hz.
- *snr5_0p5cm* Number of spikes with SNR > 5 and amplitude exceeding 0.5 cm/s^2 using acceleration data filtered 0.3-15 Hz.
- *snr10_0p5cm* Number of spikes with SNR > 10 and amplitude exceeding 0.5 cm/s^2 using acceleration data filtered 0.3-15 Hz.
- *snr20_0p5cm* Number of spikes with SNR > 20 and amplitude exceeding 0.5 cm/s^2 using acceleration data filtered 0.3-15 Hz.
- *snr5_1cm* Number of spikes with SNR > 5 and amplitude exceeding 1 cm/s^2 using acceleration data filtered 0.3-15 Hz.
- *snr10_1cm* Number of spikes with SNR > 10 and amplitude exceeding 1 cm/s^2 using acceleration data filtered 0.3-15 Hz.
- *snr20_1cm* Number of spikes with SNR > 20 and amplitude exceeding 1 cm/s^2 using acceleration data filtered 0.3-15 Hz.
- *snr5_2cm* Number of spikes with SNR > 5 and amplitude exceeding 2 cm/s^2 using acceleration data filtered 0.3-15 Hz.
- *snr10_2cm* Number of spikes with SNR > 10 and amplitude exceeding 2 cm/s^2 using acceleration data filtered 0.3-15 Hz.
- *snr20_2cm* Number of spikes with SNR > 20 and amplitude exceeding 2 cm/s^2 using acceleration data filtered 0.3-15 Hz.

What I'm calculating for Glenn.  Uses ObsPy z_detect trigger with 1 sec window.
- *snr20_0p05cm* Number of spikes with SNR > 20 and amplitude exceeding 0.05 cm/s^2 using acceleration data filtered 1-5 Hz.
- *snr20_0p1cm* Number of spikes with SNR > 20 and amplitude exceeding 0.1 cm/s^2 using acceleration data filtered 1-5 Hz.
- *snr15_0p17cm* Number of spikes with SNR > 15 and amplitude exceeding 0.17 cm/s^2 using acceleration data filtered 1-5 Hz.
- *snr20_0p17cm* Number of spikes with SNR > 20 and amplitude exceeding 0.17 cm/s^2 using acceleration data filtered 1-5 Hz.
- *snr20_0p5cm* Number of spikes with SNR > 20 and amplitude exceeding 0.5 cm/s^2 using acceleration data filtered 1-5 Hz.
- *snr20_1cm* Number of spikes with SNR > 20 and amplitude exceeding 1 cm/s^2 using acceleration data filtered 1-5 Hz.
- *snr20_2cm* Number of spikes with SNR > 20 and amplitude exceeding 2 cm/s^2 using acceleration data filtered 1-5 Hz.

What should be calculated??
- *0.75-20Hz* filtering
- *acceleration* or *acceleration/velocity (native ground motion units)*?
- *amplitude thresholds* of: 0.05, 0.1, 0.17, 0.5, 1, 2 cm/s^2?
- *SNR* thresholds of 5 and 15?
- should use an sta/lta (ObsPy: classic_sta_lta) ratio where sta = 0.5s and lta = 5.0 s?

## Groups of metrics
- completness
- noise
- ShakeAlert_acceptance = pctavailable, ngaps, rawmean, rawrange, RMS0p035cm, snr20_0p17cm
- health = pctavailable, ngaps, rawmean


