#!/home/seis/miniconda3/envs/squac/bin/python

"""
Calculate hourly station-quality metrics and upload them to SQUAC.

For each channel in a channel file this fetches an hour of waveform data plus
padding, converts it to ground motion, measures a fixed set of quality metrics
and posts them to SQUAC.  The metrics are documented in station_metrics.md and
in the per-metric pages under metrics/.

Usage
-----
    calculate_station_metrics.py --starttime 2026-08-13T02:00:00
    calculate_station_metrics.py --starttime 2026-08-13T02 \\
        --chanfile chanfile.RSN.5 --datacenter IRIS --upload-chunksize 20
    calculate_station_metrics.py --starttime 2026-08-13T02:00:00 --no-squac

Requires the environment variables SQUACAPI_USER and SQUACAPI_PASSWD unless
--no-squac is given.

Time windows
------------
Two windows are in play and they are not the same length.

* The **analysis window** runs from ``starttime - (STA + LTA)`` to
  ``starttime + duration``, i.e. 3605.05 s for a one-hour run.  The extra
  5.05 s at the front is there so the STA/LTA function has already converged by
  the time the hour begins; without it the first few seconds of every hour
  would produce spurious triggers.  Every time-domain metric (amplitudes, noise
  floors, RMS durations, trigger counts) is measured over this 3605.05 s.
* The **reporting window** written to SQUAC is the clean hour, ``starttime`` to
  ``starttime + duration``.  The completeness metrics
  (dcrequest_pctavailable, dcrequest_ngaps, dcrequest_segmentshort,
  dcrequest_segmentlong) and the PSD powers are measured over this hour only.

On top of that, waveforms are requested with 120 s of padding either side of
the analysis window.  The padding is never measured; it exists so that
integration drift and filter start-up transients fall outside the window that
is measured.

Filtering
---------
* STA/LTA trigger trace: velocity, highpassed at 3 Hz.  The high corner keeps
  microseism and long-period noise out of the trigger function.
* Amplitude, RMS and noise-floor measurements: acceleration (and, for the EPIC
  approximation, velocity and displacement) either highpassed at 0.075 Hz or
  bandpassed 0.075 - 15 Hz.  Metrics carrying "bp" in their SQUAC name use the
  bandpass; the others use the highpass.

All filters are causal Butterworth with 2 corners, matching ShakeAlert
practice.

Change log
----------
Aug 2026: processing order changed.  It was detrend -> demean -> remove
          sensitivity -> slice -> integrate/differentiate -> filter -> demean;
          slicing now happens after the filter, so the 120 s padding absorbs
          the integration and filter transients.
Aug 2026: dcrequest_pctavailable numerator was the sample count over the whole
          3605.05 s analysis window, so it read above 100% on a complete hour.
          It is now the sample count inside the clean hour only.
Aug 2026: dcrequest_ngaps was the number of returned trace segments minus one,
          counted over the analysis window.  It is now a real gap count inside
          the clean hour, from Stream.get_gaps.
Aug 2026: dcrequest_segmentshort and dcrequest_segmentlong are measured on
          segments clipped to the clean hour, not the analysis window.
Aug 2026: PSD was run on the 3605.05 s analysis window, and PPSD's one-hour
          segmenting therefore measured the hour starting 5.05 s before the
          top of the hour.  It now runs on the clean hour.
Aug 2026: PSD failures used to reach SQUAC as -1.  get_power now returns None
          on failure, and powers are only uploaded when all five values are
          below -1 dB, which is the range real PSD values occupy (-180 to -50).
Aug 2026: the ElarmS/EPIC boxcar rejection test now uses the signed range
          max(x) - min(x) rather than max(|x|) - min(|x|).
Aug 2026: start time is a command-line argument rather than a hard-coded date.
Aug 2026: uploads can be batched over several channels; see --upload-chunksize.
Aug 2026: unused metric variants (different thresholds, 10/20/25 Hz bandpass
          corners, full-response removal, plotting, trigger-time log files)
          were removed.
"""

import argparse
import datetime
import os
import sys
import time
import timeit
import warnings

