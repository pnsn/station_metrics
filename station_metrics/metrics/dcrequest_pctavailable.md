# dcrequest_pctavailable

Percentage of Requested Hour Returned by the Datacenter

## Summary

This metric reports what fraction of a one hour data request was actually
satisfied by the archive's FDSN dataselect service. The request is made about
2-3 hours after real time.  The number of samples
returned inside the reporting hour is divided by the number a complete hour
would contain at the channel's nominal sample rate, and expressed as a
percentage. A channel the data center returns nothing at all for is reported
as 0.

## Uses

This is the first thing to look at when any other metric for a channel looks
strange, because a low value means the other metrics were computed on partial
data. Sustained low values point at a channel that is failing to reach the
archive, at telemetry that drops data, or at a data center request that is
being truncated. Note the distinction between the archive's contents and the
request's success: a channel that is complete at the archive can still read low
here if the web service request timed out or returned early.

A value of 0 means either that data were returned but none of it fell inside
the reporting hour, or that the data center returned nothing for the channel.
In the second case this is the only metric reported for that channel, so a
channel showing 0 here and nothing else is a dead channel rather than a
processing failure.

## Data Analyzed

Traces - one N.S.L.C (Network.Station.Location.Channel) per measurement.

Window - the reporting hour, from the requested start time to one hour later.
The channel's other time-domain metrics use a longer 3605.05 s analysis window,
but this metric deliberately uses the clean hour so that the percentage means
what it says.

Data Source - FDSN dataselect from the permanent archive: EarthScope/IRIS DMC
for PNSN data, NCEDC for NCSN data, SCEDC for SCSN data.

SEED Channel Types - ?H? and ?N? (high gain broadband and accelerometer), as
listed in the ShakeAlert channel file.

## Algorithm

1. Request one hour of data plus 5.05 s of lead-in and 120 s of padding on each
   side, for a single N.S.L.C, from the archive's FDSN dataselect service.
2. Cut each returned trace to the reporting hour, from the start time to the
   start time plus 3600 s. The cut includes both endpoints, so a complete
   segment holds one sample more than 3600 s of data.
3. Sum the number of samples in all the cut traces:

   npts_in_hour = sum over segments of npts

4. Divide by the number of samples a complete hour would hold and express as a
   percentage:

   dcrequest_pctavailable = 100 * npts_in_hour / (3600 / delta)

   where delta is the channel's sample interval in seconds.
5. Channels in the channel file that the data center returned no traces for at
   all are reported as 0. This is skipped entirely if the request returned no
   traces for any channel, since that indicates a failed or unreachable data
   center rather than dead stations.

## Metric Values Returned

value - percentage of the reporting hour returned.

starttime - beginning of the reporting hour (UTC).

endtime - end of the reporting hour (UTC).

channel - the channel analyzed, as N.S.L.C.

## Threshold

98.0 percent.

## Notes

Because the cut includes both endpoints, a perfectly complete channel returns
one sample more than 3600 s of data and reads a few thousandths of a percent
above 100.

The PSD metrics are cut separately, with one extra second at the end of the
hour, and are not affected by this. That padding exists because ObsPy's PPSD
requires a segment of at least sampling_rate * 3600 samples, and a cut of
exactly 3600.000 s can come back one sample short of that when the samples are
not aligned with the top of the hour.

If the channel has gaps, several segments are returned and their sample counts
are summed. Overlapping segments would double count, but overlaps are not
expected from an archive request.

## Change Log

Sep 14 2026: the numerator counted samples over the whole 3605.05 s analysis
window while the denominator used an integer 3605 s, so a complete hour read
about 100.14 percent. Both are now the clean hour.

Sep 17 2026: channels the data center returns nothing for are now reported as
0 rather than being omitted from SQUAC.

Sep 17 2026: the PSD metrics no longer share this metric's cut of the hour, so
the extra sample described above is no longer what makes the PSD segment long
enough. See the note above.

## Contact

squac-help@uw.edu

## See Also

dcrequest_ngaps, dcrequest_segmentshort, dcrequest_segmentlong

## Updated

2026-09-17
