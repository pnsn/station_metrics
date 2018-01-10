#!/usr/bin/env python

# Plot the last hour of data to a .png file.

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.dates import DateFormatter
import numpy as np
import datetime

def make_station_figure(st1,st2,st3,st4,st5,label1,label2,label3,label4,label5):

        net = st1[0].stats.network
        stat = st1[0].stats.station
        loc = st1[0].stats.location
        chan = st1[0].stats.channel

        fig = plt.figure(figsize=(8,8),dpi=80)

        gs1 = gridspec.GridSpec(1,1)
        gs1.update(left=0.15,right=0.92,bottom=0.81,top=0.94,wspace=0.01)
        ax1 = plt.subplot(gs1[:,:])
        gs2 = gridspec.GridSpec(1,1)
        gs2.update(left=0.15,right=0.92,bottom=0.62,top=0.78,wspace=0.01)
        ax2 = plt.subplot(gs2[:,:])
        gs3 = gridspec.GridSpec(1,1)
        gs3.update(left=0.15,right=0.92,bottom=0.43,top=0.59,wspace=0.01)
        ax3 = plt.subplot(gs3[:,:])
        gs4 = gridspec.GridSpec(1,1)
        gs4.update(left=0.15,right=0.92,bottom=0.24,top=0.40,wspace=0.01)
        ax4 = plt.subplot(gs4[:,:])
        gs5 = gridspec.GridSpec(1,1)
        gs5.update(left=0.15,right=0.92,bottom=0.08,top=0.21,wspace=0.01)
        ax5 = plt.subplot(gs5[:,:])

        for ii in range(0,len(st1)):
            timearray = np.arange(st1[ii].stats.npts)*st1[ii].stats.delta
            t = st1[ii].stats.starttime
            x1 = np.array([datetime.datetime(t.year,t.month,t.day,t.hour,t.minute,t.second,t.microsecond) + datetime.timedelta(seconds=jj) for jj in timearray ])
            ax1.plot(x1,st1[ii].data,color='k')
            ax1.xaxis.set_major_formatter(DateFormatter('%H:%M'))
            tlast = st1[ii].stats.endtime
        for ii in range(0,len(st2)):
            timearray = np.arange(st2[ii].stats.npts)*st2[ii].stats.delta
            t = st2[ii].stats.starttime
            x2 = np.array([datetime.datetime(t.year,t.month,t.day,t.hour,t.minute,t.second,t.microsecond) + datetime.timedelta(seconds=jj) for jj in timearray ])
            ax2.plot(x2,st2[ii].data,color='k')
            ax2.xaxis.set_major_formatter(DateFormatter('%H:%M'))
        for ii in range(0,len(st3)):
            timearray = np.arange(st3[ii].stats.npts)*st3[ii].stats.delta
            t = st3[ii].stats.starttime
            x3 = np.array([datetime.datetime(t.year,t.month,t.day,t.hour,t.minute,t.second,t.microsecond) + datetime.timedelta(seconds=jj) for jj in timearray ])
            ax3.plot(x3,st3[ii].data,color='k')
            ax3.xaxis.set_major_formatter(DateFormatter('%H:%M'))
        for ii in range(0,len(st4)):
            timearray = np.arange(st4[ii].stats.npts)*st4[ii].stats.delta
            t = st4[ii].stats.starttime
            x4 = np.array([datetime.datetime(t.year,t.month,t.day,t.hour,t.minute,t.second,t.microsecond) + datetime.timedelta(seconds=jj) for jj in timearray ])
            ax4.plot(x4,st4[ii].data,color='k')
            ax4.xaxis.set_major_formatter(DateFormatter('%H:%M'))

        timearray = np.arange(len(st5))*st1[0].stats.delta
        t = st1[ii].stats.starttime
        x5 = np.array([datetime.datetime(t.year,t.month,t.day,t.hour,t.minute,t.second,t.microsecond) + datetime.timedelta(seconds=jj) for jj in timearray ])
        ax5.plot(x5,st5,color='k')
        ax5.xaxis.set_major_formatter(DateFormatter('%H:%M'))

        timediffinsec = (tlast - st1[0].stats.starttime)
        tadd = timediffinsec*0.01
