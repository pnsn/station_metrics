# power_40sec

Hourly Acceleration Power Spectral Density at 40 Seconds

## Summary

This metric reports the acceleration power spectral density of a channel at a
period of 40 s, that is 0.025 Hz, for the reporting hour. The value is in
decibels relative to 1 (m/s^2)^2/Hz and is read from a single one hour ObsPy
PPSD segment at the period bin nearest 40 s.

## Uses

At 40 s the record is dominated by long period noise sources rather than by
seismic signal: temperature swings in the vault, barometric pressure changes,
ground tilt, and mass position drift. On a broadband sensor a rising value
often precedes a mass that needs recentring or points at a vault whose
insulation has failed. On a strong motion accelerometer this band is
essentially all instrument self noise and the value carries little information
about the site.

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
5. Find the period bin whose centre is closest to 40 s and report the power in
   that bin:

   power_40sec = psd_power[argmin(|psd_periods - 40.0|)]

6. Discard the result if it is not below -1 dB. Real values run roughly -180 to
   -50 dB, so anything at or above -1 dB indicates a failed calculation rather
   than a measurement, and is not uploaded.

## Metric Values Returned

value - acceleration power spectral density at 40 s period
(dB rel. 1 (m/s^2)^2/Hz).

starttime - beginning of the reporting hour (UTC).

endtime - end of the reporting hour (UTC).

channel - the channel analyzed, as N.S.L.C.

## Threshold

0 dB.

## Notes

A one hour segment contains only 90 cycles at this period, so the estimate is
statistically poorer here than at the shorter period metrics. Judge it on
multi-day trends rather than on individual hours.

Interpretation differs sharply between broadband and strong motion channels and
they should not be compared directly.

Unlike the time-domain metrics on this channel, PPSD removes the full
instrument response rather than just the sensitivity.

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

power_10Hz, power_5Hz, power_1Hz, power_5sec

## Updated

2026-08-28
