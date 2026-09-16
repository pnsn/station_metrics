# epic_rejected_triggers

Hourly Count of EPIC Triggers Rejected by Quality Checks

## Summary

This metric reports the number of triggers the EPIC early warning algorithm
declared on a channel during the hour whose final status shows they were
rejected by EPIC's quality checks, that is, a final status containing LARGE,
SMALL or RANGE. It is read from the log files of an EPIC instance on
eew-uw-rei, not calculated from archived waveforms.

## Uses

A rejected trigger is one EPIC spent effort on and then threw away. A steady
stream of them points to a station problem: glitches, spikes, telemetry
dropouts, or amplitudes outside the range EPIC considers plausible for real
ground motion. Comparing this count with epic_candidate_triggers shows what
fraction of a station's trigger load is junk, and epic_temporary_3sec_triggers
shows how many of those rejects looked real for long enough to matter.

## Data Analyzed

Log lines - EPIC log lines for one N.S.L.C (Network.Station.Location.Channel)
per measurement. Four line types are used: N: (a new trigger), U: (an update to
that trigger's status), E:I:T: (the trigger was associated with an event), and
S: (the periodic station status line, used only to decide which hours the
station was being analyzed). The "M: Adding station" line is also used for
stations added part way through a day.

Window - the clean UTC hour. Each trigger is assigned to the hour that contains
its trigger (pick) time, not the hour in which its log lines were written.

Data Source - the daily EPIC log files (epic_YYYYMMDD.log) of an EPIC instance
running on eew-uw-rei. This instance mirrors the production EPIC configuration,
and is used by ShakeAlert staff to check the station quality of new or upgraded
stations for the purposes of station acceptance into ShakeAlert. Its channel
file is therefore larger than production's: it also includes candidate and
suspended stations. Nothing is read from an archive.

SEED Channel Types - vertical component channels (channel code ending in Z)
that are in the eew-uw-rei EPIC channel file and have a channel id in the SQUAC
channel map.

## Algorithm

1. Read the daily EPIC log files for the requested days.
2. Group the log lines into triggers. A trigger is identified by its network,
   station, location, channel and trigger time. An N: line starts a trigger and
   records its first status; each later U: line for the same trigger records
   its new status; an E:I:T: line with an event count greater than zero records
   the status "associated". U: and E:I:T: lines with no matching N: line in the
   same log file are ignored.
3. Discard triggers whose trigger time falls before the first requested day.
4. Take each trigger's final status to be the last status recorded for it.
   Count the trigger as rejected if that final status contains any of the
   strings LARGE, SMALL or RANGE.
5. Assign each trigger to the UTC hour containing its trigger time.
6. For every hour in which the channel was present, count the rejected
   triggers assigned to that hour. A channel is present in an hour that
   contains an S: line for it, a trigger on it, or, for a station added part
   way through the day, its "M: Adding station" line. A present hour with no
   rejected triggers is reported as 0.

## Metric Values Returned

value - number of rejected EPIC triggers on the channel in the hour.

starttime - beginning of the hour (UTC).

endtime - end of the hour (UTC).

channel - the channel analyzed, as N.S.L.C.

## Threshold

10

## Notes

The match on LARGE, SMALL and RANGE is a substring match, so any status
containing one of those words counts.

Rejection is decided before lateness. A rejected trigger is counted here even
if its latency was over 120 s, and is never counted as late.

Only the final status matters. A trigger that was rejected and then updated to
some other status by a later U: line is not counted here.

A 0 means the channel was being analyzed and produced no rejected triggers. No
measurement at all means the channel was not being analyzed that hour, or the
log file for that day was missing.

A trigger whose log lines straddle midnight is split across two log files. Only
the lines in the file holding its N: line are used, so its final status is the
last one written before midnight.

## Change Log

Sep 16 2026: first full documentation of this metric. The page was previously a
placeholder.

## Contact

squac-help@uw.edu

## See Also

epic_candidate_triggers, epic_temporary_3sec_triggers,
approximate_epic_triggers

## Updated

2026-09-14

