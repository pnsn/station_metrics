# prefix_ring_completeness

Wave Ring Data Completeness

## Summary

This metric reports the percentage of a measurement window for which a
channel's data actually arrived in an Earthworm wave ring, taken as the window
duration minus the total duration of all gaps, divided by the window duration.

## Uses

This is the simplest measure of how much of a station's real time stream is
present, and it is the real time counterpart of the archive completeness
metrics. A station can be complete at the archive and incomplete here, because
archives are backfilled and early warning is not: data that arrives late is
still archived but is useless in real time. Because the metric counts only the
wall clock duration swallowed by gaps, a channel with one long gap and a
channel with many short gaps can score identically, which is why a
gap-penalized version exists alongside it.

## Data Analyzed

Traces - one S.C.N.L (Station.Channel.Network.Location) per measurement, as
reported by Earthworm's sniffwave.

Window - the sniffwave run duration, normally 600 s. The duration used in the
calculation is the end time of the last packet minus the start time of the
first packet seen for that channel, which is slightly shorter than the
requested run duration.

Data Source - an Earthworm wave ring, normally WAVE_RING, on a live server.
Nothing is read from an archive; this describes the real time data flow as it
actually arrived.

Prefix - identifies the server the measurement was made on: export (PNSN
ewserver), scsn (SCSN pine), ucb (UC Berkeley eew-bk-dev1), menlo (USGS Menlo
Park), eewdev1, eewdev2, ews02.

SEED Channel Types - ?H? and ?N? with components E, N, Z, 1, 2 or 3, matched by
sniffwave_tally's channel filter.

## Algorithm

1. Run Earthworm's sniffwave against the wave ring for the requested duration
   and consume its output line by line.
2. For each channel, keep the end time of the previous packet seen.
3. Declare a gap when the next packet's start time is later than the previous
   packet's end time plus one sample interval, by more than a tolerance of
   0.01 s. Accumulate the total duration of those gaps:

   gap_dur = sum of ( starttime - (prev_endtime + delta) ) over all gaps

4. At the end of the run, compute the measurement duration as the end time of
   the last packet minus the start time of the first.
5. Report the percentage of the duration for which data was present:

   prefix_ring_completeness = 100 * (duration - gap_dur) / duration

## Metric Values Returned

value - percentage of the measurement window for which data arrived.

starttime - start time of the first packet seen for the channel (UTC).

endtime - end time of the last packet seen for the channel (UTC).

channel - the channel analyzed.

## Threshold

90.0 percent.

## Notes

Because the duration is measured from the first to the last packet actually
seen, a channel that was silent for the first half of the window and then
delivered continuously reports 100 percent completeness over the half window it
was present for. Total or partial absence at the edges of the window is
therefore invisible here and has to be caught by the channel simply not
appearing, or by the archive completeness metrics.

A channel that produced no packets at all during the window does not appear in
the output and reports nothing rather than reporting zero.

The gap detection is sequential and assumes packets arrive in order.

## Change Log

No changes in August 2026.

## Contact

squac-help@uw.edu

## See Also

prefix_ring_completeness_incl_gap_penalty, prefix_ring_gaps_per_hour

## Updated

2026-08-28
