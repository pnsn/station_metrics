from obspy import UTCDateTime

def raw_trace_to_ground_motion_filtered_pruned(TraceOrig,T1,T2,AccVelDisp,FullResponse,f1,f2,f3,f4,inv):

#  Input is an ObsPy trace that will get demeaned, converted to ACC/VEL/DISP, and then filtered.
#  FullResponse = 0: only apply gain correction.  
#  FullResponse = 1: remove the full response.  Warning: this is slow, about 5sec/hour long trace.

    if ( "cc" in AccVelDisp or "CC" in AccVelDisp ):
        GM = "ACC"
    elif ( "V" in AccVelDisp or "v" in AccVelDisp ):
        GM = "VEL"
    else:
        GM = "DISP"
    trace = TraceOrig.copy()
    trace.detrend(type='demean')
    if ( len(inv) == 0 ):
        print ( "No metadata" )
    else:
        #----- correct for gain factor only
        if ( FullResponse == 0 ):
            trace.remove_sensitivity(inv)
            if ( f3 == 0 ):
                trace.filter("highpass", freq = f2)
            else:
                trace.filter("bandpass", freqmin = f2, freqmax = f3)
            trace = trace.slice(UTCDateTime(T1),UTCDateTime(T2))
#            trace.detrend(type='polynomial',order=3)  #--- of order 0.08 sec/trace
#            trace.detrend(type='linear')              #--- of order 0.027 sec/trace
#            trace.detrend(type='demean')              #--- of order 0.002 sec/trace
            if ( trace.stats.channel[1:2] == "N" ):
                GMnative = "ACC"
            else:
                GMnative = "VEL"
            if ( GMnative == GM ):
                idonothing = 1
            elif ( GMnative == "ACC" and GM == "VEL" and trace.stats.npts > 2 ):
                trace.integrate(method='cumtrapz')
            elif ( GMnative == "ACC" and GM == "DISP" ):
                trace.integrate(method='cumtrapz')
                trace.integrate(method='cumtrapz')
            elif ( GMnative == "VEL" and GM == "ACC" and trace.stats.npts > 2 ):
                trace.differentiate(method='gradient')
        #----- remove the full response
        elif ( FullResponse == 1 ):
            trace.remove_response(inventory=inv, output=GM, pre_filt=(f1,f2,f3,f4))
            trace = trace.slice(UTCDateTime(T1),UTCDateTime(T2))

#        trace.detrend(type='polynomial',order=3)
        trace.detrend(type='demean')              #--- of order 0.002 sec/trace

    return trace
