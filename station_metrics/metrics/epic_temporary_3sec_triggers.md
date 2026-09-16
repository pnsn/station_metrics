# epic_temporary_3sec_triggers

Hourly Count of Rejected EPIC Triggers That Were Valid for at Least 3 Seconds

## Summary

This metric reports the number of rejected EPIC triggers on a channel during
the hour that spent at least 3 s continuously in a valid state (WAITING,
UNASSOC or NO_ZCOMP) before being rejected. These are triggers that looked
real for a while before failing EPIC's quality checks. It is read from the log
files of an EPIC instance on eew-uw-rei, not calculated from archived
waveforms.

## Uses

A trigger rejected immediately does little harm. A trigger that stays valid for
several seconds is available to the associator during that time and can
contribute to, or even start, a false event before it is thrown out. This
metric isolates that more dangerous subset of epic_rejected_triggers, and a
station producing many of them deserves attention even if its total reject
count looks modest.

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
   the status "associated". Every status is stored together with the wall
   clock time its log line was written. U: and E:I:T: lines with no matching N:
   line in the same log file are ignored.
3. Discard triggers whose trigger time falls before the first requested day.
4. Keep only rejected triggers: those whose final (last recorded) status
   contains LARGE, SMALL or RANGE.
5. Walk through each rejected trigger's statuses in order. A valid window opens
   at the first status that is WAITING, UNASSOC or NO_ZCOMP, and closes at the
   next status that is not one of those three. Its length is

   window_length = (log time of closing line) - (log time of opening line)

   Keep the longest such window for the trigger.
6. Count the trigger if its longest valid window is 3 s or more.
7. Assign each trigger to the UTC hour containing its trigger time.
8. For every hour in which the channel was present, report the count for that
   hour. A channel is present in an hour that contains an S: line for it, a
   trigger on it, or, for a station added part way through the day, its
   "M: Adding station" line. A present hour with no such triggers is reported
   as 0.

## Metric Values Returned

value - number of rejected EPIC triggers on the channel in the hour that were
valid for at least 3 s.

starttime - beginning of the hour (UTC).

endtime - end of the hour (UTC).

channel - the channel analyzed, as N.S.L.C.

## Threshold

10

## Notes

This count is a subset of epic_rejected_triggers and can never exceed it.

The comparison is inclusive, so a window of exactly 3 s counts.

Time spent valid is measured from log line to log line, so it is only as fine
as the spacing of the status updates EPIC writes. A trigger rejected on its N:
line has a valid window of zero.

The 3 s window is a setting of the parsing script (--temp-window, default 3).
The metric name assumes the default, so uploads should always be made with it.

A trigger whose log lines straddle midnight is split across two log files. Only
the lines in the file holding its N: line are used.

## Change Log

Sep 16 2026: first full documentation of this metric. The page was previously a
placeholder.

## Contact

squac-help@uw.edu

## See Also

epic_rejected_triggers, epic_candidate_triggers

## Updated

2026-09-14

