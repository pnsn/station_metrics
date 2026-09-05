# epic_trigger_latency_max

Maximum EPIC Trigger Latency

STATUS: PLACEHOLDER. This metric is produced outside the station_metrics
repository. The algorithm section needs to be completed by whoever maintains
the producing code.

## Summary

This metric reports the largest EPIC trigger latency observed for a channel.

## Uses

This exposes the worst case that the median trigger latency hides. A channel
with a good median but a large maximum is producing triggers in bursts, which
typically means processing or telemetry that stalls and then catches up, and
those late triggers arrive too late to contribute to an alert even though they
eventually arrive.

## Data Analyzed

Traces - one channel per measurement.

Window - TODO.

Data Source - EPIC logfiles. TODO: confirm which server and which logfile.

## Algorithm

TODO. Document how trigger latency is defined, from what reference time it is
measured, and over what window the maximum is taken.

## Metric Values Returned

value - maximum trigger latency (seconds).

starttime - TODO.

endtime - TODO.

channel - the channel analyzed.

## Threshold

TODO.

## Contact

squac-help@uw.edu

## See Also

epic_trigger_latency_median, epic_trigger_latency_le_3.5

## Updated

2026-08-28
