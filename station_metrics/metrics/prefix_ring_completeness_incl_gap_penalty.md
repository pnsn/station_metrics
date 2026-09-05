# prefix_ring_completeness_incl_gap_penalty

Wave Ring Data Completeness With Gap Penalty

## Summary

This metric reports the percentage of a measurement window for which a
channel's data arrived in an Earthworm wave ring, with an additional 30 seconds
deducted from the numerator for every gap found. It is a completeness measure
that deliberately punishes fragmentation as well as absence.

## Uses

The penalty encodes an operational reality that plain completeness misses: each
interruption costs more than the data it swallowed, because algorithms
downstream have to recover state each time the stream breaks. A channel with a
single 60 s gap scores far better here than one with twenty 3 s gaps, even
though both lost the same amount of data, which correctly reflects which of the
two is more useful for early warning. Used alongside plain completeness, the
size of the difference between the two identifies channels whose problem is
fragmentation rather than volume.

## Data Analyzed

Traces - one S.C.N.L (Station.Channel.Network.Location) per measurement, as
reported by Earthworm's sniffwave.

Window - the sniffwave run duration, normally 600 s. The duration used in the
calculation is the end time of the last packet minus the start time of the
first packet seen for that channel.

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
   0.01 s. Count the gaps and accumulate their total duration.
4. At the end of the run, compute the measurement duration as the end time of
   the last packet minus the start time of the first.
5. Report the percentage of the duration for which data was present, less a
   30 second penalty per gap:

   prefix_ring_completeness_incl_gap_penalty =
       100 * (duration - gap_dur - 30 * ngap) / duration

## Metric Values Returned

value - penalized percentage of the measurement window for which data arrived.

starttime - start time of the first packet seen for the channel (UTC).

endtime - end time of the last packet seen for the channel (UTC).

channel - the channel analyzed.

## Threshold

90.0 percent.

## Notes

The value can go negative, and does so easily. With a typical 600 s measurement
window, twenty gaps alone deduct 600 s and drive the result to zero or below
before any gap duration is counted. A large negative value should be read as
"gapping constantly" rather than as an error.

Because the penalty is a fixed 30 s regardless of window length, results from
servers running sniffwave_tally with different durations are not directly
comparable. Plain completeness does not have this problem.

Because the duration is measured from the first to the last packet actually
seen, absence at the edges of the window is invisible here.

A channel that produced no packets at all during the window does not appear in
the output and reports nothing rather than reporting zero.

## Change Log

No changes in August 2026.

## Contact

squac-help@uw.edu

## See Also

prefix_ring_completeness, prefix_ring_gaps_per_hour

## Updated

2026-08-28
