# system_temperature

System Temperature

STATUS: PLACEHOLDER. This metric is produced outside the station_metrics
repository. The algorithm section needs to be completed by whoever maintains
the producing code.

## Summary

This metric reports a datalogger or vault temperature, read from a state of
health channel.

## Uses

Temperature drives long period seismic noise, mass position drift, and at
extremes outright equipment failure. It is tracked both for its own sake, to
catch vault insulation or ventilation problems, and as an explanation for other
metrics going bad: a long period noise metric that rises in step with
temperature points at the vault rather than at the instrument.

## Data Analyzed

Traces - a temperature state of health channel. TODO: confirm the channel codes
and which seismic channel the measurement is attached to in SQUAC.

Window - TODO.

Data Source - TODO.

## Algorithm

TODO. Document how the raw state of health samples are converted to a
temperature, including the scaling from counts to degrees, and whether the
value reported is a mean, a median or an extreme over the window.

## Metric Values Returned

value - temperature. Units TODO, presumably degrees Celsius.

starttime - TODO.

endtime - TODO.

channel - TODO.

## Threshold

TODO.

## Contact

squac-help@uw.edu

## Updated

2026-08-28
