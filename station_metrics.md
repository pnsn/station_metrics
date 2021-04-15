# Station quality metrics
All the metrics listed below are calculated from data archived at their
respective permanent archives (IRIS DMC for PNSN data, NCEDC for NCSN data,
SCEDC for SCSN data) and requested using FDSN web services. The metrics of
completeness give an indication of how successful the collection of the data
from their respective data archives was using FDSN dataselect and may not always
accurately represent what is stored at the respective archives.

## Metrics of measurement completeness at datacenters
| metric name | description | frequency | unit | threshold | old name |
|-------------|-------------|-----------|------|-----------|----------|
| dcrequest_pctavailable | Percentage of data returned of 1 hour of data requested via FDSN webservice. | once an hour | percentage | 98.0 | pctavailable |
| dcrequest_ngaps | Number of gaps in data returned of 1 hour of data requested via FDSN webservice. | once an hour | count | 1 | ngaps |
| dcrequest_segmentshort | Duration in seconds of the shortest data segment in 1 hour of data requested as returned by FDSN webservice. | once an hour | seconds | 1.0 | segmentshort |
| dcrequest_segmentlong | Duration in seconds of the longest data segment in 1 hour of data requested as returned by FDSN webservice. | once an hour | seconds | 3600.0 | segmentlong |

## General station quality metrics
| metric name | description | frequency | unit | threshold | old name |
|-------------|-------------|-----------|------|-----------|----------|
| hourly_min | Hourly min of raw data. | once an hour | counts | -1e9 | rawmin |
| hourly_max | Hourly max of raw data. | once an hour | counts | 1e9 | rawmax |
| hourly_range | Hourly range of raw data. | once an hour | counts | 2e9 | rawrange |
| hourly_mean | Hourly mean of raw data. | once an hour | counts | 1e8 | rawmean |
| hourly_max_acc | Hourly maximum acceleration highpassed at 0.075 Hz. | once an hour | cm/s^2 | 2.0 | accmax |
| hourly_max_bp_acc | Hourly maximum acceleration bandpassed 0.075 - 15 Hz. | once an hour | cm/s^2 | 2.0 | accmax |
| hourly_noise_floor_acc | Approximation of the median envelope amplitude by using the half range of the 2nd to 98th percentile amplitudes.  Uses acceleration data highpassed at 0.075 Hz. | once an hour | cm/s^2 | 0.2 | NoiseFloorAcc |
| hourly_noise_floor_bp_acc | Approximation of the median envelope amplitude by using the half range of the 2nd to 98th percentile amplitudes.  Uses acceleration data bandpassed 0.075 - 15 Hz. | once an hour | cm/s^2 | 0.2 | NoiseFloorAcc |
| power_10Hz | Hourly power in db at 10 Hz. From IRIS MUSTANG. | once an hour | dB | 0 | |
| power_5Hz | Hourly power in db at 5 Hz. From IRIS MUSTANG. | once an hour | dB | 0 | pow5Hz |
| power_1Hz | Hourly power in db at 1 Hz. From IRIS MUSTANG. | once an hour | dB | 0 | pow1Hz |
| power_5sec | Hourly power in db at 0.2 Hz. From IRIS MUSTANG. | once an hour | dB | 0 | pow5sec |
| power_40sec | Hourly power in db at 0.025 Hz. From IRIS MUSTANG. | once an hour | dB | 0 | |

