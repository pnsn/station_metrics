# hourly_noise_floor_acc

Noise Floor of Highpassed Acceleration

## Summary

This metric approximates the median envelope amplitude, or noise floor, of a
channel's ground acceleration over the analysis window, using data that has
been sensitivity corrected, converted to acceleration and highpassed at
0.075 Hz. It is computed as half the range between the 2nd and 98th percentile
of the samples, and reported in cm/s^2.

## Uses

This is the workhorse metric for identifying a station that has become noisy.
Trimming the distribution at the 2nd and 98th percentile keeps earthquakes,
calibration pulses and one-off spikes from dominating a number that is meant to
describe the quiet background, so the value tracks the persistent noise level
rather than the loudest thing that happened. A gradual rise over days or weeks
usually means a failing sensor, a loose or corroding connection, or a change in
the site environment such as new construction. A sudden step usually means a
hardware or configuration change.

## Data Analyzed

Traces - one N.S.L.C (Network.Station.Location.Channel) per measurement. Where
the channel has gaps, each segment is processed separately and the resulting
samples are pooled before the percentiles are taken.

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
4. Divide by the channel's overall sensitivity from the metadata.
5. Convert to acceleration. A channel whose second SEED code letter is N is
   already an accelerometer; anything else is differentiated from velocity.
6. Apply a causal Butterworth highpass at 0.075 Hz with 2 corners.
7. Cut the trace to the analysis window and remove the mean again.
8. Pool the samples from all segments into one series a of length n, in m/s^2,
   and sort it ascending.
9. Take the values at the 2nd and 98th percentile positions:

   a2  = sorted_a[int(0.02 * n)]
   a98 = sorted_a[int(0.98 * n)]

10. Report half their difference, converted to cm/s^2:

   hourly_noise_floor_acc = 100 * (a98 - a2) / 2

## Metric Values Returned

value - approximate noise floor of the highpassed acceleration (cm/s^2).

starttime - beginning of the reporting hour (UTC).

endtime - end of the reporting hour (UTC).

channel - the channel analyzed, as N.S.L.C.

## Threshold

0.2 cm/s^2.

## Notes

The percentiles are taken on the signed trace, not on its absolute value. For a
demeaned, roughly symmetric noise record the 2nd percentile is negative and the
98th is positive, so half their difference is a sensible amplitude scale. On a
badly asymmetric record, for instance one with a large one-sided glitch, the
number is less meaningful.

The percentile positions are found by integer indexing into the sorted array
rather than by interpolation, which is adequate given the hundreds of thousands
of samples in an hour.

This is not a true median envelope and should not be compared numerically
against one; it is a fast approximation that behaves consistently for the same
channel over time, which is what matters for trend detection.

Because this uses a highpass rather than a bandpass, it includes all energy
above 0.075 Hz, which makes it more sensitive than hourly_noise_floor_bp_acc to
high frequency instrument noise.

## Change Log

Aug 2026: the processing order changed. Previously the trace was cut to the
analysis window before integration or differentiation and before filtering, so
the filter transient fell inside the measured window. Cutting is now the last
step before the final demean.

## Contact

squac-help@uw.edu

## See Also

hourly_noise_floor_bp_acc, hourly_max_acc, power_1Hz

## Updated

2026-08-28
