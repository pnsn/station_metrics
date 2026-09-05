# rms_bp_above_.07

Duration of Bandpassed Acceleration RMS Above 0.07 cm/s^2

## Summary

This metric reports the total number of seconds during the analysis window that
a five second sliding window RMS of ground acceleration, bandpassed between
0.075 Hz and 15 Hz, stays above 0.07 cm/s^2. 0.07 cm/s^2 is the 2018 ShakeAlert
station acceptance threshold.

## Uses

This is a duration rather than a count, which makes it the right tool for
finding stations that are persistently too noisy for early warning rather than
stations that occasionally spike. Because the 15 Hz upper corner removes high
frequency energy, comparing this value against the highpassed version separates
two different problems: a channel scoring high on both is genuinely noisy in
the band that matters, while a channel scoring high only on the highpassed
version is noisy above 15 Hz, which usually indicates electronics or digitizer
trouble rather than site noise.

## Data Analyzed

Traces - one N.S.L.C (Network.Station.Location.Channel) per measurement. Where
the channel has gaps, each segment is processed separately and the resulting
samples are pooled into one series before the RMS is computed.

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
4. Apply a causal Butterworth bandpass from 0.075 Hz to 15 Hz with 2 corners.
5. Cut the trace to the analysis window, discarding the padding along with the
   filter start-up transient, and remove the mean again.
6. Pool the samples from all segments into one series a, in m/s^2.
7. Square the series, smooth it with a centred boxcar 5 s long, and take the
   square root to give a sliding window RMS at every sample:

   RMS(n) = sqrt( mean( a[n - 2.5s : n + 2.5s]^2 ) )

8. Count the samples of the RMS function above the threshold and convert to
   seconds by multiplying by the sample interval:

   rms_bp_above_.07 = count( RMS > 0.0007 m/s^2 ) * delta

## Metric Values Returned

value - seconds during the window that the RMS exceeded 0.07 cm/s^2, or -1 if
the returned trace was shorter than the 5 s RMS window.

starttime - beginning of the reporting hour (UTC).

endtime - end of the reporting hour (UTC).

channel - the channel analyzed, as N.S.L.C.

## Threshold

60.0 seconds.

## Notes

On channels sampled at or below 30 samples per second the 15 Hz upper corner
sits at or above the Nyquist frequency. ObsPy warns about this and clamps the
filter, so on those channels this metric becomes equivalent to the highpassed
version.

The RMS window is centred on each sample rather than trailing it, so the
reported duration extends approximately 2.5 s either side of the noisy
interval.

A value of -1 means the trace was shorter than 5 s. It is uploaded rather than
withheld, because withholding would be ambiguous between "no data existed",
"the channel was not analyzed" and "the trace was too short".

## Change Log

Aug 2026: the SQUAC metric name contained a double underscore and was spelled
rms__bp_above_.07. It is now rms_bp_above_.07. The underlying metric id, 87, is
unchanged, so historical data is continuous across the rename.

Aug 2026: the processing order changed. Previously the trace was cut to the
analysis window before differentiation and filtering, so the filter start-up
transient fell inside the measured window.

## Contact

squac-help@uw.edu

## See Also

rms_above_.07, hourly_noise_floor_bp_acc, acc_bp_spikes_gt_.34

## Updated

2026-08-28
