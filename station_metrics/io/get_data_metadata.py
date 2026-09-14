#!/home/seis/miniconda3/envs/squac/bin/python

"""
Waveform and metadata retrieval, and raw-counts-to-ground-motion conversion.

Everything that talks to an FDSN web service, plus the single function that
turns a raw counts trace into filtered ground motion, lives here.  The metric
arithmetic itself is in noise_metrics.py.

Change log
----------
Aug 2026: raw_trace_to_ground_motion_filtered_pruned renamed to
          raw_trace_to_ground_motion, and the processing order changed.  It was
          detrend -> demean -> remove sensitivity -> slice -> integrate/
          differentiate -> filter -> demean.  It is now detrend -> demean ->
          remove sensitivity -> integrate/differentiate -> filter -> slice ->
          demean, i.e. the trace is kept long through the integration and the
          filter and only cut to the analysis window at the end.  Cutting first
          meant the filter and the integration ran with the analysis window's
          own edges as their start-up transient; now the 120 s of padding
          either side absorbs that transient and it is thrown away with the cut.
Aug 2026: full-response removal (remove_response with a pre-filter) dropped.
          It was never used in production; only the sensitivity (gain) path was.
Aug 2026: all slicing goes through slice_trace, which adds one extra sample at
          the end so that a nominally 3600 s cut always spans at least 3600 s.
          A cut of exactly 3600.000 s can come back a hair short and be
          rejected by PPSD.
"""

import datetime
import time
import timeit

from obspy import UTCDateTime


def build_list(chanfile):
    """
    Build a list of NSLC strings from a file or from a list of lines.

    Accepts either whitespace- or period-separated channel descriptions, with
    or without a location code::

        UW BABE -- HHZ
        UW BABE HHZ
        UW.BABE.--.HHZ

    Blank lines and lines starting with # are skipped.  An empty location code
    is normalised to ``--``.

    :type chanfile: str or list
    :param chanfile: Path to a channel file, or a list of channel lines.
    :rtype: list
    :return: List of NSLC strings, e.g. ``['UW.BABE.--.HHZ']``.
    """
    sncls = []

    if type(chanfile) is not list:
        f1 = open(chanfile)
        lines = f1.readlines()
        f1.close()
    else:
        lines = chanfile

    for line in lines:
        line = str(line).strip()
        line = line.replace("..", ".--.")
        if line == "" or line.startswith("#"):
            continue

        # Already period separated, e.g. UW.BABE.--.HHZ
        if '.' in line and len(line.split('.')) == 4 and len(line.split()) == 1:
            sncls.append(line)
            continue

        # Whitespace separated, with or without a location code.
        parts = line.split()
        if len(parts) == 4:
            net = parts[0]
            sta = parts[1]
            loc = parts[2]
            cha = parts[3]
        elif len(parts) == 3:
            net = parts[0]
            sta = parts[1]
            loc = '--'
            cha = parts[2]
        else:
            print("bad line in chanfile: {}".format(line))
            continue

        sncls.append(net + '.' + sta + '.' + loc + '.' + cha)

    return sncls


def slice_trace(trace, time1, time2):
    """
    Cut a trace to a time window, with one extra sample on the end.

    ObsPy's slice is inclusive of both endpoints, so a cut from t to t+3600
    returns 3600/dt + 1 samples spanning exactly 3600 s.  Rounding in the
    sample times can leave that a fraction of a sample short, which is enough
    for PPSD to reject the segment.  Asking for one more sample removes the
    ambiguity at the cost of a window that is dt seconds long than requested.

    :type trace: :class:`obspy.core.trace.Trace`
    :param trace: Trace to cut.
    :type time1: :class:`datetime.datetime` or :class:`obspy.UTCDateTime`
    :param time1: Start of the window.
    :type time2: :class:`datetime.datetime` or :class:`obspy.UTCDateTime`
    :param time2: End of the window.
    :rtype: :class:`obspy.core.trace.Trace`
    :return: The cut trace.  May be empty if the trace does not overlap the
        window.
    """
    t1 = UTCDateTime(time1)
    t2 = UTCDateTime(time2) + trace.stats.delta

    return trace.slice(t1, t2)


