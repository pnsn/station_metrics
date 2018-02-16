#!/usr/bin/env python

import os
import psycopg2
import datetime
from pgcopy import CopyManager

# Find the last inserted ID into the measurements table.
def last_insert_id(cursor, table_name, pk_name):
    sequence = "{table_name}_{pk_name}_seq".format(table_name=table_name,
                                                       pk_name=pk_name)
    cursor.execute("SELECT last_value from {sequence}".format(sequence=sequence))
    return cursor.fetchone()[0]

# Read the sncl/scnl and metrics tables to get sncl_id and metric_id.
def read_database(dbname,hostname,dbuser,dbpass):
    dbuser = os.environ['POSTGRES_USER']
    dbpass = os.environ['POSTGRES_PASSWD']
    conn = psycopg2.connect(dbname=dbname, user=dbuser, host=hostname, password=dbpass )
    cursor = conn.cursor()
    cursor.execute('SELECT * from sncls;' )
    colnames = [desc[0] for desc in cursor.description]
    idindex = colnames.index('id')
    snclindex = colnames.index('sncl')
    sncl_id_list = []
    sncl_list = []
    metric_id_list = []
    metric_list = []
    for record in cursor:
        sncl_id_list.append(record[idindex])
        sncl_list.append(record[snclindex])
    cursor.execute('SELECT * from metrics;' )
    for record in cursor:
        metric_id_list.append(record[0])
        metric_list.append(record[1])

    return sncl_list,sncl_id_list,metric_list,metric_id_list,conn

# This can only INSERT.  It cannot UPDATE.  Needs to find a way to UPSERT.
def write_database(dbconn,sncl_id,starttime,endtime,datasrc_id,metriclist,valuelist,metric_list_db,metric_id_list_db):
    now = datetime.datetime.utcnow()
    now = now.replace(microsecond=0)
    cursor = dbconn.cursor()

    for idb in range(0,len(metriclist)):
        if ( metriclist[idb] in metric_list_db ):
            idmetric = metric_list_db.index(metriclist[idb])
            metric_id = metric_id_list_db[idmetric]
            cursor.execute('INSERT INTO measurements (sncl_id,metric_id,value,starttime,endtime,datasrc_id,created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)', (sncl_id,metric_id,str(valuelist[idb]),starttime,endtime,datasrc_id,now) )
            dbconn.commit()

    return


######################################################################################
# These functions are me just hacking around... please ignore.
# UPSERT
# https://dba.stackexchange.com/questions/167591/postgresql-psycopg2-upsert-syntax-to-update-columns
def write_database2(dbconn,sncl_id,starttime,endtime,datasrc_id,metriclist,valuelist,metric_list_db,metric_id_list_db):
    now = datetime.datetime.utcnow()
    now = now.replace(microsecond=0)
    cursor = dbconn.cursor()

    for idb in range(0,len(metriclist)):
        if ( metriclist[idb] in metric_list_db ):
            idmetric = metric_list_db.index(metriclist[idb])
            metric_id = metric_id_list_db[idmetric]
            iid = last_insert_id(dbconn.cursor(),'measurements','id') + 1
            cursor.execute('INSERT INTO measurements (id,sncl_id,metric_id,value,starttime,endtime,datasrc_id,created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO UPDATE SET (sncl_id,metric_id,value,starttime,endtime,datasrc_id,created_at) = (EXCLUDED.sncl_id,EXCLUDED.metric_id,EXCLUDED.value,EXCLUDED.starttime,EXCLUDED.endtime,EXCLUDED.datasrc_id,EXCLUDED.created_at)', (sncl_id,metric_id,str(valuelist[idb]),starttime,endtime,datasrc_id,now) )
            dbconn.commit()

    return


def write_database3(dbconn,sncl_id,starttime,endtime,datasrc_id,metriclist,valuelist,metric_list_db,metric_id_list_db):
    now = datetime.datetime.utcnow()
    now = now.replace(microsecond=0)
    cursor = dbconn.cursor()

    for idb in range(0,len(metriclist)):
        if ( metriclist[idb] in metric_list_db ):
            idmetric = metric_list_db.index(metriclist[idb])
            metric_id = metric_id_list_db[idmetric]
            cursor.execute('INSERT INTO measurements (sncl_id,metric_id,value,starttime,endtime,datasrc_id,created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)', (sncl_id,metric_id,str(valuelist[idb]),starttime,endtime,datasrc_id,now) )
            dbconn.commit()

#    execute_values(cursor

    return


# https://github.com/altaurog/pgcopy
# This uses CopyManager and takes 0.01 sec vs 0.3 sec. However:
# psycopg2.IntegrityError: duplicate key value violates unique constraint "measurements_id_key"
# DETAIL:  Key (id)=(1) already exists.
# CONTEXT:  COPY measurements, line 1
#
def write_database4(dbconn,sncl_id,starttime,endtime,datasrc_id,metriclist,valuelist,metric_list_db,metric_id_list_db):
    now = datetime.datetime.utcnow()
    now = now.replace(microsecond=0)
    records = []
    cols = ('id','sncl_id','metric_id','value','starttime','endtime','datasrc_id','created_at')
    iid = last_insert_id(dbconn.cursor(),'measurements','id') + 1 

    print "Last ID is " + str(iid) #+ " " + str(type(iid))

    for idb in range(0,len(metriclist)):
        if ( metriclist[idb] in metric_list_db ):
            idmetric = metric_list_db.index(metriclist[idb])
            metric_id = metric_id_list_db[idmetric]
            iid = iid + 1
            records.append((iid,sncl_id,metric_id,valuelist[idb],starttime,endtime,datasrc_id,now))
            print str(iid) + " " + str(valuelist[idb]) + " " + str(metric_id) 
    print "IID2 : " + str(iid)
    print "RECORED: " + str(records)
    mgr = CopyManager(dbconn, 'measurements', cols)
    mgr.copy(records)

    return

# https://stackoverflow.com/questions/8134602/psycopg2-insert-multiple-rows-with-one-query 

# https://billyfung.com/writing/2017/06/improving-multiple-inserts-with-psycopg2 


