# prefix_ring_latency

Average Wave Ring Data Latency

## Summary

This metric reports the average latency of all Tracebuf2 packets carrying a
channel's data into an Earthworm wave ring during a measurement window. Each
packet's latency is the feed latency reported by sniffwave, that is the time
between the measurement and the end of the packet, plus half of that packet's
length.

## Uses

This is the headline number for whether a station is fast enough to be useful
for earthquake early warning. ShakeAlert needs data within a few seconds of
real time, and a station whose average latency sits well above that contributes
little no matter how clean its waveforms are or how complete its archive
coverage is. Being an average it hides bursty behaviour, so it should always be
read together with the maximum latency and the percentage of packets under
3.5 s.

## Data Analyzed

Traces - one S.C.N.L (Station.Channel.Network.Location) per measurement, as
reported by Earthworm's sniffwave.

Window - the sniffwave run duration, normally 600 s. The start and end times
reported are the start time of the first packet and the end time of the last
packet seen for that channel, so the effective window is slightly shorter than
the requested duration and differs slightly between channels.

Data Source - an Earthworm wave ring, normally WAVE_RING, on a live server.
Nothing is read from an archive; this describes the real time data flow as it
actually arrived.

Prefix - identifies the server the measurement was made on: export (PNSN
ewserver), scsn (SCSN pine), ucb (UC Berkeley eew-bk-dev1), menlo (USGS Menlo
Park), eewdev1, eewdev2, ews02. Most channels are sniffed at only one
institution, but a few are sniffed at several; the prefix keeps those
measurements distinct.

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

   The half packet length term estimates the age of the middle of the packet
   rather than its trailing edge.
4. Accumulate the sum of the latencies and the number of packets for each
   channel.
5. At the end of the run report the mean:

   prefix_ring_latency = sum(latency) / npackets

## Metric Values Returned

value - average packet latency (seconds).

starttime - start time of the first packet seen for the channel (UTC).

endtime - end time of the last packet seen for the channel (UTC).

channel - the channel analyzed.

## Threshold

5.0 seconds.

## Notes

This metric requires sniffwave_tally to be run with the --all flag, which is
set automatically when --squac is given.

Packets whose start time is more than 24 hours away from the current time are
discarded before any tallying, which protects the average from a stale or
badly timestamped packet dragging it to an absurd value.

A negative feed latency is possible and is not filtered out. It means the
packet's end time is in the future relative to the server clock, which
indicates a clock problem at either the station or the server.

Because the value is a mean over a short window, a channel that stalls and then
delivers a backlog can show a moderate average while every packet in the
backlog was individually useless to early warning.

## Change Log

No changes in August 2026.

## Contact

squac-help@uw.edu

## See Also

prefix_ring_latency_max, prefix_ring_latency_le_3.5, prefix_ring_packet_length

## Updated

2026-08-28
