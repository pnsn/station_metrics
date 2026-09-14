# prefix_ring_overlap_dur

Total Overlap Duration in the Wave Ring

## Summary

This metric reports the total amount of time by which packets overlapped their
predecessor for a channel in an Earthworm wave ring during a measurement
window. As of September 2026 it is a positive number of seconds; before that
date it was reported as a negative number.

## Uses

Where prefix_ring_noverlap says how many packets re-delivered data, this says
how much time was re-delivered. The ratio of the two gives the average overlap
per event, which separates a channel repeating whole packets from one whose
packet boundaries are drifting by a sample or two. A total approaching the
window length means essentially every sample is arriving twice, which is the
signature of a station imported by two feeds into the same ring.

## Data Analyzed

Traces - one S.C.N.L (Station.Channel.Network.Location) per measurement, as
reported by Earthworm's sniffwave.

Window - the sniffwave run duration, normally 600 s.

Data Source - an Earthworm wave ring, normally WAVE_RING, on a live server.

Prefix - identifies the server the measurement was made on: export, scsn, ucb,
menlo, eewdev1, eewdev2, ews02.

## Algorithm

Detection is described under prefix_ring_noverlap. For each packet counted as
an overlap, the amount added here is

    (previous packet end time + dt) - this packet start time

where dt is one sample period. That is the distance between where the packet
should have started and where it actually started, in seconds, and it is always
positive for a packet that qualifies as an overlap.

Note that this is a distance in time, not a sum of packet lengths. It is the
opposite convention from prefix_ring_oo_dur, which sums the lengths of the
out-of-order packets. The two are not comparable quantities even though both
are reported in seconds.

An exactly duplicated packet contributes roughly one packet length. A packet
that repeats half of its predecessor contributes roughly half a packet length.
An overlap can never contribute much more than one packet length, because a
packet starting further back than the high-water mark is classified as out of
order rather than as an overlap.

### Effect of the tolerance

Overlaps smaller than TOLERANCE (0.01 s) are not counted at all, so this total
excludes sub-tolerance jitter. At 40 sps the tolerance is under half a sample;
at 200 sps it is two samples, so overlaps of one or two samples are invisible
at high rates.

### Relationship to the completeness metrics

prefix_ring_completeness and prefix_ring_completeness_incl_gap_penalty are
computed from gap duration only. Overlap duration does not enter either
calculation, so duplicated data cannot push completeness above 100 percent.

## Metric Values Returned

value - total overlap duration, in positive seconds.

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
   prefix_ring_n_oo and prefix_ring_noverlap, so this metric and
   prefix_ring_noverlap read lower than before on channels that reorder.
4. This metric is now reported as a positive number of seconds. It was
   previously negative, because the accumulated quantity was start time minus
   expected start rather than the reverse. Any SQUAC alarm, dashboard axis, or
   downstream comparison written against the old sign needs updating; the
   magnitude is unchanged.
5. prefix_ring_oo_dur is unchanged in definition: the summed length of the
   out-of-order packets, in positive seconds. It has never been negative.
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

prefix_ring_noverlap, prefix_ring_oo_dur, prefix_ring_n_oo,
prefix_ring_completeness

## Updated

2026-09-08

