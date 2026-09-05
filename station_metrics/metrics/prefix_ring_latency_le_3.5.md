# prefix_ring_latency_le_3.5

Percentage of Packets Arriving Within 3.5 Seconds

## Summary

This metric reports the percentage of Tracebuf2 packets carrying a channel's
data into an Earthworm wave ring that arrived with a latency of 3.5 s or less,
where latency is the feed latency reported by sniffwave plus half of the
packet's length. A higher value is better.

## Uses

3.5 s is the working threshold for a packet being useful to ShakeAlert. Where
average latency describes typical performance and maximum latency describes the
worst case, this metric describes reliability: what fraction of the data
actually arrived in time to be used. A station can have an acceptable average
while failing this metric badly if its latency distribution has a long tail,
which is exactly the behaviour a stalling telemetry link produces.

## Data Analyzed

Traces - one S.C.N.L (Station.Channel.Network.Location) per measurement, as
reported by Earthworm's sniffwave.

Window - the sniffwave run duration, normally 600 s. The start and end times
reported are the start time of the first packet and the end time of the last
packet seen for that channel.

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
2. For each line that parses as a valid packet for a seismic channel, compute
   the packet length and the packet's latency:

   packet_length = endtime - starttime
   latency       = feed_latency + 0.5 * packet_length

3. Count the packet as late if its latency is strictly greater than 3.5 s.
   Accumulate the total packet count and the late packet count per channel.
4. At the end of the run report the percentage that were not late:

   prefix_ring_latency_le_3.5 = 100 * (npackets - nlate) / npackets

## Metric Values Returned

value - percentage of packets with latency of 3.5 s or less.

starttime - start time of the first packet seen for the channel (UTC).

endtime - end time of the last packet seen for the channel (UTC).

channel - the channel analyzed.

## Threshold

90.0 percent.

## Notes

The older name for this measurement, pct_gt_3.5sec_late, is misleading. The
value has always been the percentage of packets that are NOT late, so
historical data recorded under the old name should be read exactly the same way
as data recorded under the current name. No inversion is needed when comparing
across the rename.

This metric requires sniffwave_tally to be run with the --all flag, which is
set automatically when --squac is given.

The comparison is strict, so a packet at exactly 3.5 s counts as on time.

Packets whose start time is more than 24 hours away from the current time are
discarded before any tallying.

## Change Log

No changes in August 2026.

## Contact

squac-help@uw.edu

## See Also

prefix_ring_latency, prefix_ring_latency_max

## Updated

2026-08-28
