# epic_trigger_latency_le_3.5

Percentage of EPIC Triggers Within 3.5 Seconds

STATUS: PLACEHOLDER. This metric is produced outside the station_metrics
repository. The algorithm section needs to be completed by whoever maintains
the producing code.

## Summary

This metric reports the percentage of EPIC triggers from a channel that had a
latency of 3.5 seconds or less.

## Uses

3.5 s is the working threshold for a measurement being useful to ShakeAlert.
Where the median trigger latency describes typical performance, this describes
reliability: what fraction of a channel's triggers actually arrived in time to
contribute to an alert. A channel with an acceptable median but a poor
percentage here has a long tail in its latency distribution.

## Data Analyzed

Traces - one channel per measurement.

Window - TODO.

Data Source - EPIC logfiles. TODO: confirm which server and which logfile.

## Algorithm

TODO. Document how trigger latency is defined, from what reference time it is
measured, and whether the comparison at exactly 3.5 s is inclusive.

## Metric Values Returned

value - percentage of triggers with latency of 3.5 s or less.

starttime - TODO.

endtime - TODO.

channel - the channel analyzed.

## Threshold

TODO.

## Contact

squac-help@uw.edu

## See Also

epic_trigger_latency_median, epic_trigger_latency_max

## Updated

2026-08-28
