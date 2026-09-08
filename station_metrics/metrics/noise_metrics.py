#!/home/seis/miniconda3/envs/squac/bin/python

"""
Time-domain station-quality metric functions.

These are the low-level calculations used by calculate_station_metrics.py.
Each function takes plain numpy arrays (already sensitivity-corrected,
integrated/differentiated and filtered) plus the sample interval, and returns a
single number.

Amplitude units follow whatever was handed in.  calculate_station_metrics.py
works in SI (m/s^2, m/s, m) here and converts to cm at the very end, so the
thresholds below are in SI.

Sentinel values
---------------
A return value of -1 means "the trace was too short to make this measurement".
That is deliberately distinct from "no value uploaded", which would be
ambiguous between "no data existed", "channel not analyzed" and "trace short".

Change log
----------
Aug 2026: count_peaks_stalta_new renamed to count_peaks_stalta; the older
          count_peaks_stalta and the unused detect_peaks helper were removed.
Aug 2026: the ElarmS/EPIC boxcar rejection test was measured on rectified data,
          i.e. max(|x|) - min(|x|).  It is now measured on the signed trace,
          max(x) - min(x), which is what a boxcar (DC step) test should be.
          Rectifying collapses a symmetric boxcar toward zero range, so the old
          test rejected more triggers than intended.
Aug 2026: count_peaks_stalta_Elarms_times folded back into
          count_peaks_stalta_Elarms; trigger sample indices are no longer
          returned (nothing consumed them).
"""

import math

import numpy as np


# ---------------------------------------------------------------------------
# ElarmS3/EPIC amplitude gates (Chung et al., SRL March/April 2019).
# A candidate trigger is kept only if the peak amplitude in the measurement
# window falls inside all three of these ranges.  Units are SI.
# ---------------------------------------------------------------------------
ELARMS_ACC_MIN = 0.000031623      # m/s^2   (0.0031623 cm/s^2)
ELARMS_VEL_MIN = 0.000000031623   # m/s
ELARMS_VEL_MAX = 10.0             # m/s
ELARMS_DIS_MIN = 0.000000031623   # m
ELARMS_DIS_MAX = 31.623           # m

# Minimum peak-to-peak range required just after a trigger.  A digitizer glitch
# or telemetry boxcar is a DC step: it trips the STA/LTA but has essentially no
# wiggle behind it, so it fails this test and is thrown out.
ELARMS_BOXCAR_ACC = 0.000022      # m/s^2, applied to ?N? (accelerometer) channels
ELARMS_BOXCAR_VEL = 0.000000022   # m/s,   applied to ?H? (broadband) channels
ELARMS_BOXCAR_WINDOW = 0.1        # s, length of the boxcar test window


def noise_floor(x):
    """
    Quick approximation of the median envelope amplitude, a.k.a. the noise
    floor: half the range between the 2nd and 98th percentile of the samples.

    Trimming at the 2nd/98th percentile keeps earthquakes, calibration pulses
    and one-off spikes from dominating what is meant to be a background-noise
    number.

    :type x: :class:`numpy.ndarray`
    :param x: Signed (not rectified) time series.
    :rtype: float
    :return: Half range of the 2nd to 98th percentile amplitudes, same units
        as ``x``.
    """
    xsort = np.sort(x)
    x2 = xsort[int(len(x) * 0.02)]
    x98 = xsort[int(len(x) * 0.98)]

    return (x98 - x2) / 2.


def duration_exceed_RMS(x, ampthresh, RMSlen, dt):
    """
    Total time that a sliding-window RMS of the trace stays above a threshold.

    The RMS is computed by smoothing the squared trace with a centred boxcar
    ``RMSlen`` seconds long and taking the square root, then simply counting
    how many samples of that RMS function exceed ``ampthresh``.  This is a
    duration, not a count of excursions: one long noisy episode and many short
    ones can give the same answer.

    :type x: :class:`numpy.ndarray`
    :param x: Time series, normally sensitivity-corrected acceleration.
    :type ampthresh: float
    :param ampthresh: RMS amplitude threshold, same units as ``x``.
    :type RMSlen: float
    :param RMSlen: Length of the RMS sliding window in seconds.
    :type dt: float
    :param dt: Sample interval in seconds.
    :rtype: float
    :return: Seconds above threshold, or -1 if the trace is shorter than the
        RMS window.
    """
    from obspy.signal.util import smooth

    if len(x) <= int(RMSlen / dt):
        return -1

    iRMSwinlen = int(RMSlen / dt)
    RMS = np.sqrt(smooth((x ** 2), iRMSwinlen))

    return ((RMS > ampthresh).sum()) * dt


