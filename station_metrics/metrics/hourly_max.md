# hourly_max

Maximum Raw Sample Value

## Summary

This metric reports the largest raw sample value seen on a channel during the
analysis window, in digital counts, with no gain correction, filtering or
detrending applied.

## Uses

Because the value is uncorrected it speaks directly to the state of the
digitizer. A value pinned at the positive end of the digitizer's range, for
example near 2^23 for a 24 bit system, means the channel clipped during the
hour, and any ground motion metric computed for that hour is suspect. A value
that is identically zero across many consecutive hours usually means a dead
channel. Read alongside hourly_min it shows whether the signal sits centred in
the digitizer's range or rides near one rail.

## Data Analyzed

Traces - one N.S.L.C (Network.Station.Location.Channel) per measurement. Where
the channel has gaps, the samples from all segments in the window are pooled
into a single series before the maximum is taken.

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
4. Report the maximum:

   hourly_max = max(x)

## Metric Values Returned

value - largest raw sample value in the window (digital counts).

starttime - beginning of the reporting hour (UTC).

endtime - end of the reporting hour (UTC).

channel - the channel analyzed, as N.S.L.C.

## Threshold

1e9 counts.

## Notes

The measurement window is 3605.05 s while the start and end times reported to
SQUAC are the clean hour. The 5.05 s of extra data at the front can in
principle contribute the extreme value.

Where a channel has gaps, samples from separate segments are concatenated
without regard for the time between them. That is harmless for a maximum, which
does not depend on sample ordering.

## Change Log

Aug 2026: no change to the calculation. This metric has always been taken from
the untouched raw trace.

## Contact

squac-help@uw.edu

## See Also

hourly_min, hourly_mean, hourly_range

## Updated

2026-08-28
