import psycopg2
import pandas as pd
import numpy as np
import gzip

import io
import os

from tqdm.auto import tqdm

pd.options.display.max_columns = None
pd.options.display.max_rows = None
pd.options.display.max_colwidth = 1000

class ProgressFile:
    """ProgressFile: simple class to work as a file-like object that can be used by function to read the file
    while at the same time updating a progress bar.
    """

    def __init__(self, pbar, filename, mode="rt"):
        self.file = gzip.open(filename, mode, encoding='windows-1252')
        self.progress = self.file.tell()
        self.pbar = pbar
        self.file.readline() #skip the first line: csv header

    def close(self):
        self.file.seek(0, os.SEEK_END)
        self.pbar.n = self.file.tell()
        self.pbar.refresh()
        self.file.close()

    def read(self, size):
        buf = self.file.read(size)
        self.pbar.update(size)

        return buf

    def readline(self, size):
        buf = self.file.readline(size)
        self.pbar.update(size)

        return buf


def copy_progress(csv, table):
    """copy the csv file to the table using tdqm progressbar.
    """
    #import the database using a tqdm progressbar and a ProgressFile
    pbar = tqdm(total=os.path.getsize(csv), desc='Importing '+os.path.splitext(os.path.basename(csv))[0],
            dynamic_ncols=True, unit_scale=1, unit='Bytes') #make a tdqm progress bar object

    pfile = ProgressFile(pbar, csv, 'rt') #create a ProgressFile for showing progress

    cursor.copy_expert("""COPY {} FROM STDIN WITH (FORMAT CSV)""".format(table), pfile)

    #close the objects
    pfile.close()
    pbar.close()

    #show the first 10 records of this table
    #df = pd.read_sql('SELECT * FROM ' + table + ' LIMIT 10',con)
    #print('## ' + os.path.splitext(os.path.basename(csv))[0] + ' (' + str(cursor.rowcount) + ' records copied):\n')
    #print(df)

#Modify config.ini in the root folder of the repository to change the settings to connect to your postgreSQL database
import configparser
import os
config = configparser.ConfigParser()

if os.path.isfile('config.ini'):
    config.read('config.ini')
else:
    config.read('config.SAMPLE.ini')

#Open a connection to the postgres database:
con = psycopg2.connect(database=config['psycopg2']['database'],
                       user=config['psycopg2']['username'], password=config['psycopg2']['password'],
                       host=config['psycopg2']['host'], port=config['psycopg2']['port'])
con.set_client_encoding('WIN1252') #Uses code page for Dutch accented characters.
con.set_session(autocommit=True)
cursor = con.cursor()

# Create schema
sql = """
CREATE SCHEMA IF NOT EXISTS amsterdamumcdb;
GRANT USAGE ON SCHEMA amsterdamumcdb TO public;
GRANT CREATE ON SCHEMA amsterdamumcdb TO public;
SET SCHEMA 'amsterdamumcdb';
"""
cursor.execute(sql)

# Create admissions table

table = 'admissions'
sql = """
DROP TABLE IF EXISTS admissions CASCADE;
CREATE TABLE admissions
(
    patientid INTEGER,
    admissionid serial PRIMARY KEY,
    admissioncount INTEGER,
    location VARCHAR,
    urgency BIT,
    origin VARCHAR,
    admittedat BIGINT,
    admissionyeargroup VARCHAR,
    dischargedat BIGINT,
    lengthofstay SMALLINT,
    destination VARCHAR,
    gender VARCHAR,
    agegroup VARCHAR,
    dateofdeath BIGINT,
    weightgroup VARCHAR,
    weightsource VARCHAR,
    heightgroup VARCHAR,
    heightsource VARCHAR,
    specialty VARCHAR
);
"""
#cursor.execute(sql)
#csv = os.path.join(config['files']['datapath'], config['files'][table])
#copy_progress(csv, table) #runs copy_from using a tdqm progress bar

# Create drugitems table

