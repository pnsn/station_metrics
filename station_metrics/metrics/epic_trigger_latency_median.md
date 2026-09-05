# epic_trigger_latency_median

Median EPIC Trigger Latency

STATUS: PLACEHOLDER. This metric is produced outside the station_metrics
repository. The algorithm section needs to be completed by whoever maintains
the producing code.

## Summary

This metric reports the median latency of the EPIC triggers produced by a
channel.

## Uses

Where wave ring latency describes how fast a channel's raw data arrives, this
describes how fast the resulting triggers become available to the associator,
which includes the processing time on top of the telemetry time. A median
rather than a mean is used so that a single very late trigger does not distort
the picture of typical performance.

## Data Analyzed

Traces - one channel per measurement.

Window - TODO.

Data Source - EPIC logfiles. TODO: confirm which server and which logfile.

## Algorithm

TODO. Document how trigger latency is defined, from what reference time it is
measured, and over what window the median is taken.

## Metric Values Returned

value - median trigger latency (seconds).

starttime - TODO.

endtime - TODO.

channel - the channel analyzed.

## Threshold

TODO.

## Contact

squac-help@uw.edu

## See Also

epic_trigger_latency_le_3.5, epic_trigger_latency_max

## Updated

2026-08-28
