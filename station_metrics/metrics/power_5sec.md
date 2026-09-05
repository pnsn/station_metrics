# power_5sec

Hourly Acceleration Power Spectral Density at 5 Seconds

## Summary

This metric reports the acceleration power spectral density of a channel at a
period of 5 s, that is 0.2 Hz, for the reporting hour. The value is in decibels
relative to 1 (m/s^2)^2/Hz and is read from a single one hour ObsPy PPSD
segment at the period bin nearest 5 s.

## Uses

5 s is close to the secondary microseism peak, where ocean waves interacting
with the coast drive the loudest persistent noise in the seismic spectrum. The
value therefore rises and falls with sea state and is expected to vary
seasonally and with individual storms. It should be judged against the same
station's own history rather than against other stations, and an unusually flat
seasonal pattern can itself be a sign that a channel is not responding
properly at long period.

## Data Analyzed

Traces - one N.S.L.C (Network.Station.Location.Channel) per measurement. Only a
single continuous segment spanning the whole reporting hour is used; a channel
whose hour is broken by a gap produces no value.

Window - the reporting hour, from the requested start time to one hour later.
This differs from the 3605.05 s analysis window used by the time-domain
metrics.

Data Source - FDSN dataselect from the permanent archive: EarthScope/IRIS DMC
for PNSN data, NCEDC for NCSN data, SCEDC for SCSN data. Instrument metadata is
requested at response level from the same archive.

SEED Channel Types - ?H? and ?N? (high gain broadband and accelerometer), as
listed in the ShakeAlert channel file.

## Algorithm

1. Request the reporting hour plus lead-in and padding for a single N.S.L.C,
   along with the channel's response level metadata.
2. Cut the raw, uncorrected counts trace to the reporting hour, taking one
   extra sample at the end so the segment always spans at least 3600 s.
3. Confirm the segment spans at least 3600 s. If it does not, no value is
   produced.
4. Hand the raw trace and the response level metadata to ObsPy's PPSD with its
   default settings. PPSD removes the full instrument response, segments the
   input into one hour pieces, and returns power in dB relative to
   1 (m/s^2)^2/Hz on its standard octave-fraction period binning. Because the
   input is exactly one hour long, exactly one segment is produced.
5. Find the period bin whose centre is closest to 5 s and report the power in
   that bin:

   power_5sec = psd_power[argmin(|psd_periods - 5.0|)]

6. Discard the result if it is not below -1 dB. Real values run roughly -180 to
   -50 dB, so anything at or above -1 dB indicates a failed calculation rather
   than a measurement, and is not uploaded.

## Metric Values Returned

value - acceleration power spectral density at 5 s period
(dB rel. 1 (m/s^2)^2/Hz).

starttime - beginning of the reporting hour (UTC).

endtime - end of the reporting hour (UTC).

channel - the channel analyzed, as N.S.L.C.

## Threshold

0 dB.

## Notes

On strong motion accelerometers the microseism is often at or below the
instrument's self noise at this period, so the value reflects instrument noise
rather than ground motion. Interpretation differs sharply between ?H? and ?N?
channels and they should not be compared directly.

Unlike the time-domain metrics on this channel, PPSD removes the full
instrument response rather than just the sensitivity.

The value is taken from the nearest available period bin, not interpolated to
exactly 5 s.

Requesting one extra sample at the end of the cut is deliberate: a segment of
exactly 3600.000 s can come back a fraction of a sample short and be rejected by
PPSD.

## Change Log

Aug 2026: the PSD was previously computed on the 3605.05 s analysis window, so
the hour actually measured began 5.05 s before the top of the hour. It now runs
on the clean hour.

Aug 2026: a failed PPSD calculation used to reach SQUAC as a value of -1. It is
now discarded.

Aug 2026: previously documented as coming from IRIS MUSTANG. It has always been
calculated locally with ObsPy PPSD.

## Contact

squac-help@uw.edu

## See Also

power_10Hz, power_5Hz, power_1Hz, power_40sec

## Updated

2026-08-28