def _stalta_onsets(stalta, mph):
    """
    Sample indices where an STA/LTA function crosses up through a threshold.

    The STA/LTA trace is first squashed to a two-state function (0 below the
    threshold, 1 at or above it).  Every upward step in that function is one
    trigger onset, so a single long excursion above the threshold produces one
    onset rather than one per sample.

    :type stalta: :class:`numpy.ndarray`
    :param stalta: STA/LTA function.
    :type mph: float
    :param mph: Minimum peak height, i.e. the STA/LTA trigger threshold.
    :rtype: :class:`numpy.ndarray`
    :return: Integer sample indices of the upward crossings.
    """
    above = np.where(np.asarray(stalta) >= mph, 1., 0.)

    return np.nonzero(np.diff(above) > 0)[0]


def count_peaks_stalta(x, stalta, sta, lta, mpd, mph, dt, twin, ampthresh):
    """
    Count STA/LTA triggers that are backed up by a large enough amplitude.

    A trigger is counted when both of the following hold:

    1. the STA/LTA function crosses up through ``mph``, and
    2. the largest absolute amplitude of ``x`` in a ``twin``-second window,
       starting ``sta`` seconds before the crossing, exceeds ``ampthresh``.

    Triggers that survive both tests are then thinned with a dead time: any
    trigger within ``mpd`` seconds of the previous kept trigger is discarded,
    so one energetic arrival counts once rather than dozens of times.

    Note that ``x`` and ``stalta`` need not come from the same filtered trace.
    In this project the STA/LTA is computed on velocity highpassed at 3 Hz
    while the amplitude test is applied to acceleration filtered at 0.075 Hz.

    :type x: :class:`numpy.ndarray`
    :param x: Amplitude trace to test, normally acceleration.
    :type stalta: :class:`numpy.ndarray`
    :param stalta: STA/LTA function, same length and sampling as ``x``.
    :type sta: float
    :param sta: Short-term average window in seconds, used here only to back
        the measurement window up to just before the crossing.
    :type lta: float
    :param lta: Long-term average window in seconds.  Kept for documentation
        of the STA/LTA that was handed in; not used in the arithmetic.
    :type mpd: float
    :param mpd: Minimum time between counted triggers (dead time) in seconds.
    :type mph: float
    :param mph: STA/LTA trigger threshold.
    :type dt: float
    :param dt: Sample interval in seconds.
    :type twin: float
    :param twin: Length in seconds of the amplitude measurement window.
    :type ampthresh: float
    :param ampthresh: Amplitude the window peak must exceed, units of ``x``.
    :rtype: int
    :return: Number of triggers, or -1 if the trace is shorter than the dead
        time.
    """
    if len(stalta) <= int(mpd / dt):
        return -1

    ax = np.abs(np.asarray(x))
    istalta = int(sta / dt)
    itwin = int(twin / dt)
    impd = int(mpd / dt)

    peakcount = 0
    ilast = None
    for ionset in _stalta_onsets(stalta, mph):
        # Window runs from sta seconds before the crossing to twin seconds
        # later.  ionset can never be smaller than istalta because ObsPy's
        # classic_sta_lta zeroes the first lta seconds of its output, so no
        # onset is reported there and i1 cannot go negative.
        i1 = ionset - istalta
        i2 = min(i1 + itwin, len(ax))
        if max(ax[i1:i2]) < ampthresh:
            continue
        if ilast is not None and (ionset - ilast) < impd:
            continue
        peakcount = peakcount + 1
        ilast = ionset

    return peakcount