## ShakeAlert station quality metrics
| metric name | description | frequency | unit | threshold | old name |
|-------------|-------------|-----------|------|-----------|----------|
| rms_above_.07 | Number of seconds per hour that the rms calculated over a 5 second sliding window exceeds 0.07 cm/s^2. Uses highpass data 0.075 Hz. | once an hour | seconds | 60.0 | RMS0p07cmHP or RMSduration_0p07cmHP |
| rms__bp_above_.07 | Number of seconds per hour that the rms calculated over a 5 second sliding window exceeds 0.07 cm/s^2. Uses bandpass data 0.075 - 15 Hz. | once an hour | seconds | 60.0 | RMS0p07cm or RMSduration_0p07cm|
| acc_spikes_gt_.34 | Times per hour that STA/LTA > 20 and abs(Acc) > 0.34 cm/s^2.  Uses highpass data 0.075 Hz. | once an hour| count| 1 | snr20_0p34cmHP
| acc_bp_spikes_gt_.34 | Times per hour that STA/LTA > 20 and abs(Acc) > 0.34 cm/s^2.  Uses bandpass data 0.075 - 15 Hz. | once an hour| count| 1 | snr20_0p34cm
| acc_gt_2.0 | Times per hour that acceleration sample exceeds 2 cm/s^2, minimum of 30 s between samples. Uses highpass data 0.075 Hz. | once an hour | count | 10 | finder_2cm_hp
|approximate_epic_triggers | Approximation to number of ElarmS3/EPIC triggers using only vertical component data. All data examined are sensitivity corrected and highpass filtered above 0.075 Hz. Triggers occur when the STA/LTA exceed 20 on the velocity trace using STA/LTA lengths of 0.05/5.0 sec. Minimum time between triggers must be at least 10 sec. Peak amplitude within 4 sec of trigger must greater than 0.0031623 cm/s^2 on the acceleration trace, between 0.000000031623 - 10 m/s on the velocity trace and 0.000000031623 to 31.623 m on the displacement trace. (A. I. Chung et al., SRL March/April 2019) | once an hour | count | 60 |NTrigElarmSAlex |
|approximate_epic_bp_triggers | Approximation to number of ElarmS3/EPIC triggers using only vertical component data. All data examined are sensitivity corrected and highpass filtered above 0.075 Hz. Triggers occur when the STA/LTA exceed 20 on the velocity trace using STA/LTA lengths of 0.05/5.0 sec. Minimum time between triggers must be at least 10 sec. Peak amplitude within 4 sec of trigger must greater than 0.0031623 cm/s^2 on the acceleration trace, between 0.000000031623 - 10 m/s on the velocity trace and 0.000000031623 to 31.623 m on the displacement trace. (A. I. Chung et al., SRL March/April 2019) | once an hour | count | 60 |NTrigElarmSAlexBB15 |
| daily_ci_finder_triggers | Daily number of FinDer triggers from eew-ci-test1. From https://service.scedc.caltech.edu/station/triggerreport.php. | once a day | count | 240 | |
| daily_ci_l2z | L2Z latency from eew-ci-test1. From https://service.scedc.caltech.edu/station/triggerreport.php. | once a day | seconds | 5.0 | |
| daily_ci_paclen | Packet lengths from eew-ci-test1. From https://service.scedc.caltech.edu/station/triggerreport.php. | once a day | seconds | 5.0 | |
| daily_ci_epic_associated_triggers | Daily number of associated (with an event) EPIC triggers from eew-ci-test1. From https://service.scedc.caltech.edu/station/triggerreport.php. | once a day | count | 24 | |
| daily_ci_epic_unassociated_triggers | Daily number of unassociated (with an event) EPIC triggers from eew-ci-test1. From https://service.scedc.caltech.edu/station/triggerreport.php. | once a day | count | 1440 | |
| daily_aqms_p_arrivals | Daily number of P-arrivals used for events in AQMS at SCSN. From https://service.scedc.caltech.edu/station/triggerreport.php. | once a day | count | 24 | |
| epic_associated_triggers | Hourly number of unassociated (with an event) triggers from EPIC. From eew-bk-dev1. | once an hour | count | 60 | |
| epic_unassociated_triggers | Hourly number of unassociated (with an event) triggers from EPIC. From eew-bk-dev1. | once an hour | count | 60 | |

## Latency and gap metrics from sniffwave_tally
These latency and gap metrics are from sniffwave_tally (https://github.com/pnsn/sniffwave_tally) run at the four different EEW institutions.  "prefix" varies by institution: export = PNSN export server (ewserver), ci = SCSN server pine, ucb = UCB server eew-bk-dev1, menlo = MENLO server.  Note: most channels are sniffwave_tally-ed at only one institution though a few are sniffed at more than one; either way, they will be unique measurements because of the unique prefix in the metric name.
| metric name | description | frequency | unit | threshold | old name |
|-------------|-------------|-----------|------|-----------|----------|
| prefix_ring_latency | Latency as defined by time between measurement end of packet plus half of packet length, measured for 10 minutes and averaged. | once every 10 minutes | seconds | 5.0 | |
| prefix_ring_latency_le_3.5 | Percentage of packets with data latency less than 3.5s. | once every 10 minutes | percent | 90.0 | pct_gt_3.5sec_late |
| prefix_ring_gaps_per_hour | Number of gaps in WAVE_RING on server during time window, normalized to per hour. | once every 10 minutes | count | 1 | |
| prefix_ring_packet_length | Average length of Tracebuf2 packet. | once every 10 minutes | seconds | 5.0 | |
| prefix_ring_completeness | Percentage of measurement time window for which data exists. | once every 10 minutes | percent | 90.0 | |
| prefix_ring_completeness_incl_gap_penalty | Percentage of measurement time window for which data exists, subtracting extra 30s for each data gap. | once every 10 minutes | percent | 90.0 | |
