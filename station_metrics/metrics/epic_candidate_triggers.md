# epic_candidate_triggers

EPIC Candidate Triggers Per Hour

STATUS: PLACEHOLDER. This metric is produced outside the station_metrics
repository. The algorithm section needs to be completed by whoever maintains
the producing code.

## Summary

This metric reports the number of hourly triggers from EPIC for a channel,
counting every trigger regardless of whether it was eventually rejected or was
never associated with an event.

## Uses

This is the raw trigger production rate of a channel before any of EPIC's
quality filtering is applied, so it measures the total load the channel places
on the system. Read against the rejected and associated counts, it shows what
fraction of a channel's output is useful: a channel with a high candidate count
and almost no associated triggers is feeding EPIC noise.

## Data Analyzed

Traces - one channel per measurement.

Window - one hour.

Data Source - EPIC logfiles. TODO: confirm which server and which logfile.

## Algorithm

TODO. Document how triggers are extracted from the EPIC logfiles and how a
trigger is attributed to an hour.

## Metric Values Returned

value - number of candidate triggers in the hour (count).

starttime - beginning of the reporting hour (UTC).

endtime - end of the reporting hour (UTC).

channel - the channel analyzed.

## Threshold

TODO.

## Contact

squac-help@uw.edu

## See Also

epic_rejected_triggers, epic_temporary_3sec_triggers,
epic_associated_triggers, epic_unassociated_triggers

## Updated

2026-08-28
