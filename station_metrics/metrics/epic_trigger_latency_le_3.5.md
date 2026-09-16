# epic_trigger_latency_le_3.5

Percentage of EPIC Triggers With Latency of 3.5 Seconds or Less

## Summary

This metric reports the percentage of triggers EPIC declared on a channel
during the hour whose latency, the time between the trigger's time and the
moment EPIC wrote it to its log, was 3.5 s or less. A higher value is better.
It is read from the log files of an EPIC instance on eew-uw-rei, not calculated
from archived waveforms.

## Uses

3.5 s is the working threshold for data being useful to ShakeAlert. This metric
describes reliability: what fraction of a station's triggers reached EPIC in
time to be useful. A station can have an acceptable median while failing this
metric if its latency distribution has a long tail. It is the EPIC-side
counterpart of prefix_ring_latency_le_3.5, which measures packets at a wave
ring rather than triggers.

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
4. For every hour with at least one trigger, count the triggers with latency
   less than or equal to 3.5 s and report

   epic_trigger_latency_le_3.5 = 100 * n_le_3.5 / n_triggers

## Metric Values Returned

value - percentage of triggers in the hour with latency of 3.5 s or less.

starttime - beginning of the hour (UTC).

endtime - end of the hour (UTC).

channel - the channel analyzed, as N.S.L.C.

## Threshold

90%

## Notes

Latency here is the delay between the trigger time and EPIC writing the
trigger to its log. It therefore includes telemetry latency, packetization, and
EPIC's own processing up to the moment the trigger was declared, and is
usually larger than the wave ring latency of the same channel.

No value is uploaded for an hour with no triggers. Unlike the trigger count
metrics, there is no zero-fill.

The log wall clock is taken to be UTC and the midnight correction assumes
latencies below 24 hours.

The comparison is inclusive, so a trigger at exactly 3.5 s counts as on time,
the same convention used by prefix_ring_latency_le_3.5.

With few triggers in an hour the value moves in large steps; one trigger gives
either 0 or 100.

## Change Log

Sep 16 2026: first full documentation of this metric. The page was previously a
placeholder.

## Contact

squac-help@uw.edu

## See Also

epic_trigger_latency_median, epic_trigger_latency_max,
prefix_ring_latency_le_3.5

## Updated

2026-09-14

