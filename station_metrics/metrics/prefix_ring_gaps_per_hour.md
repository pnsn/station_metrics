# prefix_ring_gaps_per_hour

Wave Ring Gaps Per Hour

## Summary

This metric reports the number of gaps found between consecutive Tracebuf2
packets for a channel in an Earthworm wave ring during a measurement window,
scaled to a rate per hour.

## Uses

Frequent gaps are the classic signature of a marginal radio or cellular link.
For earthquake early warning a channel with regular short gaps can be worse
than one cleanly off the air, because downstream algorithms keep expecting data
that does not come and have to recover state each time. Because the value is
normalized to a per hour rate, measurement windows of different lengths can be
compared directly, and results from servers running sniffwave_tally on
different schedules are comparable.

## Data Analyzed

Traces - one S.C.N.L (Station.Channel.Network.Location) per measurement, as
reported by Earthworm's sniffwave.

Window - the sniffwave run duration, normally 600 s. The duration used in the
normalization is the end time of the last packet minus the start time of the
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
   0.01 s:

   gap if starttime - (prev_endtime + delta) > 0.01 s

4. Count the gaps and accumulate their total duration per channel.
5. At the end of the run, compute the measurement duration as the end time of
   the last packet minus the start time of the first, and report the gap count
   scaled to an hourly rate:

   prefix_ring_gaps_per_hour = 3600 * ngap / duration

## Metric Values Returned

value - gaps per hour (count).

starttime - start time of the first packet seen for the channel (UTC).

endtime - end time of the last packet seen for the channel (UTC).

channel - the channel analyzed.

## Threshold

1 gap per hour.

## Notes

The tolerance of 0.01 s prevents rounding in packet timestamps from being
reported as a stream of tiny gaps.

A channel that produced no packets at all during the window does not appear in
the output, and therefore reports nothing rather than reporting a gap. Total
absence has to be detected from the channel's absence, not from this value.

Because the measurement window is typically only 10 minutes, the per hour
scaling multiplies each observed gap by roughly six. A single gap in a
10 minute window therefore reports as approximately 6 gaps per hour, which is
well above the threshold. This is intentional but is worth keeping in mind when
interpreting individual measurements as opposed to trends.

The gap detection is sequential and assumes packets arrive in order. Out of
order packets can therefore be reported as a gap followed by an overlap.

## Change Log

No changes in August 2026.

## Contact

squac-help@uw.edu

## See Also

prefix_ring_completeness, prefix_ring_completeness_incl_gap_penalty

## Updated

2026-08-28
