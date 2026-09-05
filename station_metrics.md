# Station quality metrics

All hourly metrics listed below are calculated from data archived at their
respective permanent archives (EarthScope/IRIS DMC for PNSN data, NCEDC for
NCSN data, SCEDC for SCSN data) and requested using FDSN web services. The
metrics of measurement completeness give an indication of how successful the
collection of the data from those archives was using FDSN dataselect, and may
not always accurately represent what is stored at the archive.

Metric names link to a standalone detail page under `metrics/`.

## Time windows

Two windows are in play for the hourly metrics and they are not the same
length.

* **Analysis window** — runs from `starttime - 5.05 s` to `starttime + 3600 s`,
  i.e. 3605.05 s. The 5.05 s lead-in is the STA (0.05 s) plus LTA (5.0 s) of
  the trigger function, present so the STA/LTA has converged before the hour
  begins. Every time-domain metric (amplitudes, noise floors, RMS durations,
  spike and trigger counts) is measured over this window.
* **Reporting window** — the clean hour, `starttime` to `starttime + 3600 s`.
  This is what is written to SQUAC as the measurement start and end time. The
  four `dcrequest_*` completeness metrics and the five `power_*` PSD metrics
  are measured over this window only.

Waveforms are requested with a further 120 s of padding either side of the
analysis window. The padding is never measured; it exists so that integration
drift and filter start-up transients fall outside the measured window.

## Processing chain

Raw counts to filtered ground motion, in this order:

1. detrend with a third-order polynomial (on the padded trace)
2. remove the mean
3. divide out the overall sensitivity from the station metadata (gain only,
   not the full response)
4. integrate or differentiate to the requested ground-motion type
5. filter, causal Butterworth, 2 corners
6. cut to the analysis window
7. remove the mean again

Filtering is causal on purpose: ShakeAlert's real-time processing is causal,
and these metrics are meant to resemble what the production system sees.

## Filter bands

* STA/LTA trigger function: velocity, highpassed at 3 Hz, STA 0.05 s,
  LTA 5.0 s, threshold 20.
* Amplitude measurements: acceleration (and velocity and displacement for the
  EPIC approximation), either highpassed at 0.075 Hz or bandpassed
  0.075 - 15 Hz. Metrics with `bp` in their name use the bandpass; the rest
  use the highpass.

## August 2026 changes

* Processing order changed. Slicing to the analysis window now happens after
  filtering rather than before, so filter and integration transients land in
  the discarded padding.
* `dcrequest_pctavailable`, `dcrequest_ngaps`, `dcrequest_segmentshort` and
  `dcrequest_segmentlong` are now measured over the clean hour rather than the
  3605.05 s analysis window. `dcrequest_ngaps` is now a real gap count rather
  than the number of returned segments minus one.
* `power_*` PSDs are now measured on the clean hour. They were previously
  measured on the hour starting 5.05 s before the top of the hour.
* PSD failures no longer reach SQUAC as -1.
* The ElarmS/EPIC boxcar rejection test now uses the signed range
  `max(x) - min(x)` rather than `max(|x|) - min(|x|)`.
* `rms__bp_above_.07` corrected to `rms_bp_above_.07` (single underscore).
* `prefix_ring_latency_max` added to this document.

## Metrics of measurement completeness at datacenters

| metric name | description | frequency | unit | threshold | old name |
|-------------|-------------|-----------|------|-----------|----------|
| [dcrequest_pctavailable](station_metrics/metrics/dcrequest_pctavailable.md) | Percentage of the requested hour of data returned via FDSN webservice. | once an hour | percent | 98.0 | pctavailable |
| [dcrequest_ngaps](station_metrics/metrics/dcrequest_ngaps.md) | Number of gaps in the hour of data returned via FDSN webservice. | once an hour | count | 1 | ngaps |
| [dcrequest_segmentshort](station_metrics/metrics/dcrequest_segmentshort.md) | Duration in seconds of the shortest continuous data segment in the hour returned by FDSN webservice. | once an hour | seconds | 1.0 | segmentshort |
| [dcrequest_segmentlong](station_metrics/metrics/dcrequest_segmentlong.md) | Duration in seconds of the longest continuous data segment in the hour returned by FDSN webservice. | once an hour | seconds | 3600.0 | segmentlong |