#        t = st1[0].stats.starttime
        t1 = st1[0].stats.starttime - datetime.timedelta(seconds=tadd)
        t2 = tlast + datetime.timedelta(seconds=tadd)
        t = t1
        t1 = datetime.datetime(t.year,t.month,t.day,t.hour,t.minute,t.second,t.microsecond)
        t = t2
        t2 = datetime.datetime(t.year,t.month,t.day,t.hour,t.minute,t.second,t.microsecond)
        ttextL = t1 - datetime.timedelta(seconds=timediffinsec*0.18)
        ttextR = t1 + datetime.timedelta(seconds=timediffinsec*1.025)
        ttextR2 = t1 + datetime.timedelta(seconds=timediffinsec*1.055)
        ttitle = t1 + datetime.timedelta(seconds=timediffinsec*0.15)
        titletext = str(ttitle.year) + '/' + str(ttitle.month) + '/' + str(ttitle.day) + ' (UTC)         ' + net + '.' + stat + '.' + loc + '.' + chan 
        ytitle = ax1.get_ylim()[0] + ( ax1.get_ylim()[1] - ax1.get_ylim()[0] )*1.04
        ax1.text(ttitle,ytitle,titletext)
        ax1.set_xlim([t1,t2])
        ax2.set_xlim([t1,t2])
        ax3.set_xlim([t1,t2])
        ax4.set_xlim([t1,t2])
        ax5.set_xlim([t1,t2])
        ax1.set_xticklabels([])
        ax2.set_xticklabels([])
        ax3.set_xticklabels([])
        ax4.set_xticklabels([])
        ytext1 = ax1.get_ylim()[0] + ( ax1.get_ylim()[1] - ax1.get_ylim()[0] )*0.65
        ytext2 = ax2.get_ylim()[0] + ( ax2.get_ylim()[1] - ax2.get_ylim()[0] )*0.65
        ytext3 = ax3.get_ylim()[0] + ( ax3.get_ylim()[1] - ax3.get_ylim()[0] )*0.65
        ytext4 = ax4.get_ylim()[0] + ( ax4.get_ylim()[1] - ax4.get_ylim()[0] )*0.65
        ytext5 = ax5.get_ylim()[0] + ( ax5.get_ylim()[1] - ax5.get_ylim()[0] )*0.65
        if ( len(label1) < 10 ):
            ax1.text(ttextR,ytext1,label1,color='k',rotation=270)
        else:
            ax1.text(ttextR2,ytext1,label1.split()[0],color='k',rotation=270)
            ax1.text(ttextR,ytext1," ".join(label1.split()[1:]),color='k',rotation=270)
        if ( len(label2) < 10 ):
            ax1.text(ttextR,ytext2,label2,color='k',rotation=270)
        else:
            ax2.text(ttextR2,ytext2,label2.split()[0],color='k',rotation=270)
            ax2.text(ttextR,ytext2," ".join(label2.split()[1:]),color='k',rotation=270)
        if ( len(label3) < 10 ):
            ax3.text(ttextR,ytext3,label3,color='k',rotation=270)
        else:
            ax3.text(ttextR2,ytext3,label3.split()[0],color='k',rotation=270)
            ax3.text(ttextR,ytext3," ".join(label3.split()[1:]),color='k',rotation=270)
        if ( len(label4) < 10 ):
            ax4.text(ttextR,ytext4,label4,color='k',rotation=270)
        else:
            ax4.text(ttextR2,ytext4,label4.split()[0],color='k',rotation=270)
            ax4.text(ttextR,ytext4," ".join(label4.split()[1:]),color='k',rotation=270)
        if ( len(label5) < 10 ):
            ax5.text(ttextR,ytext5,label5,color='k',rotation=270)
        else:
            ax5.text(ttextR2,ytext5,label5.split()[0],color='k',rotation=270)
            ax5.text(ttextR,ytext5," ".join(label5.split()[1:]),color='k',rotation=270)
        locname = loc
        if ( loc == "--" ):
           locname = ""
        figname = 'WAVEFORMS.' + str(ttitle.year) + '.' + str(ttitle.month) + '.' + str(ttitle.day) + '.' + str(ttitle.hour) + '.' + net + '.' + stat + '.' + locname + '.' + chan + '.png'
        plt.savefig(figname)
        plt.close("all")


