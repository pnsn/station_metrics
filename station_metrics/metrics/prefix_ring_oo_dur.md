# prefix_ring_oo_dur

Total Duration of Out-of-Order Packets in the Wave Ring

STATUS: PLACEHOLDER. The out-of-order detection logic in sniffwave_tally is
under review as of August 2026. This metric should not be relied on until that
work is finished.

## Summary

This metric reports the total duration of the out-of-order Tracebuf2 packets
seen for a channel in an Earthworm wave ring during a measurement window,
accumulated as the packet length of every packet counted as out of order.

## Uses

Where the out-of-order packet count says how often ordering was violated, this
says how much data was involved. A large duration spread over few packets means
long packets arrived late; a small duration spread over many packets means
frequent small disruptions. Together they distinguish a single reordering
episode from a link that is persistently delivering out of sequence.

## Data Analyzed

Traces - one S.C.N.L (Station.Channel.Network.Location) per measurement, as
reported by Earthworm's sniffwave.

Window - the sniffwave run duration, normally 600 s.

Data Source - an Earthworm wave ring, normally WAVE_RING, on a live server.

Prefix - identifies the server the measurement was made on: export, scsn, ucb,
menlo, eewdev1, eewdev2, ews02.

## Algorithm

TODO. The duration accumulated is the packet length of each packet counted as
out of order, so this metric inherits whatever detection logic the out-of-order
count uses. That logic is under review; document the corrected algorithm here
once it is settled.

## Metric Values Returned

value - total duration of out-of-order packets (seconds).

starttime - start time of the first packet seen for the channel (UTC).

endtime - end time of the last packet seen for the channel (UTC).

channel - the channel analyzed.

## Threshold

TODO.

## Contact

squac-help@uw.edu

## See Also

prefix_ring_n_oo, prefix_ring_completeness

## Updated

2026-08-28

================================================================================
END OF DOCUMENT
================================================================================
