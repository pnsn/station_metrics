# prefix_ring_n_oo

Number of Out-of-Order Packets in the Wave Ring

STATUS: PLACEHOLDER. The out-of-order detection logic in sniffwave_tally is
under review as of August 2026. This metric should not be relied on until that
work is finished.

## Summary

This metric reports the number of out-of-order Tracebuf2 packets seen for a
channel in an Earthworm wave ring during a measurement window. sniffwave_tally
counts a packet as out of order when its end time falls before the start time
of a packet already seen.

## Uses

Out-of-order arrival means packets are reaching the server by a path that does
not preserve ordering, or that a retransmission mechanism is refilling earlier
intervals. For early warning this matters because downstream algorithms
generally assume ordered data, and a channel delivering out of order can
produce results that are hard to interpret even when its completeness and
latency numbers look acceptable.

## Data Analyzed

Traces - one S.C.N.L (Station.Channel.Network.Location) per measurement, as
reported by Earthworm's sniffwave.

Window - the sniffwave run duration, normally 600 s.

Data Source - an Earthworm wave ring, normally WAVE_RING, on a live server.

Prefix - identifies the server the measurement was made on: export, scsn, ucb,
menlo, eewdev1, eewdev2, ews02.

## Algorithm

TODO. The current implementation compares each packet's end time against the
start time of the immediately preceding packet only, which is why the logic is
under review: it does not detect a packet that arrives out of order relative to
a packet further back in the stream, and it can interact with the gap and
overlap detection so that a single out-of-order packet is also reported as a
gap and an overlap. Document the corrected algorithm here once it is settled.

## Metric Values Returned

value - number of out-of-order packets (count).

starttime - start time of the first packet seen for the channel (UTC).

endtime - end time of the last packet seen for the channel (UTC).

channel - the channel analyzed.

## Threshold

TODO.

## Contact

squac-help@uw.edu

## See Also

prefix_ring_oo_dur, prefix_ring_gaps_per_hour

## Updated

2026-08-28
