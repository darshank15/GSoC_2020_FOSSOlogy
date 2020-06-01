from prometheus_client import start_http_server, Summary
from prometheus_client import Counter, Gauge
import random
import time
import psycopg2

# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

unique_hash = Gauge('unique_hash', 'Number of unique pfile_sha256')
agent_run = Gauge('agent_run', 'Count of agent run')
num_of_project = Gauge('num_of_project', 'number of project per instance', ['server_instance'])

# Decorate function with metric.
@REQUEST_TIME.time()
def process_request(cursor):

    query = "select count(*) from pfile"
    cursor.execute(query)
    pfile_records = cursor.fetchone()
    unique_hash.set(pfile_records[0])
    
    query = "select count(*) from ars_master"
    cursor.execute(query)
    ars_master_records = cursor.fetchone()
    agent_run.set(ars_master_records[0])
    time.sleep(random.random())


    val=  random.randint(100, 500)
    num_of_project.labels(server_instance='server1').set(val)

    val=  random.randint(100, 500)
    num_of_project.labels(server_instance='server2').set(val)


def connect():
    """ Connect to the PostgreSQL database server """
    print("Connection Function Called")
    conn = None
    try:
        conn = psycopg2.connect(user="fossy",
                                  password="fossy",
                                  host="localhost",
                                  port="5432",
                                  database="fossology")
        cursor = conn.cursor()
        return cursor
       
        
    except (Exception, psycopg2.DatabaseError) as error:
        print("Exception !!!")


if __name__ == '__main__':
    
    cursor = connect()

    # Start up the server to expose the metrics.
    start_http_server(8000)
    # Generate some requests.

    while True:
        process_request(cursor)
