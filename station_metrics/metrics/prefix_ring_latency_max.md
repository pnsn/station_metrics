# prefix_ring_latency_max

Maximum Wave Ring Data Latency

## Summary

This metric reports the largest single packet latency observed for a channel in
an Earthworm wave ring during a measurement window, where latency is the feed
latency reported by sniffwave, that is the time between the measurement and the
end of the packet, plus half of that packet's length.

## Uses

This exposes the worst case that an average latency hides. A channel with a
good average but a large maximum is arriving in bursts, which typically means a
telemetry link that stalls and then dumps a backlog. Those backlogged packets
are useless to earthquake early warning even though they eventually arrive, so
a station can look healthy on average while being unreliable exactly when it
matters. Watched over time, a maximum that creeps upward is often the earliest
warning of a degrading radio or cellular link.

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
2. For each line that parses as a valid packet for a seismic channel, extract
   the packet start time, end time, and the feed latency that sniffwave
   reports.
3. Compute the packet length and the packet's latency:

   packet_length = endtime - starttime
   latency       = feed_latency + 0.5 * packet_length

4. Keep a running maximum of the latency for each channel, initialised from the
   first packet seen.
5. At the end of the run report that maximum:

   prefix_ring_latency_max = max(latency over all packets)

## Metric Values Returned

value - largest packet latency observed (seconds).

starttime - start time of the first packet seen for the channel (UTC).

endtime - end time of the last packet seen for the channel (UTC).

channel - the channel analyzed.

## Threshold

5.0 seconds.

## Notes

This metric requires sniffwave_tally to be run with the --all flag, which is
set automatically when --squac is given.

Packets whose start time is more than 24 hours away from the current time are
discarded before any tallying, so a single stale packet cannot set the maximum
to an absurd value. Within that filter, however, the metric is by construction
driven by a single packet and is therefore much noisier hour to hour than the
average latency.

A channel that produced exactly one packet during the window reports that
packet's latency as both the average and the maximum.

## Change Log

Aug 2026: added to the published metric documentation. The measurement itself
has been produced by sniffwave_tally for some time.

## Contact

squac-help@uw.edu

## See Also

prefix_ring_latency, prefix_ring_latency_le_3.5

## Updated

2026-08-28
