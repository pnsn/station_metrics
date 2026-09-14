# prefix_ring_n_oo

Number of Out-of-Order Packets in the Wave Ring

## Summary

This metric reports the number of out-of-order Tracebuf2 packets seen for a
channel in an Earthworm wave ring during a measurement window. sniffwave_tally
counts a packet as out of order when it starts earlier than the latest packet
start time already accepted for that channel.

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

sniffwave prints packets in the order they appear in the ring, that is, in
arrival order. For each channel sniffwave_tally keeps a high-water mark: the
start time of the most recent packet it accepted as in order.

A packet is counted as out of order when its start time is more than TOLERANCE
(0.01 s) earlier than that high-water mark. When that happens the packet is
counted here, its length is added to prefix_ring_oo_dur, and the tracking times
are left where they are: the high-water mark, the previous packet end time, and
the channel's reported end time are all unchanged.

Leaving the tracking times alone is the point of the design. If they were
rolled back to the stale packet, the next normally ordered packet would be
measured against a time in the past and reported as a large gap that never
happened. Because the high-water mark is not rolled back either, gap, overlap,
and out-of-order are mutually exclusive: a packet is counted in at most one of
the three.

An out-of-order packet still counts toward the packet total, the latency
statistics, and the byte total, since it did flow through the ring. It does not
extend the channel's reported end time, so if a late packet happens to reach
further forward in time than anything seen so far, that extra coverage is not
credited to the completeness metrics.

### Effect of the tolerance

The 0.01 s tolerance is absolute, so it is a different number of samples at
different rates: 0.4 samples at 40 sps, 1 sample at 100 sps, 2 samples at
200 sps. A packet that starts less than 0.01 s before the high-water mark is
therefore treated as in order, and will normally be counted as an overlap
instead. At 200 sps and above, reordering of one or two samples is invisible to
this metric. That is deliberate; the tolerance exists to absorb the rounding in
sniffwave's four-decimal time fields, which is about 5e-5 s.

### Backfilled gaps are reported as both a gap and an out-of-order packet

This is intended behavior, not double counting. The two events are separate and
both are real:

- When the live stream skips an interval, a gap is counted at that moment. At
  that moment the data was genuinely absent from the ring.
- When the missing packet arrives later, it is counted here as out of order.

So a channel whose link retransmits will show gaps and out-of-order packets
covering the same interval. Read the pair together: gaps alone means data was
lost, gaps plus out-of-order packets means data was late and subsequently
recovered. Nothing in sniffwave_tally retroactively removes a gap that was
later filled.

### Distinguishing reordering from a station time jump

A digitizer whose clock steps backward, most often after a power cycle without
GPS lock or an NTP resynchronization on a unit with a dead RTC battery, makes
every packet after the jump earlier than the high-water mark. All of them are
counted here.

Three signals separate that case from network reordering:

- prefix_ring_latency_max. sniffwave's latency is server time now minus the
  packet end time. Reordering in a network path produces latencies of a few
  seconds. A station running an hour behind produces latencies of an hour.
- The count relative to the total packet count. Reordering affects a handful of
  packets out of hundreds; a time jump affects every packet after the jump, so
  this metric approaches the channel's packet count.
- Persistence. A retransmission backfill after a comms outage also produces
  many out-of-order packets with large latency, but it is confined to one or
  two measurement windows. A wrong clock persists across windows.

A high count combined with a latency far exceeding the window length is a
timing problem, not reordering.

One limit worth knowing: sniffwave_tally discards any packet whose start time
is more than 86400 s from the current time, so a clock that is off by days
never reaches this logic at all. Those channels show a reduced packet count
instead.

## Metric Values Returned

value - number of out-of-order packets (count).

starttime - start time of the first packet seen for the channel, in arrival
order, which is not necessarily the earliest packet in time (UTC).

endtime - end time of the last in-order packet seen for the channel (UTC).

channel - the channel analyzed.

## Threshold

1 count.

## September 2026 Changes

The gap, overlap, and out-of-order logic in sniffwave_tally was corrected in
September 2026. Values before and after that date are not directly comparable.
The same list appears in all four related documents.

1. Out-of-order detection now compares each packet's start time against the
   high-water mark of accepted start times. The previous test compared the
   packet's end time against the start time of the immediately preceding packet
   only, which required a packet to lie entirely before its predecessor. Late
   packets that started early but overlapped their predecessor were counted as
   nothing at all. prefix_ring_n_oo and prefix_ring_oo_dur both read higher
   than before on affected channels.
2. Out-of-order packets no longer roll the tracking times backward. Previously
   the first normal packet after an out-of-order packet was reported as a gap
   that never occurred, with a duration of roughly two packet lengths.
   prefix_ring_gaps_per_hour reads lower and both completeness metrics read
   higher on channels that reorder.
3. Gap, overlap, and out-of-order are now mutually exclusive. Previously a
   second out-of-order packet overlapping the first could be counted in both
   prefix_ring_n_oo and prefix_ring_noverlap.
4. prefix_ring_overlap_dur is now reported as a positive number of seconds. It
   was previously negative.
5. prefix_ring_oo_dur is unchanged in definition: the summed length of the
   out-of-order packets, in positive seconds.
6. The channel end time reported with each measurement is now the end of the
   last in-order packet, so it can no longer be rolled backward by a late
   packet. The window length used by the completeness metrics and by
   prefix_ring_gaps_per_hour is derived from it.
7. These four metrics are now sent to SQUAC. Previously they were computed and
   written to the CSV but never posted. As with every metric here, they must
   already exist in the SQUAC database under the given prefix; any that do not
   are skipped and their names are printed at the start of the run.
8. The byte total now includes the first packet of each channel in each window,
   which was previously omitted.
9. The sanity filter that discards packets more than 86400 s from the present
   now uses a correct epoch time. It previously used a naive UTC timestamp,
   which was offset by the server's UTC offset on any host not set to UTC.
10. TOLERANCE is unchanged at 0.01 s.

## Contact

squac-help@uw.edu

## See Also

prefix_ring_oo_dur, prefix_ring_noverlap, prefix_ring_overlap_dur,
prefix_ring_gaps_per_hour, prefix_ring_latency_max

## Updated

2026-09-08

