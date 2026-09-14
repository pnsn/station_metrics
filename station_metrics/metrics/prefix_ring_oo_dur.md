# prefix_ring_oo_dur

Total Duration of Out-of-Order Packets in the Wave Ring

## Summary

This metric reports the total duration of the out-of-order Tracebuf2 packets
seen for a channel in an Earthworm wave ring during a measurement window,
accumulated as the packet length of every packet counted as out of order. It is
a positive number of seconds.

## Uses

Where prefix_ring_n_oo says how often ordering was violated, this says how much
data was involved. A large duration spread over few packets means long packets
arrived late; a small duration spread over many packets means frequent small
disruptions. Together they distinguish a single reordering episode from a link
that is persistently delivering out of sequence.

## Data Analyzed

Traces - one S.C.N.L (Station.Channel.Network.Location) per measurement, as
reported by Earthworm's sniffwave.

Window - the sniffwave run duration, normally 600 s.

Data Source - an Earthworm wave ring, normally WAVE_RING, on a live server.

Prefix - identifies the server the measurement was made on: export, scsn, ucb,
menlo, eewdev1, eewdev2, ews02.

## Algorithm

Detection is described under prefix_ring_n_oo: a packet is out of order when it
starts more than TOLERANCE (0.01 s) earlier than the latest packet start time
already accepted for that channel.

For each such packet the packet length is added to a running total. Packet
length is the end time minus the start time as reported by sniffwave, so it
spans first sample to last sample and is one sample period short of the
interval the packet actually covers. Over a 600 s window that shortfall is
negligible.

This is a measure of how much data arrived out of order, not of how far out of
order it arrived, and it is not a distance in time between packets. A packet
that arrives one slot late and a packet that arrives an hour late contribute
the same amount, provided they are the same length. Note that this is the
opposite convention from prefix_ring_overlap_dur, which does accumulate a
distance in time.

Divide this metric by prefix_ring_n_oo to recover the average length of the
affected packets, which is the useful way to compare it against
prefix_ring_packet_length.

The value is always positive. Zero means either that no packet arrived out of
order or that the channel produced no data in the window; check the packet
count to tell those apart.

### Backfilled gaps contribute here and to the gap metrics

Both are reported by design. When the live stream skips an interval a gap is
counted at that moment, because the data was genuinely absent from the ring.
When the missing packet arrives later it is counted as out of order and its
length is added here. Nothing retroactively removes the earlier gap, so a
channel on a retransmitting link will show gap duration and out-of-order
duration covering the same interval. Read them together: gap duration alone
means data was lost, gap duration accompanied by out-of-order duration means
data was late and later recovered.

### Values approaching the window length

If this metric approaches the sniffwave run duration, the channel is almost
certainly not reordering. Either the station's clock stepped backward, or the
digitizer flushed a buffer of old data after a comms outage, and in both cases
every packet after the event is earlier than the high-water mark and is counted
here. Check prefix_ring_latency_max: a value far exceeding the window length
confirms a timing or backfill event rather than reordering. See
prefix_ring_n_oo for the full discussion.

## Metric Values Returned

value - total duration of out-of-order packets, in positive seconds.

starttime - start time of the first packet seen for the channel, in arrival
order, which is not necessarily the earliest packet in time (UTC).

endtime - end time of the last in-order packet seen for the channel (UTC).

channel - the channel analyzed.

## Threshold

0.01 seconds.

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
   out-of-order packets, in positive seconds. It has never been a cumulative
   distance in time between packets, and it has never been negative.
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

prefix_ring_n_oo, prefix_ring_noverlap, prefix_ring_overlap_dur,
prefix_ring_completeness, prefix_ring_latency_max

## Updated

2026-09-08

