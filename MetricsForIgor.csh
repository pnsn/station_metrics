#!/bin/csh

cd ~/STATION_METRICS
set here = `pwd`

set list = "IRISZ"

set year = `date --date="2 hours ago" -u +%-Y`
set month = `date --date="2 hours ago" -u +%-m`
set day = `date --date="2 hours ago" -u +%-d`
set hour = `date --date="2 hours ago" -u +%-H`

if ( -e status_running.$list ) then
   echo "Currently running: " $list $year.$month.$day.$hour
else

echo "Currently running: " $year.$month.$day.$hour $list > status_running.$list

if ( -e log.IGORMETRICS.$year.$month.$day.$hour.$list ) /bin/rm log.IGORMETRICS.$year.$month.$day.$hour.$list
if ( -e IGORMETRICS.GAIN.$year.$month.$day.$hour.$list.txt ) /bin/rm IGORMETRICS.GAIN.$year.$month.$day.$hour.$list.txt

/bin/cp $here/MetricsForIgor.py MetricsForIgortemp.py
sed -i 's/IFULLRESP/0/g' MetricsForIgortemp.py
sed -i 's/YEAR/'"$year"'/g' MetricsForIgortemp.py
sed -i 's/MONTH/'"$month"'/g' MetricsForIgortemp.py
sed -i 's/DAY/'"$day"'/g' MetricsForIgortemp.py
sed -i 's/HOUR/'"$hour"'/g' MetricsForIgortemp.py
sed -i 's/LIST/'"$list"'/g' MetricsForIgortemp.py
./MetricsForIgortemp.py > log.IGORMETRICS.$year.$month.$day.$hour.$list
sleep 62

/bin/rm status_running.$list

endif