table = 'drugitems'
sql = """
DROP TABLE IF EXISTS drugitems CASCADE;
CREATE TABLE drugitems
(
    admissionid INTEGER,
    orderid BIGINT,
    ordercategoryid INTEGER,
    ordercategory VARCHAR,
    itemid INTEGER,
    item VARCHAR,
    isadditive BIT,
    isconditional BIT,
    rate FLOAT,
    rateunit VARCHAR,
    rateunitid INTEGER,
    ratetimeunitid INTEGER,
    doserateperkg BIT,
    dose FLOAT,
    doseunit VARCHAR,
    doserateunit VARCHAR,
    doseunitid INTEGER,
    doserateunitid INTEGER,
    administered FLOAT,
    administeredunit VARCHAR,
    administeredunitid INTEGER,
    action VARCHAR,
    start BIGINT,
    stop BIGINT,
    duration BIGINT,
    solutionitemid INTEGER,
    solutionitem VARCHAR,
    solutionadministered FLOAT,
    solutionadministeredunit VARCHAR,
    fluidin FLOAT,
    iscontinuous BIT
)
"""
#cursor.execute(sql)
#csv = os.path.join(config['files']['datapath'], config['files'][table])
#copy_progress(csv, table) #runs copy_from using a tdqm progress bar

# Create freetextitems table

table = 'freetextitems'
sql = """
DROP TABLE IF EXISTS freetextitems CASCADE;
CREATE TABLE freetextitems
(
    admissionid INTEGER,
    itemid BIGINT,
    item VARCHAR,
    value VARCHAR,
    comment VARCHAR,
    measuredat BIGINT,
    registeredat BIGINT,
    registeredby VARCHAR,
    updatedat BIGINT,
    updatedby VARCHAR,
    islabresult BIT
)
"""
#cursor.execute(sql)
#csv = os.path.join(config['files']['datapath'], config['files'][table])
#copy_progress(csv, table) #runs copy_from using a tdqm progress bar

# Create listitems table

table = 'listitems'
sql = """
DROP TABLE IF EXISTS listitems CASCADE;
CREATE TABLE listitems
(
    admissionid INTEGER,
    itemid BIGINT,
    item VARCHAR,
    valueid INT,
    value VARCHAR,
    measuredat BIGINT,
    registeredat BIGINT,
    registeredby VARCHAR,
    updatedat BIGINT,
    updatedby VARCHAR,
    islabresult BIT
)
"""
#cursor.execute(sql)
#csv = os.path.join(config['files']['datapath'], config['files'][table])
#copy_progress(csv, table) #runs copy_from using a tdqm progress bar

# Create numericitems table

table = 'numericitems'
sql = """
    DROP TABLE IF EXISTS numericitems CASCADE;
    CREATE TABLE numericitems
    (
    admissionid INTEGER,
    itemid BIGINT,
    item VARCHAR,
    tag VARCHAR,
    value FLOAT,
    unitid INT,
    unit VARCHAR,
    comment VARCHAR,
    measuredat BIGINT,
    registeredat BIGINT,
    registeredby VARCHAR,
    updatedat BIGINT,
    updatedby VARCHAR,
    islabresult BIT,
    fluidout FLOAT
    )
"""
#cursor.execute(sql)
#csv = os.path.join(config['files']['datapath'], config['files'][table])
#copy_progress(csv, table) #runs copy_from using a tdqm progress bar

# Create procedureorderitems table

table = 'procedureorderitems'
sql = """
DROP TABLE IF EXISTS procedureorderitems CASCADE;
CREATE TABLE procedureorderitems
(
    admissionid INTEGER,
    orderid BIGINT,
    ordercategoryid INT,
    ordercategoryname VARCHAR,
    itemid INT,
    item VARCHAR,
    registeredat BIGINT,
    registeredby VARCHAR
)
"""
#cursor.execute(sql)
#csv = os.path.join(config['files']['datapath'], config['files'][table])
#copy_progress(csv, table) #runs copy_from using a tdqm progress bar

# Create processitems table

table = 'processitems'
sql = """
DROP TABLE IF EXISTS processitems CASCADE;
CREATE TABLE processitems
(
    admissionid INTEGER,
    itemid BIGINT,
    item VARCHAR,
    start BIGINT,
    stop BIGINT,
    duration BIGINT
);
"""
#cursor.execute(sql)
#csv = os.path.join(config['files']['datapath'], config['files'][table])
#copy_progress(csv, table) #runs copy_from using a tdqm progress bar

# Verify tables

