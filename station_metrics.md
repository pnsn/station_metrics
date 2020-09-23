# Station quality metrics
All the metrics listed below are calculated from data archived at their
respective permanent archives (IRIS DMC for PNSN data, NCEDC for NCSS data,
SCEDC for SCSN data) and requested using FDSN web services. The metrics of
completeness give an indication of how successful the collection of the data
from their respective data archives was using FDSN dataselect and may not always
accurately represent what is stored at the respective archives.

## Metrics of measurement completeness

| metric name | description | frequency | unit | threshold | old name |
|-------------|-------------|-----------|------|-----------|----------|
| dcrequest_pctavailable | Percentage of data returned of 1 hour of data requested via FDSN webservice. | once an hour | percentage | 90.0 | pctavailable |
| dcrequest_ngaps | Number of gaps in data returned of 1 hour of data requested via FDSN webservice. | once an hour | count | 10 | ngaps |
| dcrequest_segmentshort | Duration in seconds of the shortest data segment of 1 hour of data requested as returned by FDSN webservice. | once an hour | seconds | 1 | segmentshort |
| dcrequest_segmentlong | Duration in seconds of the longest data segment of 1 hour of data requested as returned by FDSN webservice. | once an hour | seconds | 1 | segmentlong |

## ShakeAlert Station Quality Metrics
### Phase 1
| metric name | description | frequency | unit | threshold | old name |
|-------------|-------------|-----------|------|-----------|----------|
| rms_above_.07 | Number of seconds per hour that the rms calculated over a 5 second sliding window exceeds 0.07 cm/s^2. Uses highpass data 0.075 Hz. | once an hour | seconds | 60.0 | RMS0p07cmHP or RMSduration_0p07cmHP |
| rms__bp_above_.07 | Number of seconds per hour that the rms calculated over a 5 second sliding window exceeds 0.07 cm/s^2. Uses bandpass data 0.075 - 15 Hz. | once an hour | seconds | 60.0 | RMS0p07cm or RMSduration_0p07cm|
| acc_spikes_gt_.34 | Times per hour that STA/LTA > 20 and abs(Acc) > 0.34 cm/s^2.  Uses highpass data 0.075 Hz. | once an hour| count| 1 | snr20_0p34cmHP
| acc_bp_spikes_gt_.34 | Times per hour that STA/LTA > 20 and abs(Acc) > 0.34 cm/s^2.  Uses bandpass data 0.075 - 15 Hz. | once an hour| count| 1 | snr20_0p34cm
| acc_gt_2.0 | Times per hour that acceleration sample exceeds 2 cm/s^2, minimum of 30 s between samples. Uses highpass data 0.075 Hz. | once an hour | count | 10 | finder_2cm_hp
|approximate_epic_triggers | Approximation to number of ElarmS3/EPIC triggers using only vertical component data. All data examined are sensitivity corrected and highpass filtered above 0.075 Hz. Triggers occur when the STA/LTA exceed 20 on the velocity trace using STA/LTA lengths of 0.05/5.0 sec. Minimum time between triggers must be at least 10 sec. Peak amplitude within 4 sec of trigger must greater than 0.0031623 cm/s^2 on the acceleration trace, between 0.000000031623 - 10 m/s on the velocity trace and 0.000000031623 to 31.623 m on the displacement trace. (A. I. Chung et al., SRL March/April 2019) | once an hour | count | 100 |NTrigElarmSAlex |
|approximate_epic_bp_triggers | Approximation to number of ElarmS3/EPIC triggers using only vertical component data. All data examined are sensitivity corrected and highpass filtered above 0.075 Hz. Triggers occur when the STA/LTA exceed 20 on the velocity trace using STA/LTA lengths of 0.05/5.0 sec. Minimum time between triggers must be at least 10 sec. Peak amplitude within 4 sec of trigger must greater than 0.0031623 cm/s^2 on the acceleration trace, between 0.000000031623 - 10 m/s on the velocity trace and 0.000000031623 to 31.623 m on the displacement trace. (A. I. Chung et al., SRL March/April 2019) | once an hour | count | 100 |NTrigElarmSAlexBB15 |
| export_ring_latency_le_3.5 | Percentage of packets with data latency less than 3.5s. | once every 10 minutes | percent | 90.0 | pct_gt_3.5sec_late |

### Phase 2

## General Station Quality metrics
| metric name | description | frequency | unit | threshold | old name |
|-------------|-------------|-----------|------|-----------|----------|
| hourly_min | Hourly min of raw data. | once an hour | counts | -1e9 | rawmin |
| hourly_max | Hourly max of raw data. | once an hour | counts | 1e9 | rawmax |
| hourly_range | Hourly range of raw data. | once an hour | counts | 2e9 | rawrange |
| hourly_mean | Hourly mean of raw data. | once an hour | counts | 1e8 | rawmean |
| hourly_max_bp_acc | Hourly maximum acceleration bandpassed 0.075 - 15 Hz. | once an hour | cm/s^2 | 2 | accmax |
| hourly_noise_floor_bp_acc | Approximation of the median envelope amplitude by using the half range of the 2nd to 98th percentile amplitudes.  Uses acceleration data bandpassed 0.075 - 15 Hz. | once an hour | cm/s^2 | 1 | NoiseFloorAcc |
| power_5Hz | Hourly power in db at 5 Hz. | once an hour | db | 0 | pow5Hz |
| power_1Hz | Hourly power in db at 1 Hz. | once an hour | db | 0 | pow1Hz |
| power_0.2Hz | Hourly power in db at 0.2 Hz. | once an hour | db | 0 | pow5sec |

