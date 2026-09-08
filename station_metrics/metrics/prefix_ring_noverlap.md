# prefix_ring_noverlap

Number of Overlapping Packets in the Wave Ring

## Summary

This metric reports the number of Tracebuf2 packets seen for a channel in an
Earthworm wave ring during a measurement window that re-delivered data already
covered by the previous packet. A packet is counted as overlapping when it
starts before the previous packet's next expected sample, but is not far enough
back to be classified as out of order.

## Uses

Overlaps mean the same samples reached the ring more than once. The usual
causes are a retransmission mechanism resending data that already arrived, a
station being imported by two feeds into the same ring, or a digitizer
repeating a packet after a link hiccup. None of these lose data, so overlaps do
not by themselves indicate a data problem, but they do indicate wasted
bandwidth and they can confuse downstream modules that assume each sample
arrives once. A channel that produces a steady overlap count usually has a
duplicate import route that should be removed.

## Data Analyzed

Traces - one S.C.N.L (Station.Channel.Network.Location) per measurement, as
reported by Earthworm's sniffwave.

Window - the sniffwave run duration, normally 600 s.

Data Source - an Earthworm wave ring, normally WAVE_RING, on a live server.

Prefix - identifies the server the measurement was made on: export, scsn, ucb,
menlo, eewdev1, eewdev2, ews02.

## Algorithm

For each channel sniffwave_tally tracks the end time of the previous in-order
packet. The expected start of the next packet is that end time plus one sample
period, dt, where dt is the reciprocal of the sample rate reported by
sniffwave.

A packet that is not out of order is compared against that expected start:

- If it starts more than TOLERANCE (0.01 s) after the expected start, it is a
  gap.
- If it starts more than TOLERANCE before the expected start, it is counted
  here as an overlap, and the amount is added to prefix_ring_overlap_dur.
- Otherwise it is contiguous and nothing is counted.

Gap, overlap, and out-of-order are mutually exclusive. A packet that starts
before the high-water mark of accepted start times is classified as out of
order instead of as an overlap, and is not counted here. In practice this
metric captures packets that re-deliver part of the immediately preceding
packet, while packets that re-deliver something further back are captured by
prefix_ring_n_oo.

A fully duplicated packet, delivered twice in a row, is counted here once, with
an overlap amount of roughly one packet length.

### Effect of the tolerance

The 0.01 s tolerance is absolute, so it is a different number of samples at
different rates: 0.4 samples at 40 sps, 1 sample at 100 sps, 2 samples at
200 sps. Overlaps smaller than the tolerance are not counted, so at 200 sps and
above a one- or two-sample overlap is invisible. That is deliberate; the
tolerance exists to absorb the rounding in sniffwave's four-decimal time
fields, which is about 5e-5 s.

### Relationship to the completeness metrics

prefix_ring_completeness and prefix_ring_completeness_incl_gap_penalty are
computed from gap duration only. Overlapping data neither raises nor lowers
them, and completeness can never exceed 100 percent because of duplicates.

## Metric Values Returned

value - number of overlapping packets (count).

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
   prefix_ring_n_oo and this metric, so this metric reads lower than before on
   channels that reorder. The explicit guard that used to exclude out-of-order
   packets from the overlap test has been removed as unnecessary; freezing the
   tracking times does the same job.
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

prefix_ring_overlap_dur, prefix_ring_n_oo, prefix_ring_oo_dur,
prefix_ring_gaps_per_hour

## Updated

2026-09-08

