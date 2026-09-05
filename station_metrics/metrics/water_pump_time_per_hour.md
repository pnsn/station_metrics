# water_pump_time_per_hour

Water Pump Run Time Per Hour

STATUS: PLACEHOLDER. This metric is produced outside the station_metrics
repository. The algorithm section needs to be completed by whoever maintains
the producing code.

## Summary

This metric reports the number of seconds in each hour that a vault's water
pump was running, as recorded on the VE1 and VE2 state of health channels,
which are also seen as SP1 and SP2 on some dataloggers.

## Uses

A pump that runs more than briefly means water is entering the vault, which
threatens both the instrument and the electronics. A pump running continuously
usually means it has failed to keep up with inflow or is stuck on, either of
which is a maintenance visit. Because the metric is hourly, a rising trend over
a wet season is visible well before the water reaches anything expensive.

## Data Analyzed

Traces - the VE1 and VE2 (or SP1 and SP2) state of health channels for a
station. The resulting measurement is attached to the station's HHZ channel in
SQUAC rather than to the state of health channel itself.

Window - one hour. TODO: confirm whether this is the clean hour or a padded
window.

Data Source - TODO.

## Algorithm

TODO. Document how pump-on is detected from the VE1/VE2 sample values, what
threshold or state encoding is used, and how the on-time is accumulated.

## Metric Values Returned

value - seconds the pump was on during the hour.

starttime - beginning of the reporting hour (UTC).

endtime - end of the reporting hour (UTC).

channel - the station's HHZ channel.

## Threshold

0 seconds.

## Contact

squac-help@uw.edu

## Updated

2026-08-28
