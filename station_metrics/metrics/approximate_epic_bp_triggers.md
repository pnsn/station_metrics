# approximate_epic_bp_triggers

Approximate ElarmS3/EPIC Trigger Count, Bandpassed

## Summary

This metric approximates the number of triggers the ElarmS3/EPIC early warning
algorithm would have declared on a channel during the analysis window, using
archived data. Candidate triggers come from an STA/LTA on velocity highpassed
at 3 Hz, and are then filtered by amplitude gates on acceleration, velocity and
displacement bandpassed between 0.075 Hz and 15 Hz, and by a boxcar test that
rejects DC steps. The implementation follows A. I. Chung et al., SRL
March/April 2019.

## Uses

This estimates a station's contribution to EPIC's trigger load using amplitudes
measured in the 0.075 - 15 Hz band rather than the full band above 0.075 Hz.
Comparing it against the highpassed version shows how much of a station's
trigger production is driven by energy above 15 Hz, which is rarely genuine
ground motion and usually indicates electronics or digitizer trouble. It is
deliberately an approximation: it uses a single channel's archived data and
knows nothing about the state of the running EPIC system, so it should be read
as a station health indicator rather than a prediction of EPIC's actual output.

## Data Analyzed

Traces - one N.S.L.C (Network.Station.Location.Channel) per measurement, from
which four separately filtered series are derived: a trigger function, and
acceleration, velocity and displacement for the amplitude gates. Where the
channel has gaps, each segment is processed separately and the resulting
samples are pooled.

Window - the analysis window, running from 5.05 s before the top of the hour to
the end of the hour, 3605.05 s in total. The 5.05 s lead-in is the STA plus LTA
of the trigger function and exists so the STA/LTA has converged before the hour
begins. Waveforms are requested with a further 120 s of padding on each side,
which is used during processing and then discarded.

Data Source - FDSN dataselect from the permanent archive: EarthScope/IRIS DMC
for PNSN data, NCEDC for NCSN data, SCEDC for SCSN data. Instrument metadata is
requested at response level from the same archive.

SEED Channel Types - ?H? and ?N? (high gain broadband and accelerometer),
vertical components, as listed in the ShakeAlert channel file.

## Algorithm

1. Request the analysis window plus 120 s of padding on each side, for a single
   N.S.L.C, along with the channel's response level metadata.
2. Build three amplitude traces from the same raw data. For each of
   acceleration, velocity and displacement: detrend the padded trace with a
   third-order polynomial, remove the mean, divide by the channel's overall
   sensitivity, integrate or differentiate to the required ground motion type,
   apply a causal Butterworth bandpass from 0.075 Hz to 15 Hz with 2 corners,
   cut to the analysis window, and remove the mean again. Call these a (m/s^2),
   v (m/s) and d (m).
3. Build the trigger trace independently: same preparation, converted to
   velocity and highpassed at 3 Hz.
4. Run a classic STA/LTA over the trigger trace with a short term window of
   0.05 s and a long term window of 5.0 s.
5. Reduce the STA/LTA function to a two-state series, 1 where it reaches 20 and
   0 elsewhere, and take every upward step as one candidate trigger.
6. Apply the amplitude gates. In a 4 s window beginning 0.05 s before the
   candidate, measure the peak absolute acceleration, velocity and
   displacement. Discard the candidate unless all of the following hold:

   peak |a| > 3.1623e-5 m/s^2                  (0.0031623 cm/s^2)
   3.1623e-8 m/s   < peak |v| < 10 m/s
   3.1623e-8 m     < peak |d| < 31.623 m

7. Apply the boxcar test. In a 0.1 s window beginning 0.1 s after the
   candidate, measure the signed peak to peak range max(x) - min(x) of the
   channel's native ground motion: acceleration for a channel whose second
   SEED code letter is N, velocity for one whose second letter is H. Discard
   the candidate if that range is below 2.2e-5 m/s^2 for an accelerometer or
   2.2e-8 m/s for a broadband.
8. Apply a dead time: discard any surviving candidate that falls within 10 s of
   the previous candidate that was counted.
9. Report the number of candidates that survive all three tests.

## Metric Values Returned

value - approximate number of EPIC triggers in the window, or -1 if the
returned trace was shorter than the 10 s dead time.

starttime - beginning of the reporting hour (UTC).

endtime - end of the reporting hour (UTC).

channel - the channel analyzed, as N.S.L.C.

## Threshold

60 counts.

## Notes

On channels sampled at or below 30 samples per second the 15 Hz upper corner
sits at or above the Nyquist frequency, so ObsPy clamps the filter and this
metric becomes equivalent to the highpassed version.

The trigger function is identical to the one used by the highpassed version, so
both metrics examine exactly the same set of candidate onsets and differ only
in which candidates pass the amplitude gates and the boxcar test.

The number of candidates rejected by the boxcar test is calculated alongside
this metric and printed to the run log, but is not uploaded to SQUAC.

A value of -1 means the trace was shorter than the 10 s dead time. It is
uploaded rather than withheld, because withholding would be ambiguous.

## Change Log

Aug 2026: the boxcar test was previously applied to rectified data, measuring
max(|x|) - min(|x|), and now measures the signed range max(x) - min(x). Counts
from before and after this change are not directly comparable and should be
expected to rise.

Aug 2026: the processing order changed. Previously the trace was cut to the
analysis window before integration, differentiation and filtering.

Aug 2026: the previous documentation stated that the STA/LTA trigger trace was
highpassed at 0.075 Hz. The STA/LTA trigger trace is highpassed at 3 Hz; only
the amplitude gates use the 0.075 - 15 Hz band.

## Contact

squac-help@uw.edu

## See Also

approximate_epic_triggers, acc_bp_spikes_gt_.34

## Updated

2026-08-28