#AmsterdamUMCdb Version 1.0.2 record counts
data = [
    ['admissions', 23106],
    ['drugitems', 4907269],
    ['freetextitems', 651248],
    ['listitems', 30744065],
    ['numericitems', 977625612],
    ['procedureorderitems', 2188626],
    ['processitems', 256715]
]

counts_published = pd.DataFrame(data, columns=['tables', 'counts'])
counts_published = counts_published.set_index('tables')

failed = False
for table in counts_published.index:
        sql = "SELECT COUNT(admissionid) FROM " + table + ";"
        try:
            cursor.execute(sql)
            count = cursor.fetchone()[0]
        except:
            count = 0

        count_published = counts_published.loc[table, 'counts']

        if count == count_published:
            print(f"{table}: {count} => good")
        else:
            failed = True
            print(f"{table}: {count} => bad")

# Create indices

import select
import psycopg2.extensions
import time

def wait(conn):
    while True:
        state = conn.poll()
        if state == psycopg2.extensions.POLL_OK:
            break
        elif state == psycopg2.extensions.POLL_WRITE:
            select.select([], [conn.fileno()], [])
        elif state == psycopg2.extensions.POLL_READ:
            select.select([conn.fileno()], [], [])
        else:
            raise psycopg2.OperationalError("poll() returned %s" % state)

def get_status():
    status_sql = """
    SELECT c.relname as tablename, s.*, a.query FROM pg_stat_progress_create_index s
    JOIN pg_stat_activity a ON s.pid = a.pid
    JOIN pg_class c on s.relid = c.oid
    WHERE query LIKE '%-- amsterdamumcdb indices%';
    """
    status = pd.read_sql(status_sql, con)
    if len(status) > 0:
        pid = status['pid'][0]
        phase = status['phase'][0]
        tablename = status['tablename'][0]

        if 'tuples' in phase:
            total = status['tuples_total'][0]
            current = status['tuples_done'][0]
        else:
            total = status['blocks_total'][0]
            current = status['blocks_done'][0]

        return pid, total, current, phase, tablename
    else:
        #no running index available
        return None, None, None, None, None


#create a new async connection, to monitor the status from another connection while the indexing is running.
aconn = psycopg2.connect(database=config['psycopg2']['database'],
                       user=config['psycopg2']['username'], password=config['psycopg2']['password'],
                       host=config['psycopg2']['host'], port=config['psycopg2']['port'], async_=1)

wait(aconn) #wait until connection is ready
acurs = aconn.cursor()

index_sql = """
-- amsterdamumcdb indices
SET SCHEMA 'amsterdamumcdb';
-- admissions table
CREATE INDEX admissions_admissionid_index ON admissions (admissionid);
CREATE INDEX admissions_patientid_index ON admissions (patientid);

-- drugitems table
CREATE INDEX drugitems_admissionid_index ON drugitems (admissionid);
CREATE INDEX drugitems_orderid_index ON drugitems (orderid);
CREATE INDEX drugitems_ordercategoryid_index ON drugitems (ordercategoryid);
CREATE INDEX drugitems_itemid_index ON drugitems (itemid);
CREATE INDEX drugitems_start_index ON drugitems (start);
CREATE INDEX drugitems_stop_index ON drugitems (stop);

-- freetextitems table
CREATE INDEX freetextitems_admissionid_index ON freetextitems (admissionid);
CREATE INDEX freetextitems_itemid_index ON freetextitems (itemid);
CREATE INDEX freetextitems_measuredat_index ON freetextitems (measuredat);

-- listitems table
CREATE INDEX listitems_admissionid_index ON listitems (admissionid);
CREATE INDEX listitems_itemid_index ON listitems (itemid);
CREATE INDEX listitems_measuredat_index ON listitems (measuredat);

-- numericitems table
CREATE INDEX numericitems_admissionid_index ON numericitems (admissionid);
CREATE INDEX numericitems_itemid_index ON numericitems (itemid);
CREATE INDEX numericitems_measuredat_index ON numericitems (measuredat);
CREATE INDEX numericitems_admission_item_time_index ON numericitems (admissionid, itemid, measuredat);
CREATE INDEX numericitems_islabresult_index ON numericitems (islabresult);
CREATE INDEX numericitems_fluidout_index ON numericitems (fluidout);

-- procedureorderitems table
CREATE INDEX procedureorderitems_admissionid_index ON procedureorderitems (admissionid);
CREATE INDEX procedureorderitems_itemid_index ON procedureorderitems (itemid);
CREATE INDEX procedureorderitems_ordercategoryid_index ON procedureorderitems (ordercategoryid);
CREATE INDEX procedureorderitems_registeredat_index ON procedureorderitems (registeredat);

-- processitems table
CREATE INDEX processitems_admissionid_index ON processitems (admissionid);
CREATE INDEX processitems_itemid_index ON processitems (itemid);
CREATE INDEX processitems_start_index ON processitems (start);
CREATE INDEX processitems_stop_index ON processitems (stop);
"""
#execute create index sql query **asychronously**
acurs.execute(index_sql)

