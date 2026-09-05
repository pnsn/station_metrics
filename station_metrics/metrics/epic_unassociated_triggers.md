# epic_unassociated_triggers

EPIC Unassociated Triggers Per Hour

STATUS: PLACEHOLDER. This metric is produced outside the station_metrics
repository. The algorithm section needs to be completed by whoever maintains
the producing code.

## Summary

This metric reports the number of hourly triggers from EPIC for a channel that
were not associated with any event.

## Uses

An unassociated trigger is one the channel produced that no event could be
found for, so a high rate means the channel is feeding EPIC noise. This is the
most direct measure of a station's nuisance contribution to the early warning
system, and a sustained rise is usually grounds for investigating the station
or removing it from the trigger stream.

## Data Analyzed

Traces - one channel per measurement.

Window - one hour.

Data Source - the ShakeAlert server eew-bk-dev1. TODO: confirm the logfile and
the extraction method.

## Algorithm

TODO. Document how unassociated triggers are identified and attributed to a
channel and an hour.

## Metric Values Returned

value - number of unassociated triggers in the hour (count).

starttime - beginning of the reporting hour (UTC).

endtime - end of the reporting hour (UTC).

channel - the channel analyzed.

## Threshold

60 counts.

## Contact

squac-help@uw.edu

## See Also

epic_associated_triggers, epic_candidate_triggers

## Updated

2026-08-28
