# epic_candidate_triggers

Hourly Count of All EPIC Triggers

## Summary

This metric reports the total number of triggers that the EPIC early warning
algorithm declared on a channel during the hour, whatever became of them:
associated, unassociated, rejected, or late. It is read from the log files of
an EPIC instance on eew-uw-rei, not calculated from archived waveforms.

## Uses

This is the station's full trigger load on EPIC. Every trigger must be
evaluated, and most must be associated or rejected, whether or not it turns out
to be useful, so a station with a high candidate count costs processing and
adds opportunities for false associations even if most of its triggers are
eventually rejected. Compared with the associated and unassociated counts, it
shows how much of that load is useful. Compared with
approximate_epic_triggers, which estimates the same quantity from archived
data, it shows how well the approximation matches what EPIC actually did.

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
4. Assign each trigger to the UTC hour containing its trigger time.
5. For every hour in which the channel was present, count the triggers
   assigned to that hour. A channel is present in an hour that contains an S:
   line for it, a trigger on it, or, for a station added part way through the
   day, its "M: Adding station" line. A present hour with no triggers is
   reported as 0.

## Metric Values Returned

value - number of EPIC triggers on the channel in the hour.

starttime - beginning of the hour (UTC).

endtime - end of the hour (UTC).

channel - the channel analyzed, as N.S.L.C.

## Threshold

10

## Notes

Every trigger ends up in exactly one of four classes, so for any hour

   epic_candidate_triggers = epic_associated_triggers
                           + epic_unassociated_triggers
                           + epic_rejected_triggers
                           + late triggers

Late triggers (latency over 120 s and not rejected) are counted here but are not
uploaded as a metric of their own.

A 0 means the channel was being analyzed and produced no triggers. No
measurement at all means the channel was not being analyzed that hour, or the
log file for that day was missing.

A trigger whose N: line was written just after midnight is in the next day's
log file. The last requested day can therefore slightly under-count its 23:00
hour if the following day's file was not read.

Because eew-uw-rei runs a larger channel file than production, the network of
stations around a channel differs from production. Values here describe how
this instance treated the channel and may not match production EPIC.

## Change Log

Sep 16 2026: first full documentation of this metric. The page was previously a
placeholder.

## Contact

squac-help@uw.edu

## See Also

epic_associated_triggers, epic_unassociated_triggers, epic_rejected_triggers,
epic_temporary_3sec_triggers, approximate_epic_triggers

## Updated

2026-09-14
