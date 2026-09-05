# hourly_max_acc

Maximum Highpassed Ground Acceleration

## Summary

This metric reports the largest absolute ground acceleration observed on a
channel during the analysis window, from data that has been sensitivity
corrected, converted to acceleration, and highpassed at 0.075 Hz. The result is
in cm/s^2.

## Uses

Being a single peak, this value is set by whatever the largest excursion in the
hour was: a real earthquake, a calibration pulse, a vehicle passing the vault,
or an instrument glitch. It is used both to spot felt shaking and, more often,
to spot channels producing implausibly large accelerations hour after hour,
which indicates an instrument or metadata problem rather than ground motion. A
value much larger than the same channel's bandpassed peak means the energy sits
above 15 Hz, which is rarely genuine ground motion.

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
2. Detrend the padded trace with a third-order polynomial. This removes slow
   instrument drift that differentiation or integration would otherwise
   amplify.
3. Remove the mean.
4. Divide by the channel's overall sensitivity from the metadata. Only the gain
   is removed; the full instrument response is not deconvolved.
5. Convert to acceleration. A channel whose second SEED code letter is N is
   already an accelerometer and is left alone; anything else is treated as a
   velocity sensor and is differentiated.
6. Apply a causal Butterworth highpass at 0.075 Hz with 2 corners. The filter
   is causal because ShakeAlert's real time processing is causal.
7. Cut the trace to the analysis window, discarding the padding along with the
   filter start-up transient it absorbed.
8. Remove the mean again.
9. Pool the samples from all segments into one series a, in m/s^2, and report
   the largest absolute value converted to cm/s^2:

   hourly_max_acc = 100 * max(|a|)

## Metric Values Returned

value - largest absolute acceleration in the window (cm/s^2).

starttime - beginning of the reporting hour (UTC).

endtime - end of the reporting hour (UTC).

channel - the channel analyzed, as N.S.L.C.

## Threshold

2.0 cm/s^2.

## Notes

The order of operations matters and is deliberate. Filtering before cutting
means the filter's start-up transient lands in the 120 s of padding and is
thrown away, rather than contaminating the first seconds of the measured
window. The same is true of the drift introduced when a velocity channel is
differentiated or an accelerometer is integrated for other metrics.

Only the sensitivity is removed, not the full response, so the conversion to
physical units is accurate in the passband of the instrument and progressively
less accurate towards its corners. For the frequencies these metrics care about
that approximation is acceptable and is far faster than a full deconvolution.

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

hourly_max_bp_acc, hourly_noise_floor_acc, acc_gt_2.0

## Updated

2026-08-28