import numpy as np
from obspy import Stream, UTCDateTime
from obspy.clients.fdsn import Client
from obspy.signal.trigger import classic_sta_lta

from get_data_metadata4 import (download_metadata_fdsn,
                                download_waveforms_fdsn_bulk,
                                raw_trace_to_ground_motion,
                                slice_trace)
from noise_metrics import (count_peaks_stalta, count_peaks_stalta_Elarms,
                           count_triggers_FinDer, duration_exceed_RMS,
                           get_power, noise_floor)

# These warnings are routine for this dataset and would otherwise generate an
# email per channel from cron.
warnings.filterwarnings("ignore", message=".*bandpass is at or above Nyquist.*")
warnings.filterwarnings("ignore", message=".*computed and reported sensitivities differ.*")
warnings.filterwarnings("ignore", message=".*FIR normalized.*")
warnings.filterwarnings("ignore", message=".*Error getting response from provided metadata.*")
warnings.filterwarnings("ignore", message=".*units mismatch between stages.*")
warnings.filterwarnings("ignore", message=".*EVRESP.*")
warnings.filterwarnings("ignore", message=".*norm_resp.*")
warnings.filterwarnings("ignore", category=UserWarning, module="obspy")

try:
    from squacapi_client.models.write_only_measurement_serializer \
        import WriteOnlyMeasurementSerializer
    from squacapi_client.pnsn_utilities \
        import get_client, make_channel_map, perform_bulk_create
    no_squacapi = False
except Exception:
    print("Info: squacapi_client not available, cannot upload to SQUAC")
    no_squacapi = True


# ---------------------------------------------------------------------------
# Processing parameters
# ---------------------------------------------------------------------------
STA = 0.05            # s, short-term average window for the trigger function
LTA = 5.0             # s, long-term average window for the trigger function
STALTA_THRESHOLD = 20  # STA/LTA ratio at which a trigger is declared
MPD = 10.0            # s, dead time between counted triggers
TWIN = 4.0            # s, window after a trigger in which amplitude is measured
RMSLEN = 5.0          # s, sliding window for the RMS duration metrics
PADDING = 120.0       # s, requested either side of the analysis window

FREQ_STALTA_HP = 3.0   # Hz, highpass for the velocity STA/LTA trigger trace
FREQ_HP = 0.075        # Hz, highpass corner for the amplitude traces
FREQ_BP_LOW = 0.075    # Hz, bandpass low corner for the amplitude traces
FREQ_BP_HIGH = 15.0    # Hz, bandpass high corner for the amplitude traces

# Amplitude thresholds, SI units.  0.0034 m/s^2 = 0.34 cm/s^2 and
# 0.0007 m/s^2 = 0.07 cm/s^2 are the 2018 ShakeAlert station acceptance
# thresholds; 0.02 m/s^2 = 2 cm/s^2 is the FinDer amplitude threshold.
ACC_SPIKE_THRESHOLD = 0.0034
RMS_THRESHOLD = 0.0007
FINDER_THRESHOLD = 0.02
FINDER_DEADTIME = 30.0   # s between counted FinDer excursions

# PSD periods, in the order the corresponding SQUAC metrics are listed in
# PSD_METRICS below.  0.1 s = 10 Hz, 0.2 s = 5 Hz, 1 s = 1 Hz.
PSD_PERIODS = [0.1, 0.2, 1.0, 5.0, 40.0]
PSD_METRICS = ["power_10Hz", "power_5Hz", "power_1Hz", "power_5sec",
               "power_40sec"]
# Real PSD values run roughly -180 to -50 dB.  Anything at or above this is a
# failure, not a measurement, and is not uploaded.
PSD_MAX_VALID = -1.0

