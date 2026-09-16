# epic_associated_triggers

Hourly Count of EPIC Triggers Associated With an Event

## Summary

This metric reports the number of triggers the EPIC early warning algorithm
declared on a channel during the hour that were associated with an event,
arrived on time, and were not rejected. It is read from the log files of an
EPIC instance on eew-uw-rei, not calculated from archived waveforms.

## Uses

Associated triggers are a station's useful contribution to EPIC: picks that
helped locate and size an event. Over quiet periods this count is small and
driven by local seismicity, so it is most informative when compared across
nearby stations over the same hours. A station that stays near zero while its
neighbors routinely contribute may have timing, polarity, gain or noise
problems that stop its triggers from fitting events. An unusually high count
can point to a station whose noise is being associated into false events.

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
4. Compute each trigger's latency from its N: line:

   latency = (wall clock time the N: line was written) - (trigger time)

   adding 86400 s if the result is negative (the N: line was written after
   midnight).
5. Take each trigger's final status to be the last status recorded for it, and
   count the trigger as associated if all of the following hold:

   final status does not contain LARGE, SMALL or RANGE
   final status is "associated"
   latency <= 120 s

6. Assign each trigger to the UTC hour containing its trigger time.
7. For every hour in which the channel was present, count the associated
   triggers assigned to that hour. A channel is present in an hour that
   contains an S: line for it, a trigger on it, or, for a station added part
   way through the day, its "M: Adding station" line. A present hour with no
   associated triggers is reported as 0.

## Metric Values Returned

value - number of associated, on-time EPIC triggers on the channel in the hour.

starttime - beginning of the hour (UTC).

endtime - end of the hour (UTC).

channel - the channel analyzed, as N.S.L.C.

## Threshold

10 counts.

## Notes

An associated trigger with a latency over 120 s is counted as late, not here.
Late triggers are included in epic_candidate_triggers but are not uploaded as a
metric of their own.

Only the final status matters. A trigger counts here only if the E:I:T: line
is the last status line recorded for it; a U: line written after the
association replaces "associated" as the final status.

The 120 s latency limit is a setting of the parsing script
(--latency-threshold, default 120).

A trigger whose log lines straddle midnight is split across two log files. Only
the lines in the file holding its N: line are used, so an association written
after midnight is missed.

## Change Log

Sep 16 2026: first full documentation of this metric. The page was previously a
placeholder.

## Contact

squac-help@uw.edu

## See Also

epic_unassociated_triggers, epic_candidate_triggers,
epic_trigger_latency_median

## Updated

2026-09-14

