# hourly_max_bp_acc

Maximum Bandpassed Ground Acceleration

## Summary

This metric reports the largest absolute ground acceleration observed on a
channel during the analysis window, from data that has been sensitivity
corrected, converted to acceleration, and bandpassed between 0.075 Hz and
15 Hz. The result is in cm/s^2.

## Uses

The 15 Hz upper corner suppresses high frequency spikes, making this the more
conservative of the two peak acceleration metrics and the one closest to the
band that ShakeAlert algorithms actually operate in. It is used to spot felt
shaking and, more often, to identify channels producing implausibly large
accelerations hour after hour. A channel whose highpassed peak is much larger
than this value has most of its energy above 15 Hz, which is characteristic of
electronic noise or a digitizer problem rather than ground motion.

## Data Analyzed

Traces - one N.S.L.C (Network.Station.Location.Channel) per measurement. Where
the channel has gaps, each segment is processed separately and the resulting
samples are pooled before the peak is taken.

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
2. Detrend the padded trace with a third-order polynomial.
3. Remove the mean.
4. Divide by the channel's overall sensitivity from the metadata. Only the gain
   is removed; the full instrument response is not deconvolved.
5. Convert to acceleration. A channel whose second SEED code letter is N is
   already an accelerometer and is left alone; anything else is treated as a
   velocity sensor and is differentiated.
6. Apply a causal Butterworth bandpass from 0.075 Hz to 15 Hz with 2 corners.
7. Cut the trace to the analysis window, discarding the padding along with the
   filter start-up transient it absorbed.
8. Remove the mean again.
9. Pool the samples from all segments into one series a, in m/s^2, and report
   the largest absolute value converted to cm/s^2:

   hourly_max_bp_acc = 100 * max(|a|)

## Metric Values Returned

value - largest absolute acceleration in the window (cm/s^2).

starttime - beginning of the reporting hour (UTC).

endtime - end of the reporting hour (UTC).

channel - the channel analyzed, as N.S.L.C.

## Threshold

2.0 cm/s^2.

## Notes

On channels sampled at or below 30 samples per second the 15 Hz upper corner
sits at or above the Nyquist frequency. ObsPy warns about this and clamps the
filter, so on those channels the measurement is effectively a highpass at
0.075 Hz and this metric will read the same as hourly_max_acc.

Only the sensitivity is removed, not the full response, so the conversion to
physical units is accurate in the instrument's passband and progressively less
accurate towards its corners.

A channel with no metadata available is skipped entirely rather than reported
with an uncorrected value.

## Change Log

Aug 2026: the processing order changed. Previously the trace was cut to the
analysis window before integration or differentiation and before filtering, so
the filter transient fell inside the measured window. Cutting is now the last
step before the final demean.

## Contact

squac-help@uw.edu

## See Also

hourly_max_acc, hourly_noise_floor_bp_acc

## Updated

2026-08-28