def download_waveforms_fdsn_bulk(chanfile, starttime, duration,
                                 client_external,
                                 client_internal=None,
                                 internal_chanfile=None,
                                 chunksize=10, delay=0.1):
    """
    Download waveforms for a list of channels using ObsPy's bulk waveform
    request, in chunks of ``chunksize`` channels per request.

    Chunking is there to stay inside the EarthScope FDSN web service limits
    introduced in 2026, which appear to be roughly 500 MB and a 30 s timeout
    per request.  A chunk of 25 channels runs about 10% slower than a chunk of
    100, which sometimes times out, and about twice as fast as a chunk of 1.

    If an internal client and an internal channel file are supplied, any
    channel listed in the internal channel file is requested from the internal
    client instead of the external one.

    Missing data is normal and is reported quietly rather than raised.

    :type chanfile: str or list
    :param chanfile: Channel file path, or a list of channel lines.
    :type starttime: :class:`datetime.datetime`
    :param starttime: Start of the request window.
    :type duration: float
    :param duration: Length of the request window in seconds.
    :type client_external: :class:`obspy.clients.fdsn.Client`
    :param client_external: Already-open client for the public data centre.
    :type client_internal: :class:`obspy.clients.fdsn.Client`
    :param client_internal: Optional already-open client preferred for the
        channels listed in ``internal_chanfile``.
    :type internal_chanfile: str
    :param internal_chanfile: Optional channel file listing the channels
        available from ``client_internal``.
    :type chunksize: int
    :param chunksize: Number of channels per bulk request.
    :type delay: float
    :param delay: Seconds to pause between requests, to stay polite to the
        data centre.
    :rtype: list
    :return: List of :class:`obspy.core.trace.Trace` objects.  Channels with no
        data simply do not appear.
    """
    # Channels available from the preferred internal client, if any.
    available_sncls = []
    if client_internal is not None and internal_chanfile is not None:
        available_sncls = build_list(internal_chanfile)

    # Split the requested channels between the two clients.
    sncls = build_list(chanfile)
    sncls_internal = []
    sncls_external = []
    for sncl in sncls:
        if sncl in available_sncls:
            sncls_internal.append(sncl)
        else:
            sncls_external.append(sncl)

    T1 = UTCDateTime(starttime)
    T2 = UTCDateTime(starttime + datetime.timedelta(0, duration))

    streturn = []

    for source in ['external_FDSNWS', 'internal_FDSNWS']:
        if source == 'internal_FDSNWS':
            sncls_to_download = sncls_internal
            client = client_internal
        else:
            sncls_to_download = sncls_external
            client = client_external

        if client is None or len(sncls_to_download) == 0:
            continue

        bulkrequest = []
        nptstot = 0
        Timer0 = timeit.default_timer()
        station_set = set()
        n = 0

        for sncl in sncls_to_download:
            n = n + 1

            net = sncl.split('.')[0]
            sta = sncl.split('.')[1]
            loc = sncl.split('.')[2]
            if loc == '--':
                loc = ''
            cha = sncl.split('.')[3]

            bulkrequest.append((net, sta, loc, cha, T1, T2))

            if len(bulkrequest) < chunksize and n != len(sncls_to_download):
                continue

            time.sleep(delay)
            Timer1 = timeit.default_timer()
            nowtime = datetime.datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S.%f')[:-3]

            try:
                st = client.get_waveforms_bulk(bulkrequest)
                Timer2 = timeit.default_timer()

                nptschunk = 0
                for i in range(0, len(st)):
                    nptschunk = nptschunk + st[i].stats.npts
                    nptstot = nptstot + st[i].stats.npts
                    station_set.add(st[i].stats.station)

                if nptschunk > 0:
                    print("TIME bulk download, chunksize={:>4}: {:6.2f} sec  "
                          "Ntraces: {:>7}  Approx size chunk: {:8.3f} MB  "
                          "Total: {:8.3f} MB  Elapsed time: {:8.2f} sec  "
                          "starttime: {}  now: {}  Nstations: {}  "
                          "client: {}".format(
                              chunksize, Timer2 - Timer1, len(st),
                              nptschunk / 1048576.0, nptstot / 1048576.0,
                              Timer2 - Timer0, starttime, nowtime,
                              len(station_set), source))
                    streturn += st

            except Exception as e:
                Timer2 = timeit.default_timer()
                print("Failed download request or no data for: {} {} to {}  "
                      "request took: {:.2f} sec  now: {}  client: {}".format(
                          str(chanfile), str(T1), str(T2),
                          Timer2 - Timer1, nowtime, source))

            bulkrequest = []

    return streturn


