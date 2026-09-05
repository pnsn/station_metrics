# rms_above_.07

Duration of Highpassed Acceleration RMS Above 0.07 cm/s^2

## Summary

This metric reports the total number of seconds during the analysis window that
a five second sliding window RMS of ground acceleration, highpassed at
0.075 Hz, stays above 0.07 cm/s^2. 0.07 cm/s^2 is the 2018 ShakeAlert station
acceptance threshold.

## Uses

This is a duration rather than a count, which makes it the right tool for
finding stations that are persistently too noisy to be useful for early warning
as opposed to stations that occasionally spike. A station sitting near a
compressor or a busy road will accumulate hundreds or thousands of seconds an
hour here while its peak amplitude metrics look unremarkable. Because it is a
total, one long noisy stretch and many short bursts produce the same number, so
it should be read alongside the spike counting metrics when diagnosing the
cause.

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
4. Apply a causal Butterworth highpass at 0.075 Hz with 2 corners.
5. Cut the trace to the analysis window, discarding the padding along with the
   filter start-up transient, and remove the mean again.
6. Pool the samples from all segments into one series a, in m/s^2.
7. Square the series, smooth it with a centred boxcar 5 s long, and take the
   square root to give a sliding window RMS at every sample:

   RMS(n) = sqrt( mean( a[n - 2.5s : n + 2.5s]^2 ) )

8. Count the samples of the RMS function above the threshold and convert to
   seconds by multiplying by the sample interval:

   rms_above_.07 = count( RMS > 0.0007 m/s^2 ) * delta

## Metric Values Returned

value - seconds during the window that the RMS exceeded 0.07 cm/s^2, or -1 if
the returned trace was shorter than the 5 s RMS window.

starttime - beginning of the reporting hour (UTC).

endtime - end of the reporting hour (UTC).

channel - the channel analyzed, as N.S.L.C.

## Threshold

60.0 seconds.

## Notes

The RMS window is centred on each sample rather than trailing it, so the
reported duration is symmetric about the noisy interval and extends
approximately 2.5 s either side of it.

A value of -1 means the measurement could not be made because the trace was
shorter than 5 s. It is uploaded rather than withheld, because withholding a
value would be ambiguous between "no data existed", "the channel was not
analyzed this hour" and "the trace was too short".

Since the measurement window is 3605.05 s rather than 3600 s, the maximum
possible value is slightly above 3605 rather than 3600.

Where a channel has gaps, samples from separate segments are concatenated
before the RMS is computed, so the smoothing window straddles the join. This
can create a small artificial excursion at each gap.

## Change Log

Aug 2026: the processing order changed. Previously the trace was cut to the
analysis window before differentiation and filtering, so the filter start-up
transient fell inside the measured window and could push the RMS above
threshold in the first seconds of every hour.

## Contact

squac-help@uw.edu

## See Also

rms_bp_above_.07, hourly_noise_floor_acc, acc_spikes_gt_.34

## Updated

2026-08-28
