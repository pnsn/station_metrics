# hourly_range

Range of Raw Sample Values

## Summary

This metric reports the difference between the largest and smallest raw sample
values seen on a channel during the analysis window, in digital counts, with no
gain correction, filtering or detrending applied.

## Uses

This is the simplest available measure of how much of the digitizer's dynamic
range a channel is actually using. A value approaching the digitizer's full
range, for example 2^24 for a 24 bit system, means the channel clipped during
the hour and every ground motion metric for that hour should be treated with
suspicion. A value of zero means the channel is flatlined, producing a constant
value rather than no data at all, which is a failure mode that completeness
metrics will not catch.

## Data Analyzed

Traces - one N.S.L.C (Network.Station.Location.Channel) per measurement. Where
the channel has gaps, the samples from all segments in the window are pooled
into a single series before the range is taken.

Window - the analysis window, running from 5.05 s before the top of the hour to
the end of the hour, 3605.05 s in total. The 5.05 s lead-in is the STA (0.05 s)
plus LTA (5.0 s) of the trigger function used by other metrics.

Data Source - FDSN dataselect from the permanent archive: EarthScope/IRIS DMC
for PNSN data, NCEDC for NCSN data, SCEDC for SCSN data.

SEED Channel Types - ?H? and ?N? (high gain broadband and accelerometer), as
listed in the ShakeAlert channel file.

## Algorithm

1. Request the analysis window plus 120 s of padding on each side for a single
   N.S.L.C from the archive's FDSN dataselect service.
2. Cut each returned trace to the analysis window. No detrending, gain removal
   or filtering is applied.
3. Concatenate the samples from all segments in the window into one series x.
4. Report the peak to peak range:

   hourly_range = max(x) - min(x)

## Metric Values Returned

value - peak to peak range of the raw samples in the window (digital counts).

starttime - beginning of the reporting hour (UTC).

endtime - end of the reporting hour (UTC).

channel - the channel analyzed, as N.S.L.C.

## Threshold

2e9 counts.

## Notes

Because the range includes any DC offset excursion as well as genuine ground
motion, a station whose mean is drifting will show a larger range than one that
is stable at the same noise level. hourly_mean is what separates those two
cases.

The measurement window is 3605.05 s while the start and end times reported to
SQUAC are the clean hour.

## Change Log

Aug 2026: no change to the calculation. This metric has always been taken from
the untouched raw trace.

## Contact

squac-help@uw.edu

## See Also

hourly_min, hourly_max, hourly_mean

## Updated

2026-08-28