def count_peaks_stalta_Elarms(xA, xV, xD, stalta, sta, lta, mpd, mph, dt, twin,
                              channel):
    """
    Approximate the number of ElarmS3/EPIC triggers on a vertical channel.

    This mimics the EPIC trigger logic described by Chung et al. (SRL
    March/April 2019).  A candidate is declared where the STA/LTA function
    crosses up through ``mph``, then has to survive two further tests:

    1. **Amplitude gates.**  In a ``twin``-second window starting ``sta``
       seconds before the crossing, the peak acceleration must exceed
       ELARMS_ACC_MIN, the peak velocity must lie between ELARMS_VEL_MIN and
       ELARMS_VEL_MAX, and the peak displacement must lie between
       ELARMS_DIS_MIN and ELARMS_DIS_MAX.  These bracket physically plausible
       ground motion and throw out both dead channels and absurd excursions.
    2. **Boxcar test.**  A short window just after the crossing must show a
       peak-to-peak range larger than ELARMS_BOXCAR_ACC (accelerometers) or
       ELARMS_BOXCAR_VEL (broadbands).  A DC step from a digitizer or telemetry
       glitch trips the STA/LTA but carries no oscillation behind it, so it
       fails here.  The range is measured on the signed trace.

    Survivors are then thinned with a ``mpd``-second dead time.

    :type xA: :class:`numpy.ndarray`
    :param xA: Acceleration trace in m/s^2.
    :type xV: :class:`numpy.ndarray`
    :param xV: Velocity trace in m/s, same length and sampling as ``xA``.
    :type xD: :class:`numpy.ndarray`
    :param xD: Displacement trace in m, same length and sampling as ``xA``.
    :type stalta: :class:`numpy.ndarray`
    :param stalta: STA/LTA function, same length and sampling as ``xA``.
    :type sta: float
    :param sta: Short-term average window in seconds.
    :type lta: float
    :param lta: Long-term average window in seconds.
    :type mpd: float
    :param mpd: Minimum time between counted triggers (dead time) in seconds.
    :type mph: float
    :param mph: STA/LTA trigger threshold.
    :type dt: float
    :param dt: Sample interval in seconds.
    :type twin: float
    :param twin: Length in seconds of the amplitude measurement window.
    :type channel: str
    :param channel: SEED channel code.  The second letter picks the boxcar
        threshold: N for an accelerometer, H for a broadband.
    :rtype: list
    :return: ``[peakcount, boxcount]``, the number of triggers kept and the
        number rejected by the boxcar test, or ``[-1, -1]`` if the trace is
        shorter than the dead time.
    """
    if len(stalta) <= int(mpd / dt):
        return [-1, -1]

    if channel[1:2] == 'N':
        boxcar_threshold = ELARMS_BOXCAR_ACC
        boxcar_trace = np.asarray(xA)                          # signed acceleration
    elif channel[1:2] == 'H':
        boxcar_threshold = ELARMS_BOXCAR_VEL
        boxcar_trace = np.asarray(xV)                          # signed velocity
    else:
        boxcar_threshold = None
        boxcar_trace = None

    aA = np.abs(np.asarray(xA))
    aV = np.abs(np.asarray(xV))
    aD = np.abs(np.asarray(xD))

    istalta = int(sta / dt)
    itwin = int(twin / dt)
    impd = int(mpd / dt)
    ibox = int(ELARMS_BOXCAR_WINDOW / dt)

    peakcount = 0
    boxcount = 0
    ilast = None
    for ionset in _stalta_onsets(stalta, mph):
        # Amplitude measurement window, as in count_peaks_stalta.
        i1 = ionset - istalta
        i2 = min(i1 + itwin, len(aA))
        maxA = max(aA[i1:i2])
        maxV = max(aV[i1:i2])
        maxD = max(aD[i1:i2])
        if (maxA < ELARMS_ACC_MIN or
                maxV < ELARMS_VEL_MIN or maxV > ELARMS_VEL_MAX or
                maxD < ELARMS_DIS_MIN or maxD > ELARMS_DIS_MAX):
            continue

        # Boxcar window: ELARMS_BOXCAR_WINDOW seconds long, starting one
        # window length after the crossing.
        if boxcar_trace is not None:
            ib1 = min(ionset + 1 + ibox, len(boxcar_trace) - 1)
            ib2 = min(ib1 + ibox, len(boxcar_trace))
            boxrange = max(boxcar_trace[ib1:ib2]) - min(boxcar_trace[ib1:ib2])
            if boxrange < boxcar_threshold:
                boxcount = boxcount + 1
                continue

        if ilast is not None and (ionset - ilast) < impd:
            continue

        #Uncomment to log the sample index of every trigger that is counted.
        #print("TRIGGER sample index: " + str(ionset), mph)
        peakcount = peakcount + 1
        ilast = ionset

    return [peakcount, boxcount]