## General station quality metrics

| metric name | description | frequency | unit | threshold | old name |
|-------------|-------------|-----------|------|-----------|----------|
| [hourly_min](station_metrics/metrics/hourly_min.md) | Minimum raw sample value over the analysis window. | once an hour | counts | -1e9 | rawmin |
| [hourly_max](station_metrics/metrics/hourly_max.md) | Maximum raw sample value over the analysis window. | once an hour | counts | 1e9 | rawmax |
| [hourly_range](station_metrics/metrics/hourly_range.md) | Range of raw sample values over the analysis window. | once an hour | counts | 2e9 | rawrange |
| [hourly_mean](station_metrics/metrics/hourly_mean.md) | Mean raw sample value over the analysis window. | once an hour | counts | 1e8 | rawmean |
| [hourly_max_acc](station_metrics/metrics/hourly_max_acc.md) | Maximum absolute acceleration, highpassed at 0.075 Hz. | once an hour | cm/s^2 | 2.0 | accmax, accmaxHP |
| [hourly_max_bp_acc](station_metrics/metrics/hourly_max_bp_acc.md) | Maximum absolute acceleration, bandpassed 0.075 - 15 Hz. | once an hour | cm/s^2 | 2.0 | accmax |
| [hourly_noise_floor_acc](station_metrics/metrics/hourly_noise_floor_acc.md) | Approximate median envelope amplitude, from the half range of the 2nd to 98th percentile amplitudes. Acceleration highpassed at 0.075 Hz. | once an hour | cm/s^2 | 0.2 | NoiseFloorAccHP |
| [hourly_noise_floor_bp_acc](station_metrics/metrics/hourly_noise_floor_bp_acc.md) | Approximate median envelope amplitude, from the half range of the 2nd to 98th percentile amplitudes. Acceleration bandpassed 0.075 - 15 Hz. | once an hour | cm/s^2 | 0.2 | NoiseFloorAcc |
| [power_10Hz](station_metrics/metrics/power_10Hz.md) | Power spectral density at 10 Hz for the hour. Calculated locally with ObsPy PPSD. | once an hour | dB | 0 | pow10Hz |
| [power_5Hz](station_metrics/metrics/power_5Hz.md) | Power spectral density at 5 Hz for the hour. Calculated locally with ObsPy PPSD. | once an hour | dB | 0 | pow5Hz |
| [power_1Hz](station_metrics/metrics/power_1Hz.md) | Power spectral density at 1 Hz for the hour. Calculated locally with ObsPy PPSD. | once an hour | dB | 0 | pow1Hz |
| [power_5sec](station_metrics/metrics/power_5sec.md) | Power spectral density at 0.2 Hz for the hour. Calculated locally with ObsPy PPSD. | once an hour | dB | 0 | pow5sec |
| [power_40sec](station_metrics/metrics/power_40sec.md) | Power spectral density at 0.025 Hz for the hour. Calculated locally with ObsPy PPSD. | once an hour | dB | 0 | pow40sec |

## ShakeAlert station quality metrics

| metric name | description | frequency | unit | threshold | old name |
|-------------|-------------|-----------|------|-----------|----------|
| [rms_above_.07](station_metrics/metrics/rms_above_.07.md) | Seconds per hour that a 5 s sliding-window RMS exceeds 0.07 cm/s^2. Acceleration highpassed at 0.075 Hz. | once an hour | seconds | 60.0 | RMS0p07cmHP, RMSduration_0p07cmHP |
| [rms_bp_above_.07](station_metrics/metrics/rms_bp_above_.07.md) | Seconds per hour that a 5 s sliding-window RMS exceeds 0.07 cm/s^2. Acceleration bandpassed 0.075 - 15 Hz. | once an hour | seconds | 60.0 | RMS0p07cm, RMSduration_0p07cm, rms__bp_above_.07 |
| [acc_spikes_gt_.34](station_metrics/metrics/acc_spikes_gt_.34.md) | Times per hour that the STA/LTA exceeds 20 and the absolute acceleration exceeds 0.34 cm/s^2. Acceleration highpassed at 0.075 Hz. | once an hour | count | 1 | snr20_0p34cmHP |
| [acc_bp_spikes_gt_.34](station_metrics/metrics/acc_bp_spikes_gt_.34.md) | Times per hour that the STA/LTA exceeds 20 and the absolute acceleration exceeds 0.34 cm/s^2. Acceleration bandpassed 0.075 - 15 Hz. | once an hour | count | 1 | snr20_0p34cm |
| [acc_gt_2.0](station_metrics/metrics/acc_gt_2.0.md) | Times per hour that the absolute acceleration exceeds 2 cm/s^2, counted at most once every 30 s. Acceleration highpassed at 0.075 Hz. | once an hour | count | 10 | finder_2cm_hp |
| [approximate_epic_triggers](station_metrics/metrics/approximate_epic_triggers.md) | Approximate count of ElarmS3/EPIC triggers. Amplitude gates on data highpassed at 0.075 Hz. | once an hour | count | 60 | NTrigElarmSAlex |
| [approximate_epic_bp_triggers](station_metrics/metrics/approximate_epic_bp_triggers.md) | Approximate count of ElarmS3/EPIC triggers. Amplitude gates on data bandpassed 0.075 - 15 Hz. | once an hour | count | 60 | NTrigElarmSAlexBB, NTrigElarmSAlexBB15 |