def download_metadata_fdsn(net, sta, loc, cha, starttime, client):
    """
    Fetch full response metadata for one channel.

    :type net: str
    :param net: Network code.
    :type sta: str
    :param sta: Station code.
    :type loc: str
    :param loc: Location code.  Use an empty string for a blank location.
    :type cha: str
    :param cha: Channel code.
    :type starttime: :class:`datetime.datetime`
    :param starttime: Time at which the metadata should be valid.
    :type client: :class:`obspy.clients.fdsn.Client`
    :param client: Already-open FDSN client.
    :rtype: :class:`obspy.core.inventory.inventory.Inventory` or list
    :return: Inventory at ``level='response'``, or an empty list if the request
        failed or returned nothing.
    """
    T1 = UTCDateTime(starttime)
    T2 = UTCDateTime(starttime + datetime.timedelta(0, 1))

    try:
        inventory = client.get_stations(network=net, station=sta, location=loc,
                                        channel=cha, starttime=T1, endtime=T2,
                                        level='response')
    except Exception:
        print("Inventory not available for: {}.{}.{}.{} {} to {}".format(
            net, sta, loc, cha, str(T1), str(T2)))
        inventory = []

    return inventory


def raw_trace_to_ground_motion(trace_in, time1, time2, output,
                               freqmin, freqmax, inventory):
    """
    Convert a raw counts trace to filtered ground motion over a time window.

    The processing order matters and is deliberate:

    1. remove the mean,
    2. divide out the overall sensitivity (gain only, not the full response),
    3. integrate or differentiate to the requested ground-motion type,
    4. filter (causal Butterworth, 2 corners),
    5. cut to ``[time1, time2]``,
    6. remove the mean again.

    The trace handed in should already carry padding either side of the
    analysis window, normally 120 s.  Keeping the trace long through steps 3
    and 4 means the integration drift and the filter start-up transient live in
    the padding, and step 5 throws them away.  The filter is causal on purpose:
    ShakeAlert's own processing is causal, and these metrics are meant to
    resemble what the real-time system sees.

    The channel's second letter decides the native ground-motion type: N is an
    accelerometer, anything else is treated as a velocity sensor.

    :type trace_in: :class:`obspy.core.trace.Trace`
    :param trace_in: Raw counts trace, longer than the analysis window.  It is
        copied, not modified.
    :type time1: :class:`datetime.datetime`
    :param time1: Start of the analysis window.
    :type time2: :class:`datetime.datetime`
    :param time2: End of the analysis window.
    :type output: str
    :param output: ``'ACC'``, ``'VEL'`` or ``'DIS'``.
    :type freqmin: float
    :param freqmin: Highpass corner in Hz.  Set to 0 for a lowpass.
    :type freqmax: float
    :param freqmax: Lowpass corner in Hz.  Set to 0 for a highpass.
    :type inventory: :class:`obspy.core.inventory.inventory.Inventory`
    :param inventory: Station metadata at ``level='response'``.
    :rtype: :class:`obspy.core.trace.Trace`
    :return: Ground motion in SI units (m/s^2, m/s or m), cut to the window.
    """
    output = output.upper()
    if output not in ("ACC", "VEL", "DIS"):
        raise ValueError("output must be one of ACC, VEL or DIS, got "
                         + str(output))

    trace = trace_in.copy()

    if inventory is None or len(inventory) == 0:
        # The caller is expected to skip channels with no metadata; this is
        # only here so a missing inventory cannot silently produce nonsense.
        print("No metadata for " + trace.id + ", returning uncorrected trace")
        return slice_trace(trace, time1, time2).copy()

    trace.detrend(type='demean')
    trace.remove_sensitivity(inventory)

    if trace.stats.npts > 2:
        if trace.stats.channel[1:2] == "N":
            native = "ACC"
        else:
            native = "VEL"

        if native == "ACC" and output == "VEL":
            trace.integrate(method='cumtrapz')
        elif native == "ACC" and output == "DIS":
            trace.integrate(method='cumtrapz')
            trace.integrate(method='cumtrapz')
        elif native == "VEL" and output == "DIS":
            trace.integrate(method='cumtrapz')
        elif native == "VEL" and output == "ACC":
            trace.differentiate(method='gradient')

        if freqmax == 0:
            trace.filter("highpass", freq=freqmin, corners=2, zerophase=False)
        elif freqmin == 0:
            trace.filter("lowpass", freq=freqmax, corners=2, zerophase=False)
        else:
            trace.filter("bandpass", freqmin=freqmin, freqmax=freqmax,
                         corners=2, zerophase=False)

    trace = slice_trace(trace, time1, time2).copy()
    trace.detrend(type='demean')

    return trace

