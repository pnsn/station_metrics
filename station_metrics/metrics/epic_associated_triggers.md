# epic_associated_triggers

EPIC Associated Triggers Per Hour

STATUS: PLACEHOLDER. This metric is produced outside the station_metrics
repository. The algorithm section needs to be completed by whoever maintains
the producing code.

## Summary

This metric reports the number of hourly triggers from EPIC for a channel that
were associated with an event.

## Uses

These are the triggers that did their job: they were produced by the channel
and were successfully tied to a real event by the associator. Watched against
the unassociated count, the ratio describes how useful a channel's trigger
output actually is. An abrupt drop to zero at a station that normally
contributes is a strong signal that something has broken in the path between
the sensor and EPIC.

## Data Analyzed

Traces - one channel per measurement.

Window - one hour.

Data Source - the ShakeAlert server eew-bk-dev1. TODO: confirm the logfile and
the extraction method.

## Algorithm

TODO. Document how associated triggers are identified and attributed to a
channel and an hour.

## Metric Values Returned

value - number of associated triggers in the hour (count).

starttime - beginning of the reporting hour (UTC).

endtime - end of the reporting hour (UTC).

channel - the channel analyzed.

## Threshold

60 counts.

## Contact

squac-help@uw.edu

## See Also

epic_unassociated_triggers, epic_candidate_triggers

## Updated

2026-08-28
