# dcrequest_ngaps

Number of Gaps in the Hour Returned by the Datacenter

## Summary

This metric counts the gaps between consecutive data segments returned by the
archive's FDSN dataselect service for one hour of a single channel. A channel
returned as one continuous segment scores zero.

## Uses

Gaps are the most common symptom of telemetry trouble. For earthquake early
warning a channel that gaps repeatedly can be worse than one cleanly off the
air, because the system continues to expect data that does not arrive. Read
together with dcrequest_pctavailable, this metric distinguishes a channel that
is missing a lot of data in one piece from one that is missing the same amount
shredded into fragments.

## Data Analyzed

Traces - one N.S.L.C (Network.Station.Location.Channel) per measurement.

Window - the reporting hour, from the requested start time to one hour later.

Data Source - FDSN dataselect from the permanent archive: EarthScope/IRIS DMC
for PNSN data, NCEDC for NCSN data, SCEDC for SCSN data.

SEED Channel Types - ?H? and ?N? (high gain broadband and accelerometer), as
listed in the ShakeAlert channel file.

## Algorithm

1. Request one hour of data plus lead-in and padding for a single N.S.L.C from
   the archive's FDSN dataselect service.
2. Cut every returned trace to the reporting hour and collect the cut traces
   into a single ObsPy Stream.
3. Call Stream.get_gaps on that stream. Each entry it returns describes the
   discontinuity between two consecutive segments, with a positive delta for a
   gap and a negative delta for an overlap.
4. Count only the entries with a positive delta:

   dcrequest_ngaps = number of get_gaps entries with delta > 0

## Metric Values Returned

value - number of gaps inside the reporting hour (unitless count).

starttime - beginning of the reporting hour (UTC).

endtime - end of the reporting hour (UTC).

channel - the channel analyzed, as N.S.L.C.

## Threshold

1 gap.

## Notes

Overlaps are not counted. They are reported separately by ObsPy with a negative
delta and are not expected from an archive request.

A gap that begins before the hour or ends after it is not counted, because only
the portion of the data inside the reporting hour is examined. A channel that
is entirely absent for the hour produces no segments and therefore no gaps, and
reads zero here; dcrequest_pctavailable is what identifies that case.

## Change Log

Aug 2026: this was previously the number of returned trace segments minus one,
counted over the 3605.05 s analysis window. That count also included overlaps
and any segment split caused by a change of sample rate or encoding, and it
counted discontinuities in the 5.05 s of lead-in that falls outside the
reporting hour.

## Contact

squac-help@uw.edu

## See Also

dcrequest_pctavailable, dcrequest_segmentshort, dcrequest_segmentlong

## Updated

2026-08-28
