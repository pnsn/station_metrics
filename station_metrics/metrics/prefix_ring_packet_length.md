# prefix_ring_packet_length

Average Tracebuf2 Packet Length

## Summary

This metric reports the average duration in seconds of the Tracebuf2 packets
carrying a channel's data into an Earthworm wave ring during a measurement
window, taken as the mean of each packet's end time minus its start time.

## Uses

Packet length trades directly against latency: longer packets are more
efficient on the wire, but every packet has to be filled before it can be sent,
so a station configured with long packets cannot be fast no matter how good its
telemetry is. This metric is therefore the first place to look when a station
has stubbornly high latency and no obvious link problem, since the fix is a
digitizer configuration change rather than a field visit. A sudden change in
the value almost always means someone reconfigured a datalogger.

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
   the packet length as the difference between the packet's end and start
   times:

   packet_length = endtime - starttime

3. Accumulate the sum of the packet lengths and the number of packets for each
   channel.
4. At the end of the run report the mean:

   prefix_ring_packet_length = sum(packet_length) / npackets

## Metric Values Returned

value - average packet length (seconds).

starttime - start time of the first packet seen for the channel (UTC).

endtime - end time of the last packet seen for the channel (UTC).

channel - the channel analyzed.

## Threshold

5.0 seconds.

## Notes

This metric requires sniffwave_tally to be run with the --all flag, which is
set automatically when --squac is given.

For ShakeAlert channels values are typically well under a second. The threshold
of 5.0 s is a loose sanity bound rather than a performance target; a channel
approaching it is badly misconfigured for early warning.

The packet length is measured from the timestamps in the packet itself, so it
reflects how much data the packet carries rather than how long it took to
arrive.

Packets whose start time is more than 24 hours away from the current time are
discarded before any tallying.

## Change Log

No changes in August 2026.

## Contact

squac-help@uw.edu

## See Also

prefix_ring_latency, prefix_ring_latency_le_3.5

## Updated

2026-08-28
