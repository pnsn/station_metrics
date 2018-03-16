
Metrics
=======

## C
# *nr20_0p34cm* Number of spikes with STA/LTA > 20 and amplitude exceeding 0.34 cm/s^2 using acceleration data filtered 0.3-15 Hz. 

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

## metrics counting spikes/triggers

Counts the hourly averaged number of spikes/potential earthquake triggers by using an short term average to long term average (STA/LTA) function.  ShakeAlert and regional seismic networks use an STA/LTA function to identify potential earthquake triggers.  A minimum absolute amplitude criteria is also imposed in order to ignore very low amplitude features.  This metric can be used to identify stations that might have low noise levels in a power spectrum, but frequent triggers.

The STA/LTA functions are calculated on filtered velocity traces, regardless if the instrument natively records acceleration (strong motion station) or velocity (short period and broadband stations).  Before a peak in the STA/LTA function that exceeds a theshold (e.g. 20) can be counted as a spike, the peak absolute amplitude within a short time window on the corresponding gain corrected filtered acceleration trace must exceed a threshold (e.g. 0.34 cm/s^2).  The time window used is equal to the length of the LTA window.  When scanning the STA/LTA function for peaks, only those exceeding a threshold and separatd by a minimum distance between peaks (mpd, twice the LTA time is reasonable) are considered.  The length of the STA and LTA windows are configurable and defaulted to valaues of 0.5 and 5.0sec, respectively.  Both the velocity and acceleration traces are filtered using a 0.3-15 Hz Butterworth bandpass filter.  This processing and these parameters mimic early steps in the EPIC algorithm used by ShakeAlert.

In the figure below, only one spike is counted in the time series shown.  If the STA/LTA threshold was lowered to 5, for example, there would be a second spike counted (at around 22:01:45).

<img src="https://github.com/pnsn/station_metrics/blob/master/station_metrics/img/Metric_Nspikes.png" width=800 alt="Metric: Nspikes" />

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

