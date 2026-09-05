# mass_position

Sensor Mass Position

STATUS: PLACEHOLDER. This metric is produced outside the station_metrics
repository. The algorithm section needs to be completed by whoever maintains
the producing code.

## Summary

This metric reports a seismometer's mass position, read from a state of health
channel.

## Uses

Mass position drifts as a seismometer's springs age, with temperature, and with
ground tilt. A mass that has walked close to one end of its range will clip on
real ground motion and needs recentring, so tracking the position hour to hour
gives advance warning before the channel starts producing bad data. A mass
position that jumps abruptly usually means the instrument was disturbed or has
been recentred.

## Data Analyzed

Traces - a mass position state of health channel. TODO: confirm the channel
codes and which seismic channel the measurement is attached to in SQUAC.

Window - TODO.

Data Source - TODO.

## Algorithm

TODO. Document how the raw state of health samples are converted to a reported
mass position, including any scaling from counts to volts or to a percentage of
full range, and whether the value reported is a mean, a median or an extreme
over the window.

## Metric Values Returned

value - mass position. Units TODO.

starttime - TODO.

endtime - TODO.

channel - TODO.

## Threshold

TODO.

## Contact

squac-help@uw.edu

## Updated

2026-08-28