## Latency and gap metrics from sniffwave_tally

These metrics come from sniffwave_tally (https://github.com/pnsn/sniffwave_tally)
run against an Earthworm wave ring at each participating institution. The
metric name carries a prefix identifying the server it was measured on, so the
same channel sniffed at two institutions produces two independent, uniquely
named measurements. Prefixes currently in SQUAC:

| prefix | server |
|--------|--------|
| export | PNSN export server (ewserver) |
| scsn | SCSN server pine |
| ucb | UC Berkeley server eew-bk-dev1 |
| menlo | USGS Menlo Park server |
| eewdev1 | ShakeAlert development server 1 |
| eewdev2 | ShakeAlert development server 2 |
| ews02 | ShakeAlert production server ews02 |

All seven require sniffwave_tally to be run with the `--all` flag, which is set
automatically when `--squac` is given.

| metric name | description | frequency | unit | threshold | old name |
|-------------|-------------|-----------|------|-----------|----------|
| [prefix_ring_latency](station_metrics/metrics/prefix_ring_latency.md) | Average data latency, defined as the time between the measurement and the end of the packet, plus half the packet length. | once every 10 minutes | seconds | 5.0 | |
| [prefix_ring_latency_max](station_metrics/metrics/prefix_ring_latency_max.md) | Largest single-packet latency seen during the measurement window. | once every 10 minutes | seconds | 5.0 | |
| [prefix_ring_latency_le_3.5](station_metrics/metrics/prefix_ring_latency_le_3.5.md) | Percentage of packets with data latency of 3.5 s or less. | once every 10 minutes | percent | 90.0 | pct_gt_3.5sec_late |
| [prefix_ring_gaps_per_hour](station_metrics/metrics/prefix_ring_gaps_per_hour.md) | Number of gaps seen in the wave ring during the measurement window, normalized to a per hour rate. | once every 10 minutes | count | 1 | |
| [prefix_ring_packet_length](station_metrics/metrics/prefix_ring_packet_length.md) | Average length of the Tracebuf2 packets seen. | once every 10 minutes | seconds | 5.0 | |
| [prefix_ring_completeness](station_metrics/metrics/prefix_ring_completeness.md) | Percentage of the measurement window for which data arrived. | once every 10 minutes | percent | 90.0 | |
| [prefix_ring_completeness_incl_gap_penalty](station_metrics/metrics/prefix_ring_completeness_incl_gap_penalty.md) | Percentage of the measurement window for which data arrived, subtracting an extra 30 s per gap. | once every 10 minutes | percent | 90.0 | |

## Metrics calculated outside this repository

These metrics exist in SQUAC but are produced by other software. Placeholder
pages exist for them; the algorithm sections are marked TODO and need to be
filled in by whoever owns the producing code.

| metric name | description | frequency | unit | threshold |
|-------------|-------------|-----------|------|-----------|
| [water_pump_time_per_hour](station_metrics/metrics/water_pump_time_per_hour.md) | Seconds each hour that the water pump is on, as recorded on the VE1/VE2 (SP1/SP2) channels. | once an hour | seconds | 0 |
| [mass_position](station_metrics/metrics/mass_position.md) | Sensor mass position state of health channel. | TODO | TODO | TODO |
| [system_temperature](station_metrics/metrics/system_temperature.md) | Datalogger or vault temperature state of health channel. | TODO | TODO | TODO |
| [epic_candidate_triggers](station_metrics/metrics/epic_candidate_triggers.md) | Number of hourly triggers from EPIC, including those eventually rejected or unassociated. | once an hour | count | TODO |
| [epic_rejected_triggers](station_metrics/metrics/epic_rejected_triggers.md) | Number of hourly EPIC triggers rejected for any reason. | once an hour | count | TODO |
| [epic_temporary_3sec_triggers](station_metrics/metrics/epic_temporary_3sec_triggers.md) | Number of hourly EPIC triggers valid for at least 3 s before being rejected. | once an hour | count | TODO |
| [epic_associated_triggers](station_metrics/metrics/epic_associated_triggers.md) | Hourly number of EPIC triggers associated with an event. | once an hour | count | 60 |
| [epic_unassociated_triggers](station_metrics/metrics/epic_unassociated_triggers.md) | Hourly number of EPIC triggers not associated with an event. | once an hour | count | 60 |
| [epic_trigger_latency_median](station_metrics/metrics/epic_trigger_latency_median.md) | Median latency of EPIC triggers. | TODO | seconds | TODO |
| [epic_trigger_latency_le_3.5](station_metrics/metrics/epic_trigger_latency_le_3.5.md) | Percentage of EPIC triggers with latency of 3.5 s or less. | TODO | percent | TODO |
| [epic_trigger_latency_max](station_metrics/metrics/epic_trigger_latency_max.md) | Maximum latency of EPIC triggers. | TODO | seconds | TODO |
| [prefix_ring_n_oo](station_metrics/metrics/prefix_ring_n_oo.md) | Number of out-of-order packets seen in the wave ring. | once every 10 minutes | count | TODO |
| [prefix_ring_oo_dur](station_metrics/metrics/prefix_ring_oo_dur.md) | Total duration of out-of-order packets seen in the wave ring. | once every 10 minutes | seconds | TODO |

The following metrics also exist in SQUAC and are documented only by the rows
below. They are produced entirely outside this repository and have no detail
pages.

| metric name | description | frequency | unit | threshold |
|-------------|-------------|-----------|------|-----------|
| daily_ci_finder_triggers | Daily number of FinDer triggers from eew-ci-test1. From https://service.scedc.caltech.edu/station/triggerreport.php. | once a day | count | 240 |
| daily_ci_l2z | L2Z latency from eew-ci-test1. From https://service.scedc.caltech.edu/station/triggerreport.php. | once a day | seconds | 5.0 |
| daily_ci_paclen | Packet lengths from eew-ci-test1. From https://service.scedc.caltech.edu/station/triggerreport.php. | once a day | seconds | 5.0 |
| daily_ci_epic_associated_triggers | Daily number of associated EPIC triggers from eew-ci-test1. | once a day | count | 24 |
| daily_ci_epic_unassociated_triggers | Daily number of unassociated EPIC triggers from eew-ci-test1. | once a day | count | 1440 |
| daily_aqms_p_arrivals | Daily number of P arrivals used for events in AQMS at SCSN. | once a day | count | 24 |
| distance_nearest_shakealert_station | Distance to the nearest other ShakeAlert station. Z channels only. | once a day | km | 100 |
| distance_second_nearest_shakealert_station | Distance to the second nearest other ShakeAlert station. Z channels only. | once a day | km | 100 |
| distance_third_nearest_shakealert_station | Distance to the third nearest other ShakeAlert station. Z channels only. | once a day | km | 100 |
| distance_fourth_nearest_shakealert_station | Distance to the fourth nearest other ShakeAlert station. Z channels only. | once a day | km | 100 |
| distance_fifth_nearest_shakealert_station | Distance to the fifth nearest other ShakeAlert station. Z channels only. | once a day | km | 100 |
| broadband_sensor_supply_current | Broadband sensor supply current state of health channel. | TODO | TODO | TODO |
| Multipath L1 | GNSS L1 multipath. | TODO | TODO | TODO |
| Multipath L2 | GNSS L2 multipath. | TODO | TODO | TODO |

## Contact

squac-help@uw.edu

