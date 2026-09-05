# dcrequest_segmentlong

Longest Continuous Data Segment in the Hour

## Summary

This metric reports the duration in seconds of the longest continuous data
segment returned by the archive's FDSN dataselect service for one hour of a
single channel.

## Uses

On a healthy channel the hour arrives as a single continuous segment and this
value is approximately 3600 s. A value well below 3600 while
dcrequest_pctavailable remains high means the data is nearly all present but
arrived in pieces, which points at telemetry that is dropping short intervals
rather than at a station that is down. It is the natural companion to
dcrequest_segmentshort: together they bracket how the hour was divided up.

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

4. Report the largest of those durations:

   dcrequest_segmentlong = max(segment durations)

## Metric Values Returned

value - duration in seconds of the longest segment in the reporting hour.

starttime - beginning of the reporting hour (UTC).

endtime - end of the reporting hour (UTC).

channel - the channel analyzed, as N.S.L.C.

## Threshold

3600.0 seconds.

## Notes

Segments are clipped to the reporting hour before being measured, so this value
cannot exceed roughly 3600 s no matter how long the underlying archived segment
is. Because the cut is inclusive of both endpoints and takes one extra sample,
a complete hour reads a fraction of a sample interval above 3600.

A channel with no data at all in the hour produces no segments; the value
reported in that case is 0, which should be read as "not measured".

## Change Log

Aug 2026: previously measured over the 3605.05 s analysis window, so a healthy
channel read about 3605 s rather than 3600 s. Any alerting rule tuned to the
old value needs revisiting.

## Contact

squac-help@uw.edu

## See Also

dcrequest_segmentshort, dcrequest_ngaps, dcrequest_pctavailable

## Updated

2026-08-28
