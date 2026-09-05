# acc_spikes_gt_.34

Highpassed Acceleration Spikes Above 0.34 cm/s^2

## Summary

This metric counts the number of times during the analysis window that an
STA/LTA trigger function crosses a ratio of 20 and is backed up by an absolute
ground acceleration above 0.34 cm/s^2 on data highpassed at 0.075 Hz.
0.34 cm/s^2 is the 2018 ShakeAlert station acceptance threshold.

## Uses

Requiring both a sharp onset and a large amplitude makes this a good detector
of impulsive events. On a healthy station in an ordinary hour it should be zero.
A station producing several every hour is generating impulsive spikes that
would waste the early warning system's attention, and the cause is usually
mechanical: a sensor component that is not pivoting freely, a mass recentring,
a loose cable, or animals and machinery at the site. A count that jumps on all
channels of an instrument and at several nearby stations at the same time is
much more likely to be a real earthquake.

## Data Analyzed

Traces - one N.S.L.C (Network.Station.Location.Channel) per measurement, plus a
separately filtered copy of the same channel used to build the trigger
function. Where the channel has gaps, each segment is processed separately and
the resulting samples are pooled into one series.

Window - the analysis window, running from 5.05 s before the top of the hour to
the end of the hour, 3605.05 s in total. The 5.05 s lead-in is the STA plus LTA
of the trigger function and exists so the STA/LTA has converged before the hour
begins. Waveforms are requested with a further 120 s of padding on each side,
which is used during processing and then discarded.

Data Source - FDSN dataselect from the permanent archive: EarthScope/IRIS DMC
for PNSN data, NCEDC for NCSN data, SCEDC for SCSN data. Instrument metadata is
requested at response level from the same archive.

SEED Channel Types - ?H? and ?N? (high gain broadband and accelerometer), as
listed in the ShakeAlert channel file.

## Algorithm

1. Request the analysis window plus 120 s of padding on each side, for a single
   N.S.L.C, along with the channel's response level metadata.
2. Build the amplitude trace. Detrend the padded trace with a third-order
   polynomial, remove the mean, divide by the channel's overall sensitivity,
   convert to acceleration, apply a causal Butterworth highpass at 0.075 Hz
   with 2 corners, cut to the analysis window and remove the mean again. Call
   the resulting series a, in m/s^2.
3. Build the trigger trace independently from the same raw data: same
   preparation, but converted to velocity and highpassed at 3 Hz rather than
   0.075 Hz. The higher corner keeps microseism and long period noise out of
   the trigger function.
4. Run a classic STA/LTA over the trigger trace with a short term window of
   0.05 s and a long term window of 5.0 s.
5. Reduce the STA/LTA function to a two-state series, 1 where it reaches 20 and
   0 elsewhere, and take every upward step as one trigger onset. A single long
   excursion above the threshold therefore produces one onset rather than one
   per sample.
6. For each onset, measure the largest absolute acceleration in a 4 s window
   beginning 0.05 s before the onset sample. Discard the onset if that peak
   does not exceed 0.0034 m/s^2, which is 0.34 cm/s^2.
7. Apply a dead time: discard any surviving onset that falls within 10 s of the
   previous onset that was counted.
8. Report the number of onsets that survive both tests.

## Metric Values Returned

value - number of qualifying spikes in the window, or -1 if the returned trace
was shorter than the 10 s dead time.

starttime - beginning of the reporting hour (UTC).

endtime - end of the reporting hour (UTC).

channel - the channel analyzed, as N.S.L.C.

## Threshold

1 count.

## Notes

The trigger function and the amplitude test deliberately use different filter
bands. The trigger function is built from velocity highpassed at 3 Hz to make
it sensitive to sharp onsets, while the amplitude test uses acceleration
highpassed at 0.075 Hz so that the amplitude being compared to the ShakeAlert
threshold is the full broadband ground motion.

The 4 s measurement window begins slightly before the onset, by the length of
the short term average, because the STA/LTA reports a crossing after the energy
has already begun to rise.

A value of -1 means the trace was shorter than the 10 s dead time. It is
uploaded rather than withheld, because withholding would be ambiguous between
"no data existed", "the channel was not analyzed" and "the trace was too
short".

Where a channel has gaps, samples from separate segments are concatenated
before the STA/LTA is applied, so an artificial step exists at each join. The
STA/LTA is computed per segment and zeroed for segments shorter than the STA
plus LTA, which limits but does not entirely remove spurious triggers at joins.

## Change Log

Aug 2026: the processing order changed. Previously the trace was cut to the
analysis window before differentiation and filtering, so the filter start-up
transient fell inside the measured window and could trigger at the start of
every hour.

## Contact

squac-help@uw.edu

## See Also

acc_bp_spikes_gt_.34, acc_gt_2.0, approximate_epic_triggers

## Updated

2026-08-28