def count_triggers_FinDer(x, twin, ampthresh, dt):
    """
    Count separated excursions of the absolute amplitude above a threshold.

    Every sample whose absolute value reaches ``ampthresh`` is a candidate.
    Walking forward through the candidates, each one that is kept blanks out
    everything within the following ``twin`` seconds, so a single strong
    arrival is counted once instead of once per sample.  This approximates how
    often FinDer would see the channel exceed its amplitude threshold.

    :type x: :class:`numpy.ndarray`
    :param x: Sensitivity-corrected acceleration in m/s^2.
    :type twin: float
    :param twin: Minimum time in seconds between counted excursions.
    :type ampthresh: float
    :param ampthresh: Amplitude threshold in m/s^2.
    :type dt: float
    :param dt: Sample interval in seconds.
    :rtype: int
    :return: Number of separated excursions above the threshold.
    """
    xA = np.abs(np.copy(x))
    xA[xA < ampthresh] = 0
    xA[xA >= ampthresh] = 1
    iXA = np.nonzero(xA)[0]

    if len(iXA) == 0:
        return 0

    # Blank every candidate that falls within twin seconds of a kept one.
    itwin = int(twin / dt)
    i = 0
    while i < len(iXA):
        j1 = iXA[i]
        j2 = iXA[i] + itwin - 1
        if iXA[i] > 0:
            iXA[(iXA > j1) & (iXA < j2)] = 0
        i = i + 1
    iXA = np.nonzero(iXA)[0]

    return len(iXA)


def get_power(trace, inventory, periodlist):
    """
    Power spectral density at a list of periods, from ObsPy's PPSD.

    The trace is run through :class:`obspy.signal.spectral_estimation.PPSD`
    with its default settings, which segment the input into one-hour pieces.
    The trace handed in is therefore cut to just over one hour so that exactly
    one segment is produced, and the power reported is that of a single hour
    rather than an average over many.  The value at each requested period is
    taken from the nearest PPSD period bin, so it is not interpolated.

    :type trace: :class:`obspy.core.trace.Trace`
    :param trace: Raw (uncorrected, counts) trace, at least 3600 s long.
    :type inventory: :class:`obspy.core.inventory.inventory.Inventory`
    :param inventory: Station metadata at ``level='response'``.
    :type periodlist: list
    :param periodlist: Periods in seconds at which power is wanted.
    :rtype: list or None
    :return: Power in dB at each requested period, or None if the trace was too
        short or PPSD produced no segment.
    """
    from obspy.signal import PPSD

    # PPSD's default segment length is 3600 s.  npts includes both endpoints,
    # so the span of the trace is (npts - 1) * delta.
    if (trace.stats.npts - 1) * trace.stats.delta < 3600.:
        return None

    ppsd = PPSD(trace.stats, metadata=inventory)
    ppsd.add(trace)
    if len(ppsd._binned_psds) == 0:
        return None

    psd_periods = ppsd._period_binning[2]
    psd_power = ppsd._binned_psds[0]

    powers_at_periods = []
    for period in periodlist:
        powers_at_periods.append(
            psd_power[np.argmin(abs(psd_periods - period))])

    return powers_at_periods


def average_stdev(x, x2, n):
    """
    Running-sum average and approximate standard deviation.

    :type x: float
    :param x: Sum of the values.
    :type x2: float
    :param x2: Sum of the squared values.
    :type n: int
    :param n: Number of values.
    :rtype: tuple
    :return: ``(average, standard deviation)``.
    """
    if n == 0:
        return x, n

    squared = (x2 / n) - (x / n) * (x / n)
    if squared >= 0:
        stdev = math.sqrt(squared)
    else:
        stdev = 0.

    return x / n, stdev

