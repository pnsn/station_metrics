# epic_temporary_3sec_triggers

EPIC Triggers Valid For At Least 3 Seconds Before Rejection

STATUS: PLACEHOLDER. This metric is produced outside the station_metrics
repository. The algorithm section needs to be completed by whoever maintains
the producing code.

## Summary

This metric reports the number of hourly triggers from EPIC for a channel that
remained valid for at least three seconds before being rejected, where the
final logfile update carries a rejection reason of LARGE, SMALL or RANGE.

## Uses

A trigger that survives three seconds has already had time to influence EPIC's
solution before being thrown out, so these cost considerably more than triggers
rejected immediately. This metric therefore isolates the most damaging subset
of a channel's bad triggers, and is the right one to watch when a station is
suspected of degrading alerts rather than merely wasting processing.

## Data Analyzed

Traces - one channel per measurement.

Window - one hour.

Data Source - EPIC logfiles. TODO: confirm which server and which logfile.

## Algorithm

TODO. Document how the lifetime of a trigger is measured from the EPIC
logfiles, and how the three second threshold is applied.

## Metric Values Returned

value - number of triggers valid for at least 3 s before rejection (count).

starttime - beginning of the reporting hour (UTC).

endtime - end of the reporting hour (UTC).

channel - the channel analyzed.

## Threshold

TODO.

## Contact

squac-help@uw.edu

## See Also

epic_candidate_triggers, epic_rejected_triggers

## Updated

2026-08-28
