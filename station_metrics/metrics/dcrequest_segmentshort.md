# dcrequest_segmentshort

Shortest Continuous Data Segment in the Hour

## Summary

This metric reports the duration in seconds of the shortest continuous data
segment returned by the archive's FDSN dataselect service for one hour of a
single channel.

## Uses

On a healthy channel the hour arrives as a single segment and this value is
close to 3600 s. A small value means the hour arrived broken into pieces, which
is characteristic of a marginal telemetry link, a datalogger that is resetting,
or a buffering problem upstream of the archive. Because it reports the worst
single fragment rather than an average, it is sensitive to a single bad patch
in an otherwise good hour.

## Data Analyzed

Traces - one N.S.L.C (Network.Station.Location.Channel) per measurement.

Window - the reporting hour, from the requested start time to one hour later.

Data Source - FDSN dataselect from the permanent archive: EarthScope/IRIS DMC
for PNSN data, NCEDC for NCSN data, SCEDC for SCSN data.

SEED Channel Types - ?H? and ?N? (high gain broadband and accelerometer), as
listed in the ShakeAlert channel file.

## Algorithm

1. Request one hour of data plus lead-in and padding for a single N.S.L.C from
   the archive's FDSN dataselect service.
2. Cut every returned trace to the reporting hour, from the start time to the
   start time plus 3600 s.
3. For each cut segment compute its duration as the number of samples times the
   sample interval:

   segment duration = npts * delta

4. Report the smallest of those durations:

   dcrequest_segmentshort = min(segment durations)

## Metric Values Returned

value - duration in seconds of the shortest segment in the reporting hour.

starttime - beginning of the reporting hour (UTC).

endtime - end of the reporting hour (UTC).

channel - the channel analyzed, as N.S.L.C.

## Threshold

1.0 second.

## Notes

Segments are clipped to the reporting hour before being measured, so the first
and last segments of an hour are shortened by the clip. On a channel returned
as one continuous piece, that clipping means this metric and the longest
segment metric are both approximately 3600 s rather than the full length of the
underlying archived segment.

Segments with a single sample or fewer are discarded before this measurement is
made, so a stray one-sample record does not drive the value to near zero.

A channel with no data at all in the hour produces no segments; the value
reported in that case is the sentinel 9e6, which should be read as "not
measured".

## Change Log

Aug 2026: previously measured over the 3605.05 s analysis window rather than
the reporting hour.

## Contact

squac-help@uw.edu

## See Also

dcrequest_segmentlong, dcrequest_ngaps, dcrequest_pctavailable

## Updated

2026-08-28
