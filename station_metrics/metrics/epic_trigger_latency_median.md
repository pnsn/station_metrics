# epic_trigger_latency_median

Median EPIC Trigger Latency

## Summary

This metric reports the median latency, over all triggers EPIC declared on a
channel during the hour, between each trigger's time and the moment EPIC wrote
the trigger to its log. It is read from the log files of an EPIC instance on
eew-uw-rei, not calculated from archived waveforms.

## Uses

This is the typical delay between ground motion arriving at a station and EPIC
being able to use it, measured at EPIC itself rather than at a wave ring. A
station whose median is creeping up is delivering data that is increasingly
too late for early warning, even if its data arrives complete. Comparing it
with prefix_ring_latency for the same channel separates telemetry delay from
delay inside EPIC.

## Data Analyzed

Log lines - the N: (new trigger) lines EPIC writes for one N.S.L.C
(Network.Station.Location.Channel) per measurement. Each N: line carries the
trigger (pick) time and is prefixed with the wall clock time it was written.

Window - the clean UTC hour. Each trigger is assigned to the hour that contains
its trigger time, not the hour in which its N: line was written.

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

1. Read the daily EPIC log files for the requested days and collect every
   N: line for the channel. Discard triggers whose trigger time falls before
   the first requested day.
2. For each trigger compute its latency:

   latency = (wall clock time the N: line was written) - (trigger time)

   adding 86400 s if the result is negative (the N: line was written after
   midnight).
3. Assign each trigger to the UTC hour containing its trigger time. Every
   trigger is used, whether it was later associated, unassociated, rejected or
   late.
4. For every hour with at least one trigger, sort that hour's latencies and
   report their median. With an even number of triggers the median is the
   average of the two middle values.

## Metric Values Returned

value - median trigger latency in the hour (seconds).

starttime - beginning of the hour (UTC).

endtime - end of the hour (UTC).

channel - the channel analyzed, as N.S.L.C.

## Threshold

3.5 seconds

## Notes

Latency here is the delay between the trigger time and EPIC writing the
trigger to its log. It therefore includes telemetry latency, packetization, and
EPIC's own processing up to the moment the trigger was declared, and is
usually larger than the wave ring latency of the same channel.

No value is uploaded for an hour with no triggers. Unlike the trigger count
metrics, there is no zero-fill.

The log wall clock is taken to be UTC and the midnight correction assumes
latencies below 24 hours.

With few triggers in an hour, the median rests on very few values and can jump
around from hour to hour.

## Change Log

Sep 16 2026: first full documentation of this metric. The page was previously a
placeholder.

## Contact

squac-help@uw.edu

## See Also

epic_trigger_latency_max, epic_trigger_latency_le_3.5, prefix_ring_latency

## Updated

2026-09-14

