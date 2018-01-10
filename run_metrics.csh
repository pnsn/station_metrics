#!/bin/csh

# Simple script to run the station metrics in a crontab.  
# Script will run data that is 2 to 1 hours old, i.e. near real-time.

cd /home/seis/STATION_METRICS

set datacenter = 'IRIS'
set list = "IRISZ"

set chanfile = "ShakeAlertList.$list"
set duration = 3600

set year = `date --date="2 hours ago" -u +%-Y`
set month = `date --date="2 hours ago" -u +%-m`
set day = `date --date="2 hours ago" -u +%-d`
set hour = `date --date="2 hours ago" -u +%-H`
set minute = 0
set second = 0
set sta = 0.05
set lta = 5.0
set padding = 120
set fBP1 = 0.93
set fBP2 = 1.0
set fBP3 = 5.0
set fBP4 = 5.3

set fBP1 = 0.25
set fBP2 = 0.3
set fBP3 = 15.0
set fBP4 = 17.0


set fBB1 = 0.01
set fBB2 = 0.02
set gainorfullresp = 'Gain'
#set gainorfullresp = 'Resp'
set mpd = 10.0
set rmslen = 5.0

#set iplot = 1
set iplot = 0

set dbname = "station_metrics"

# if getting data off of local earthworm
set hostname = "web3.ess.washington.edu"

if ( -e status_running.$list ) then
   echo "Currently running: " $list $year.$month.$day.$hour
else

echo "Currently running: " $year.$month.$day.$hour $list > status_running.$list

if ( -e log.METRICS.$year.$month.$day.$hour.$list ) /bin/rm log.METRICS.$year.$month.$day.$hour.$list

/bin/cp calculate_metrics.py temp_calculate_metrics.py
sed -i 's/DATACENTER/'$datacenter'/g' temp_calculate_metrics.py
sed -i 's/CHANFILE/'$chanfile'/g' temp_calculate_metrics.py
sed -i 's/DURATION/'$duration'/g' temp_calculate_metrics.py
sed -i 's/YEAR/'$year'/g' temp_calculate_metrics.py
sed -i 's/MONTH/'$month'/g' temp_calculate_metrics.py
sed -i 's/DAY/'$day'/g' temp_calculate_metrics.py
sed -i 's/HOUR/'$hour'/g' temp_calculate_metrics.py
sed -i 's/MINUTE/'$minute'/g' temp_calculate_metrics.py
sed -i 's/SECOND/'$second'/g' temp_calculate_metrics.py
sed -i 's/STA/'$sta'/g' temp_calculate_metrics.py
sed -i 's/LTA/'$lta'/g' temp_calculate_metrics.py
sed -i 's/PADDING/'$padding'/g' temp_calculate_metrics.py
sed -i 's/fBP1/'$fBP1'/g' temp_calculate_metrics.py
sed -i 's/fBP2/'$fBP2'/g' temp_calculate_metrics.py
sed -i 's/fBP3/'$fBP3'/g' temp_calculate_metrics.py
sed -i 's/fBP4/'$fBP4'/g' temp_calculate_metrics.py
sed -i 's/fBB1/'$fBB1'/g' temp_calculate_metrics.py
sed -i 's/fBB2/'$fBB2'/g' temp_calculate_metrics.py
sed -i 's/GAINORFULLRESP/'$gainorfullresp'/g' temp_calculate_metrics.py
sed -i 's/MPD/'$mpd'/g' temp_calculate_metrics.py
sed -i 's/RMSLEN/'$rmslen'/g' temp_calculate_metrics.py
sed -i 's/IPLOT/'$iplot'/g' temp_calculate_metrics.py
sed -i 's/DBNAME/'$dbname'/g' temp_calculate_metrics.py
sed -i 's/HOSTNAME/'$hostname'/g' temp_calculate_metrics.py

./temp_calculate_metrics.py > log.METRICS.$year.$month.$day.$hour.$list

/bin/rm status_running.$list

endif




