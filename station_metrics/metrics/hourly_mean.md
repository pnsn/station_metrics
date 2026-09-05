# hourly_mean

Mean Raw Sample Value

## Summary

This metric reports the arithmetic mean of the raw sample values on a channel
during the analysis window, in digital counts, with no gain correction,
filtering or detrending applied.

## Uses

On a well behaved seismometer and digitizer the mean sits at a stable offset
characteristic of that instrument. Tracking it hour to hour catches problems
that amplitude metrics miss entirely: a slow drift usually means a mass that
needs recentring or a sensor whose electronics are aging, while an abrupt jump
between hours usually means a digitizer offset change, a configuration change,
or a hardware swap that nobody logged.

## Data Analyzed

Traces - one N.S.L.C (Network.Station.Location.Channel) per measurement. Where
the channel has gaps, the samples from all segments in the window are pooled
into a single series before the mean is taken.

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
3. Concatenate the samples from all segments in the window into one series x of
   length n.
4. Report the arithmetic mean:

   hourly_mean = (1/n) * sum(x)

## Metric Values Returned

value - mean raw sample value in the window (digital counts).

starttime - beginning of the reporting hour (UTC).

endtime - end of the reporting hour (UTC).

channel - the channel analyzed, as N.S.L.C.

## Threshold

1e8 counts.

## Notes

The mean is taken over all samples present, so on a channel with gaps it is
weighted by how much data each segment contributed rather than by how much wall
clock time each covered. On a badly gapped hour the value therefore describes
the data that arrived rather than the hour as a whole.

The measurement window is 3605.05 s while the start and end times reported to
SQUAC are the clean hour.

## Change Log

Aug 2026: no change to the calculation. This metric has always been taken from
the untouched raw trace.

## Contact

squac-help@uw.edu

## See Also

hourly_min, hourly_max, hourly_range

## Updated

2026-08-28