#wait 2 seconds to allow for starting up the indexing process
time.sleep(2)

#progress bar variables
progress_blocks = None
progress_tuples = None
progress_current = None

#used for progress of indexing the database (based on indices in release 1.0.2)
TOTAL_INDEX_BLOCKS = 97361839
TOTAL_INDEX_TUPLES = 5.999210e+09

#get the current status of the indexing operation

pid, total, current, previous_phase, previous_tablename = get_status()
if pid == None:
    print('No indexing in progress.')
else:

    #create two tqdm objects for progress bars
    progress_blocks = tqdm(total=TOTAL_INDEX_BLOCKS, desc='Total blocks read', dynamic_ncols=True,
                           unit_scale=1, unit='blocks') #total blocks progress
    progress_tuples = tqdm(total=TOTAL_INDEX_TUPLES, desc='Total tuples written', dynamic_ncols=True,
                           unit_scale=1, unit='tuples') #total tuples progress
    progress_current = tqdm(total=total, desc='Processing table ' + previous_tablename + ' (' + previous_phase + ')',
                            dynamic_ncols=True, unit_scale=1, leave=False) #current index progress

    #update the progress bars every two seconds until the progress query returns empty or changes
    while True:
            current_pid, total, current, phase, tablename = get_status()

            if pid == None or current_pid != pid:
                break #process changed: done

            #phase changed, if 'scanning table' a new item was started
            if (not previous_phase == phase) or \
                (not previous_tablename == tablename):

                reset = False
                if 'scanning table' in phase: #scanning tables, loading tuples in tree
                    #previous phase ('tuples') should be added completely to progress bar
                    progress_tuples.update(progress_current.total - progress_current.n)
                    reset = True

                elif 'loading tuples in tree' in phase: #loading tuples in tree
                    #previous phase ('scanning table') should be added completely to progress bar
                    progress_blocks.update(progress_current.total - progress_current.n)
                    reset = True

                if reset:
                    #finalize (100%) the progress bar, remove it and start a new one
                    progress_current.n = progress_current.total
                    progress_current.close()
                    progress_current = tqdm(total=total, desc='Processing table ' + tablename + ' (' + phase + ')',
                                            dynamic_ncols=True, unit_scale=1, leave=False) #current index progress

            #update progress bars based on the phase
            update = False
            if 'scanning table' in phase: #scanning tables, loading tuples in tree

                progress_current.unit = 'blocks'

                #update the progress of total blocks to read
                progress_blocks.update(current - progress_current.n)
                update = True

            elif 'loading tuples in tree' in phase:
                progress_current.unit = 'tuples'

                #update the progress of total tuples written
                progress_tuples.update(current - progress_current.n)
                update = True

            if update:
                #update the progress of the current index
                progress_current.n = current
                progress_current.update(0) #trigger refresh

                #store the current phase to compare with the next
                previous_phase = phase
                previous_tablename = tablename


            time.sleep(1) #wait for one second before requerying indexing progress

    #left while loop
    if not progress_blocks is None:
        progress_blocks.n = TOTAL_INDEX_BLOCKS
        progress_blocks.close()
    if not progress_tuples is None:
        progress_tuples.n = TOTAL_INDEX_TUPLES
        progress_tuples.close()
    if not progress_current is None:
        progress_current.n = progress_current.total
        progress_current.close()

    print('Indexing done.')

wait(aconn) #wait until connection is ready
aconn.close()
