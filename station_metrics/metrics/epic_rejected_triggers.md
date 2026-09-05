# epic_rejected_triggers

EPIC Rejected Triggers Per Hour

STATUS: PLACEHOLDER. This metric is produced outside the station_metrics
repository. The algorithm section needs to be completed by whoever maintains
the producing code.

## Summary

This metric reports the number of hourly triggers from EPIC for a channel that
were rejected for any reason. The final update in the EPIC logfile for a
rejected trigger carries a reason of LARGE, SMALL or RANGE.

## Uses

Every rejected trigger is work EPIC did that produced nothing, so a channel
with a high rejection count is costing the system processing without
contributing. Broken down by rejection reason, the counts also diagnose the
cause: RANGE rejections point at amplitudes outside physically plausible
bounds, which usually means an instrument or metadata problem rather than site
noise.

## Data Analyzed

Traces - one channel per measurement.

Window - one hour.

Data Source - EPIC logfiles. TODO: confirm which server and which logfile.

## Algorithm

TODO. Document how rejected triggers are identified in the EPIC logfiles,
including how the final update for a trigger is located and how the LARGE,
SMALL and RANGE reasons are parsed.

## Metric Values Returned

value - number of rejected triggers in the hour (count).

starttime - beginning of the reporting hour (UTC).

endtime - end of the reporting hour (UTC).

channel - the channel analyzed.

## Threshold

TODO.

## Contact

squac-help@uw.edu

## See Also

epic_candidate_triggers, epic_temporary_3sec_triggers

## Updated

2026-08-28