# ---------------------------------------------------------------------------
# The single mapping from metric name to SQUAC metric id.  Every metric this
# script computes and uploads appears here exactly once; nothing is uploaded
# that is not in this dictionary.
# ---------------------------------------------------------------------------
SQUAC_METRIC_IDS = {
    "hourly_min": 82,
    "hourly_max": 83,
    "hourly_mean": 84,
    "hourly_range": 85,
    "acc_gt_2.0": 86,
    "rms_bp_above_.07": 87,
    "rms_above_.07": 88,
    "acc_bp_spikes_gt_.34": 89,
    "acc_spikes_gt_.34": 90,
    "approximate_epic_triggers": 91,
    "approximate_epic_bp_triggers": 92,
    "hourly_noise_floor_bp_acc": 93,
    "hourly_max_bp_acc": 94,
    "dcrequest_pctavailable": 95,
    "dcrequest_ngaps": 96,
    "dcrequest_segmentshort": 97,
    "dcrequest_segmentlong": 98,
    "power_5Hz": 99,
    "power_1Hz": 100,
    "power_5sec": 101,
    "hourly_max_acc": 109,
    "hourly_noise_floor_acc": 110,
    "power_40sec": 111,
    "power_10Hz": 112,
}


def parse_arguments():
    """
    Read the command line.

    :rtype: :class:`argparse.Namespace`
    :return: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Calculate hourly station quality metrics and upload "
                    "them to SQUAC.")
    parser.add_argument("--starttime", required=True,
                        help="Start of the hour to analyze, UTC, as "
                             "YYYY-MM-DDTHH or YYYY-MM-DDTHH:MM:SS")
    parser.add_argument("--chanfile", default="chanfile.RSN.5",
                        help="File listing the channels to analyze "
                             "(default: chanfile.RSN.5)")
    parser.add_argument("--datacenter", default="IRIS",
                        help="FDSN data centre name or base URL "
                             "(default: IRIS)")
    parser.add_argument("--duration", type=float, default=3600.0,
                        help="Length of the reporting window in seconds "
                             "(default: 3600)")
    parser.add_argument("--channel-map", default="channels_squacids_west_coast",
                        help="File mapping NSLC to SQUAC channel id.  If it is "
                             "missing or yields no pairs, the SQUAC API is "
                             "used instead.")
    parser.add_argument("--upload-chunksize", type=int, default=1,
                        help="Number of channels to accumulate before posting "
                             "to SQUAC (default: 1, i.e. post per channel)")
    parser.add_argument("--no-squac", action="store_true",
                        help="Calculate and print metrics without uploading")

    return parser.parse_args()


def parse_starttime(text):
    """
    Turn a command-line start time into a datetime.

    :type text: str
    :param text: ``YYYY-MM-DDTHH`` or ``YYYY-MM-DDTHH:MM:SS``.
    :rtype: :class:`datetime.datetime`
    :return: The parsed time, treated as UTC.
    """
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%dT%H"):
        try:
            return datetime.datetime.strptime(text, fmt)
        except ValueError:
            continue

    raise ValueError("could not parse start time '" + text + "', expected "
                     "YYYY-MM-DDTHH or YYYY-MM-DDTHH:MM:SS")


def load_channel_map(channel_map_file, squac_client):
    """
    Build the NSLC to SQUAC channel-id lookup.

    The file has one channel per line, NSLC first and the SQUAC channel id
    second; anything after that is ignored::

        AZ.PFO.--.HHZ 12345 2014-11-15T00:15:00 2599-12-31T23:59:59 33.6117 -116.4594 100.0 1259.0

    If the file is missing, unreadable, or yields no usable pairs, the map is
    fetched from the SQUAC API instead.

    :type channel_map_file: str
    :param channel_map_file: Path to the channel map file.
    :type squac_client: object
    :param squac_client: Open SQUAC API client, or None.
    :rtype: dict
    :return: Mapping of NSLC string to integer SQUAC channel id.
    """
    channel_map = {}

    if channel_map_file is not None and os.path.isfile(channel_map_file):
        f = open(channel_map_file)
        for line in f.readlines():
            fields = line.split()
            if len(fields) < 2:
                continue
            try:
                channel_map[fields[0]] = int(fields[1])
            except ValueError:
                continue   # header, comment, or malformed line
        f.close()
        print("Read {} channel ids from {}".format(len(channel_map),
                                                   channel_map_file))

    if len(channel_map) == 0 and squac_client is not None:
        print("No channel ids read from file, falling back to the SQUAC API")
        channel_map = make_channel_map(squac_client.api_nslc_channels_list())
        print("Read {} channel ids from the SQUAC API".format(len(channel_map)))

    return channel_map


def sncl_string(trace):
    """
    NSLC string for a trace, with a blank location code written as ``--``.

    :type trace: :class:`obspy.core.trace.Trace`
    :param trace: Any trace.
    :rtype: str
    :return: e.g. ``UW.BABE.--.HHZ``.
    """
    loc = trace.stats.location
    if loc == "":
        loc = "--"

    return "{}.{}.{}.{}".format(trace.stats.network, trace.stats.station,
                                loc, trace.stats.channel)


def group_traces_by_sncl(traces):
    """
    Collect a flat list of traces into one stream per channel.

    A channel with gaps comes back from the data centre as several traces; they
    all belong to the same measurement and are concatenated later.

    :type traces: list
    :param traces: List of :class:`obspy.core.trace.Trace`.
    :rtype: dict
    :return: Mapping of NSLC string to :class:`obspy.core.stream.Stream`.
    """
    streams = {}
    for trace in traces:
        sncl = sncl_string(trace)
        if sncl not in streams:
            streams[sncl] = Stream()
        streams[sncl].append(trace)

    return streams


def calculate_metrics_for_channel(stream, inventory, starttime, endtime,
                                  time1, time2, duration):
    """
    Measure every metric for one channel.

    :type stream: :class:`obspy.core.stream.Stream`
    :param stream: All raw traces for a single channel, padded either side of
        the analysis window.
    :type inventory: :class:`obspy.core.inventory.inventory.Inventory`
    :param inventory: Station metadata at ``level='response'``.
    :type starttime: :class:`datetime.datetime`
    :param starttime: Start of the reporting hour.
    :type endtime: :class:`datetime.datetime`
    :param endtime: End of the reporting hour.
    :type time1: :class:`datetime.datetime`
    :param time1: Start of the analysis window, ``starttime - (STA + LTA)``.
    :type time2: :class:`datetime.datetime`
    :param time2: End of the analysis window, same as ``endtime``.
    :type duration: float
    :param duration: Length of the reporting hour in seconds.
    :rtype: dict or None
    :return: Metric name to value, keyed on SQUAC metric names, or None if
        there was nothing measurable.
    """
    dt = stream[0].stats.delta
    channel = stream[0].stats.channel

    # Concatenated data over the analysis window, one array per filter band.
    data_raw = []
    data_acc_hp = []
    data_vel_hp = []
    data_dis_hp = []
    data_acc_bp = []
    data_vel_bp = []
    data_dis_bp = []
    data_stalta = []

    # Segments clipped to the reporting hour, used for the completeness metrics.
    stream_hour = Stream()
    npts_in_hour = 0
    powers = None

    for trace in stream:
        trace_raw = slice_trace(trace, time1, time2)
        if trace_raw.stats.npts <= 1:
            continue

        # Third-order polynomial detrend over the padded segment, before any
        # gain removal or integration.  This is what takes out slow instrument
        # drift that would otherwise be amplified by integration.
        trace_padded = trace.copy()
        trace_padded.detrend(type='polynomial', order=3)

        trace_stalta = raw_trace_to_ground_motion(
            trace_padded, time1, time2, "VEL", FREQ_STALTA_HP, 0, inventory)
        trace_acc_hp = raw_trace_to_ground_motion(
            trace_padded, time1, time2, "ACC", FREQ_HP, 0, inventory)
        trace_vel_hp = raw_trace_to_ground_motion(
            trace_padded, time1, time2, "VEL", FREQ_HP, 0, inventory)
        trace_dis_hp = raw_trace_to_ground_motion(
            trace_padded, time1, time2, "DIS", FREQ_HP, 0, inventory)
        trace_acc_bp = raw_trace_to_ground_motion(
            trace_padded, time1, time2, "ACC", FREQ_BP_LOW, FREQ_BP_HIGH,
            inventory)
        trace_vel_bp = raw_trace_to_ground_motion(
            trace_padded, time1, time2, "VEL", FREQ_BP_LOW, FREQ_BP_HIGH,
            inventory)
        trace_dis_bp = raw_trace_to_ground_motion(
            trace_padded, time1, time2, "DIS", FREQ_BP_LOW, FREQ_BP_HIGH,
            inventory)

        data_raw = np.concatenate((data_raw, trace_raw.data), axis=0)
        data_acc_hp = np.concatenate((data_acc_hp, trace_acc_hp.data), axis=0)
        data_vel_hp = np.concatenate((data_vel_hp, trace_vel_hp.data), axis=0)
        data_dis_hp = np.concatenate((data_dis_hp, trace_dis_hp.data), axis=0)
        data_acc_bp = np.concatenate((data_acc_bp, trace_acc_bp.data), axis=0)
        data_vel_bp = np.concatenate((data_vel_bp, trace_vel_bp.data), axis=0)
        data_dis_bp = np.concatenate((data_dis_bp, trace_dis_bp.data), axis=0)

        # STA/LTA on the 3 Hz highpassed velocity.  A segment shorter than the
        # STA plus LTA cannot produce a meaningful ratio, so it contributes
        # zeros and simply never triggers.
        if trace_raw.stats.npts * dt > (STA + LTA):
            stalta = classic_sta_lta(trace_stalta.data, int(STA / dt),
                                     int(LTA / dt))
        else:
            stalta = np.zeros(trace_stalta.stats.npts)
        data_stalta = np.concatenate((data_stalta, stalta), axis=0)

        # Completeness bookkeeping, on the reporting hour only.
        trace_hour = slice_trace(trace, starttime, endtime)
        if trace_hour.stats.npts > 1:
            stream_hour.append(trace_hour)
            npts_in_hour = npts_in_hour + trace_hour.stats.npts

        # PSD, on the reporting hour only.  Only a segment spanning the whole
        # hour can produce a PPSD segment, and only the first such segment is
        # used; a channel with a gap in the hour gets no PSD.
        if powers is None and (trace_hour.stats.npts - 1) * dt >= duration:
            try:
                powers = get_power(trace_hour.copy(), inventory, PSD_PERIODS)
            except Exception as e:
                print("PSD failed for {}: {}".format(sncl_string(trace), e))
                powers = None

    if len(data_raw) == 0:
        return None

    # ---- Completeness of the reporting hour --------------------------------
    # Slices include both endpoints plus one extra sample, so a complete hour
    # reads a few thousandths of a percent above 100.  That is expected.
    pctavailable = 100. * npts_in_hour / (duration / dt)

    ngaps = 0
    segmentshort = 9e6
    segmentlong = 0
    if len(stream_hour) > 0:
        for gap in stream_hour.get_gaps():
            if gap[6] > 0:      # positive delta is a gap; negative is overlap
                ngaps = ngaps + 1
        for trace_hour in stream_hour:
            seglen = trace_hour.stats.npts * dt
            segmentshort = min(segmentshort, seglen)
            segmentlong = max(segmentlong, seglen)

    # ---- Raw counts --------------------------------------------------------
    rawmin = float(min(data_raw))
    rawmax = float(max(data_raw))
    rawmean = float(np.mean(data_raw))
    rawrange = float(np.ptp(data_raw))

    # ---- Amplitudes and noise floors, converted from SI to cm --------------
    accmax_hp = max(abs(data_acc_hp)) * 100.
    accmax_bp = max(abs(data_acc_bp)) * 100.
    noisefloor_acc_hp = noise_floor(data_acc_hp) * 100.
    noisefloor_acc_bp = noise_floor(data_acc_bp) * 100.

    # ---- RMS durations -----------------------------------------------------
    rms_hp = duration_exceed_RMS(data_acc_hp, RMS_THRESHOLD, RMSLEN, dt)
    rms_bp = duration_exceed_RMS(data_acc_bp, RMS_THRESHOLD, RMSLEN, dt)

    # ---- Spike counts ------------------------------------------------------
    spikes_hp = count_peaks_stalta(data_acc_hp, data_stalta, STA, LTA, MPD,
                                   STALTA_THRESHOLD, dt, TWIN,
                                   ACC_SPIKE_THRESHOLD)
    spikes_bp = count_peaks_stalta(data_acc_bp, data_stalta, STA, LTA, MPD,
                                   STALTA_THRESHOLD, dt, TWIN,
                                   ACC_SPIKE_THRESHOLD)

    # ---- EPIC trigger approximations ---------------------------------------
    epic_hp, boxcars_hp = count_peaks_stalta_Elarms(
        data_acc_hp, data_vel_hp, data_dis_hp, data_stalta, STA, LTA, MPD,
        STALTA_THRESHOLD, dt, TWIN, channel)
    epic_bp, boxcars_bp = count_peaks_stalta_Elarms(
        data_acc_bp, data_vel_bp, data_dis_bp, data_stalta, STA, LTA, MPD,
        STALTA_THRESHOLD, dt, TWIN, channel)

    # ---- FinDer amplitude exceedances --------------------------------------
    finder_hp = count_triggers_FinDer(data_acc_hp, FINDER_DEADTIME,
                                      FINDER_THRESHOLD, dt)

    results = {
        "hourly_min": rawmin,
        "hourly_max": rawmax,
        "hourly_mean": rawmean,
        "hourly_range": rawrange,
        "hourly_max_acc": accmax_hp,
        "hourly_max_bp_acc": accmax_bp,
        "hourly_noise_floor_acc": noisefloor_acc_hp,
        "hourly_noise_floor_bp_acc": noisefloor_acc_bp,
        "rms_above_.07": rms_hp,
        "rms_bp_above_.07": rms_bp,
        "acc_spikes_gt_.34": spikes_hp,
        "acc_bp_spikes_gt_.34": spikes_bp,
        "approximate_epic_triggers": epic_hp,
        "approximate_epic_bp_triggers": epic_bp,
        "acc_gt_2.0": finder_hp,
        "dcrequest_pctavailable": pctavailable,
        "dcrequest_ngaps": ngaps,
        "dcrequest_segmentshort": segmentshort,
        "dcrequest_segmentlong": segmentlong,
    }

    # PSD powers are only uploaded when all five look like real measurements.
    # Genuine values run about -180 to -50 dB; anything at or above -1 dB, or a
    # None from get_power, means PPSD did not produce a usable spectrum.
    if powers is not None and max(powers) < PSD_MAX_VALID:
        for name, power in zip(PSD_METRICS, powers):
            results[name] = float(power)

    # Boxcar rejection counts are diagnostics only and are not uploaded.
    results["_boxcars_hp"] = boxcars_hp
    results["_boxcars_bp"] = boxcars_bp

    return results


def build_measurements(results, squac_channel_id, starttime, endtime):
    """
    Turn a results dictionary into SQUAC measurement objects.

    Only names present in SQUAC_METRIC_IDS are uploaded, so diagnostics and
    anything new left in the results dictionary are ignored.

    :type results: dict
    :param results: Metric name to value.
    :type squac_channel_id: int
    :param squac_channel_id: SQUAC channel id.
    :type starttime: :class:`datetime.datetime`
    :param starttime: Start of the reporting hour.
    :type endtime: :class:`datetime.datetime`
    :param endtime: End of the reporting hour.
    :rtype: list
    :return: List of WriteOnlyMeasurementSerializer objects.
    """
    measurements = []
    for name, metric_id in SQUAC_METRIC_IDS.items():
        if name not in results:
            continue
        measurements.append(WriteOnlyMeasurementSerializer(
            metric=metric_id,
            channel=squac_channel_id,
            value=results[name],
            starttime=starttime,
            endtime=endtime))

    return measurements


def main():
    args = parse_arguments()

    starttime = parse_starttime(args.starttime)
    endtime = starttime + datetime.timedelta(0, args.duration)

    # Analysis window: STA + LTA seconds of run-up before the reporting hour.
    tbuffer = STA + LTA
    time1 = starttime - datetime.timedelta(0, tbuffer)
    time2 = endtime

    print("Reporting hour:   {} to {}".format(starttime, endtime))
    print("Analysis window:  {} to {}  ({:.2f} s)".format(
        time1, time2, args.duration + tbuffer))

    # ---- SQUAC client ------------------------------------------------------
    upload = not args.no_squac
    squac_client = None
    if upload:
        if no_squacapi:
            sys.exit("squacapi_client is not available; rerun with --no-squac")
        try:
            user = os.environ['SQUACAPI_USER']
            password = os.environ['SQUACAPI_PASSWD']
        except KeyError:
            sys.exit("Requires environment variables SQUACAPI_USER and "
                     "SQUACAPI_PASSWD, or the --no-squac option")
        squac_client = get_client(user, password)
        print("SQUAC client: {}".format(squac_client))

    channel_map = load_channel_map(args.channel_map, squac_client)

    # ---- FDSN clients ------------------------------------------------------
    datacenter = args.datacenter
    if datacenter == "NCEDC":
        datacenter = "https://service.ncedc.org"

    try:
        client = Client(datacenter, timeout=1200)
        client_pnsn = None
        if 'PNSN' in args.chanfile:
            client_pnsn = Client(base_url='https://fdsnws.pnsn.uw.edu')
    except Exception as e:
        sys.exit("Failed to open FDSN client for {}: {}".format(datacenter, e))

    # ---- Download ----------------------------------------------------------
    # 120 s of padding either side of the analysis window, discarded after
    # filtering and integration.
    time1_padded = time1 - datetime.timedelta(0, PADDING)
    download_duration = args.duration + tbuffer + (2 * PADDING)

    if client_pnsn is not None:
        traces = download_waveforms_fdsn_bulk(
            args.chanfile, time1_padded, download_duration, client,
            client_internal=client_pnsn,
            internal_chanfile='chanfile.pnsnfdsnws')
    else:
        traces = download_waveforms_fdsn_bulk(
            args.chanfile, time1_padded, download_duration, client)

    streams = group_traces_by_sncl(traces)
    print("Downloaded data for {} channels".format(len(streams)))

    # ---- Loop over channels ------------------------------------------------
    measurements = []
    nchannels_pending = 0
    nchannels_uploaded = 0
    timer_start = timeit.default_timer()

    for sncl in sorted(streams):
        stream = streams[sncl]

        # Be gentle with the metadata service; without this the requests can
        # trip rate limiting partway through a large channel file.
        time.sleep(0.25)
        inventory = download_metadata_fdsn(
            stream[0].stats.network, stream[0].stats.station,
            stream[0].stats.location, stream[0].stats.channel, time1, client)
        if len(inventory) == 0:
            continue

        results = calculate_metrics_for_channel(
            stream, inventory, starttime, endtime, time1, time2, args.duration)
        if results is None:
            continue
        '''
        print("{}  pctavail {:.4g}  ngaps {}  accmax_hp {:.4g}  "
              "epic {} ({} boxcars)  epic_bp {} ({} boxcars)".format(
                  sncl, results["dcrequest_pctavailable"],
                  results["dcrequest_ngaps"], results["hourly_max_acc"],
                  results["approximate_epic_triggers"], results["_boxcars_hp"],
                  results["approximate_epic_bp_triggers"],
                  results["_boxcars_bp"]))


        print("{}  pctavail {:.4g}  ngaps {}  accmax_hp {:.4g}  "
              "epic {} ({} boxcars)  epic_bp {} ({} boxcars)  "
              "hourly_min {:.4g}  hourly_max {:.4g}  hourly_mean {:.4g}  "
              "hourly_range {:.4g}  acc_gt_2.0 {:.4g}  "
              "rms_bp_above_.07 {:.4g}  rms_above_.07 {:.4g}  "
              "acc_bp_spikes_gt_.34 {:.4g}  acc_spikes_gt_.34 {:.4g}  "
              "hourly_noise_floor_bp_acc {:.4g}  hourly_max_bp_acc {:.4g}  "
              "segmentshort {} segmentlong {}  "
              "power_5Hz {:.4g}  power_1Hz {:.4g}  power_5sec {:.4g}  "
              "hourly_max_acc {:.4g}  hourly_noise_floor_acc {:.4g}  "
              "power_40sec {:.4g}  power_10Hz {:.4g}".format(
                  sncl, results["dcrequest_pctavailable"],
                  results["dcrequest_ngaps"], results["hourly_max_acc"],
                  results["approximate_epic_triggers"], results["_boxcars_hp"],
                  results["approximate_epic_bp_triggers"], results["_boxcars_bp"],
                  results["hourly_min"], results["hourly_max"], results["hourly_mean"],
                  results["hourly_range"], results["acc_gt_2.0"],
                  results["rms_bp_above_.07"], results["rms_above_.07"],
                  results["acc_bp_spikes_gt_.34"], results["acc_spikes_gt_.34"],
                  results["hourly_noise_floor_bp_acc"], results["hourly_max_bp_acc"],
                  results["dcrequest_segmentshort"], results["dcrequest_segmentlong"],
                  results["power_5Hz"], results["power_1Hz"], results["power_5sec"],
                  results["hourly_max_acc"], results["hourly_noise_floor_acc"],
                  results["power_40sec"], results["power_10Hz"]))
        '''
        print('XXXX ',sncl, results["approximate_epic_triggers"], results["approximate_epic_bp_triggers"], results["hourly_noise_floor_bp_acc"], results["hourly_noise_floor_acc"], results["hourly_mean"], results["power_1Hz"] )

        metric_names = [
            "hourly_min",
            "hourly_max",
            "hourly_mean",
            "hourly_range",
            "acc_gt_2.0",
            "rms_bp_above_.07",
            "rms_above_.07",
            "acc_bp_spikes_gt_.34",
            "acc_spikes_gt_.34",
            "approximate_epic_triggers",
            "approximate_epic_bp_triggers",
            "hourly_noise_floor_bp_acc",
            "hourly_max_bp_acc",
            "dcrequest_pctavailable",
            "dcrequest_ngaps",
            "dcrequest_segmentshort",
            "dcrequest_segmentlong",
            "power_5Hz",
            "power_1Hz",
            "power_5sec",
            "hourly_max_acc",
            "hourly_noise_floor_acc",
            "power_40sec",
            "power_10Hz",
        ]
        integer_metrics = {
            "dcrequest_ngaps",
            "dcrequest_segmentshort",
            "dcrequest_segmentlong",
            "approximate_epic_triggers",
            "approximate_epic_bp_triggers",
        }

        metric_strings = []
        for name in metric_names:
            value = results[name]
            if name in integer_metrics:
                metric_strings.append("{} {}".format(name, value))
            else:
                metric_strings.append("{} {:.4g}".format(name, value))

        if not upload or sncl not in channel_map:
            continue

        print("{}  ({} boxcars, {} boxcars_bp)  {}".format(
            sncl,
            results["_boxcars_hp"],
            results["_boxcars_bp"],
            "  ".join(metric_strings)))

        measurements += build_measurements(results, channel_map[sncl],
                                           starttime, endtime)
        nchannels_pending = nchannels_pending + 1

        # Post once enough channels have accumulated.  A chunk size of 1 posts
        # every channel as it finishes, which is the safest but slowest option.
        if nchannels_pending >= args.upload_chunksize:
            response, errors = perform_bulk_create(measurements, squac_client,
                                                   chunk=500)
            nchannels_uploaded = nchannels_uploaded + nchannels_pending
            print("Uploaded {} channels to SQUAC ({} total), errors: {}".format(
                nchannels_pending, nchannels_uploaded, errors))
            measurements = []
            nchannels_pending = 0

    # Post whatever is left over from the last partial chunk.
    if upload and len(measurements) > 0:
        response, errors = perform_bulk_create(measurements, squac_client,
                                               chunk=500)
        nchannels_uploaded = nchannels_uploaded + nchannels_pending
        print("Uploaded {} channels to SQUAC ({} total), errors: {}".format(
            nchannels_pending, nchannels_uploaded, errors))

    print("Finished in {:.1f} s, {} channels uploaded".format(
        timeit.default_timer() - timer_start, nchannels_uploaded))


if __name__ == "__main__":
    main()

