#!/bin/sh

NET=UW
STA=DAVN
STARTTIME=2018-06-02T00:00:00
DURATION=0.1
DATACENTER=IRIS
INSTITUTION=PNSN

TALLYDIR=/home/eew-report/reports/Seattle
SCRIPTDIR=/home/seis/DEV/station_metrics
EEWENV=/home/seis/.bashrc
THISDIR=`pwd`

source $EEWENV

conda deactivate
conda activate eew

cmd="${SCRIPTDIR}/eew_stationreport -l ${TALLYDIR} -I $INSTITUTION -N $NET -S $STA -s ${STARTTIME} -d $DURATION -dc $DATACENTER"

echo $cmd

cd $SCRIPTDIR
$cmd
/bin/mv $NET.$STA.* $THISDIR
cd $THISDIR

# rsync to:  http://seismo.ess.washington.edu/users/seis
rsync -av -e "ssh -p 7777" $NET.$STA.* seis@seismo:/home/seis/public_html

