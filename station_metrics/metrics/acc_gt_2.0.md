# acc_gt_2.0

Acceleration Exceedances Above 2 cm/s^2

## Summary

This metric counts the number of separated times during the analysis window
that the absolute ground acceleration, highpassed at 0.075 Hz, exceeds
2 cm/s^2. Each exceedance that is counted blanks out the following 30 s, so a
single strong arrival contributes once. 2 cm/s^2 is the amplitude threshold
used by the FinDer algorithm.

## Uses

This approximates how often FinDer would see the channel cross its amplitude
threshold, so it estimates a station's contribution to FinDer's workload
without running FinDer. Unlike the spike metrics there is no STA/LTA test at
all: a slow build-up to a large amplitude counts here but would not trigger an
onset detector. Because 2 cm/s^2 is well above ordinary background noise, a non
zero value on a quiet day means either a real, felt earthquake or an instrument
that is badly misbehaving, and hours with double digit counts on a single
station while its neighbours read zero are almost always the latter.

## Data Analyzed

Traces - one N.S.L.C (Network.Station.Location.Channel) per measurement. Where
the channel has gaps, each segment is processed separately and the resulting
samples are pooled into one series.

Window - the analysis window, running from 5.05 s before the top of the hour to
the end of the hour, 3605.05 s in total. Waveforms are requested with a further
120 s of padding on each side, which is used during processing and then
discarded.

Data Source - FDSN dataselect from the permanent archive: EarthScope/IRIS DMC
for PNSN data, NCEDC for NCSN data, SCEDC for SCSN data. Instrument metadata is
requested at response level from the same archive.

SEED Channel Types - ?H? and ?N? (high gain broadband and accelerometer), as
listed in the ShakeAlert channel file.

## Algorithm

1. Request the analysis window plus 120 s of padding on each side, for a single
   N.S.L.C, along with the channel's response level metadata.
2. Detrend the padded trace with a third-order polynomial, remove the mean, and
   divide by the channel's overall sensitivity from the metadata.
3. Convert to acceleration. A channel whose second SEED code letter is N is
   already an accelerometer; anything else is differentiated from velocity.
4. Apply a causal Butterworth highpass at 0.075 Hz with 2 corners.
5. Cut the trace to the analysis window and remove the mean again. Pool the
   samples from all segments into one series a, in m/s^2.
6. Mark every sample whose absolute value reaches the threshold:

   candidate(n) = 1 if |a(n)| >= 0.02 m/s^2, else 0

7. Walk forward through the candidates. Each candidate that is kept blanks out
   every other candidate within the following 30 s.
8. Report the number of candidates that survive.

## Metric Values Returned

value - number of separated exceedances of 2 cm/s^2 in the window (count).

starttime - beginning of the reporting hour (UTC).

endtime - end of the reporting hour (UTC).

channel - the channel analyzed, as N.S.L.C.

## Threshold

10 counts.

## Notes

There is no STA/LTA or waveform shape test of any kind. A DC step, a
calibration pulse and a genuine earthquake all count equally if they cross the
amplitude threshold, which is deliberate: FinDer's own threshold test is
similarly blind, and the purpose here is to estimate what FinDer would see.

The 30 s blanking is applied forward only, from each kept exceedance, so the
count depends on the order the samples are examined. In practice this matters
only for sustained shaking above threshold, which is counted once every 30 s
for as long as it lasts.

Because the measurement window is 3605.05 s rather than 3600 s, an hour of
continuous above-threshold shaking would produce 121 counts rather than 120.

## Change Log

Aug 2026: the processing order changed. Previously the trace was cut to the
analysis window before differentiation and filtering, so the filter start-up
transient fell inside the measured window.

## Contact

squac-help@uw.edu

## See Also

hourly_max_acc, acc_spikes_gt_.34

## Updated

2026-08-28
