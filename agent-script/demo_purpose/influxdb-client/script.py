import codecs
from datetime import datetime
import random

"""
reference : https://github.com/influxdata/influxdb-client-python
"""
from influxdb_client import WritePrecision, InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

#database name of your influxdb
bucket = "example"

client = InfluxDBClient(url="http://localhost:8086/", token="my-token", org="my-org")

write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()

#generating random number for dumo
val = random.randint(10, 50)
p1 = Point("project_count").tag("instance", "server_1").field("value", val).time(datetime.now(), WritePrecision.MS)

#generating random number for dumo
val = random.randint(10, 50)
p2 = Point("project_count").tag("instance", "server_2").field("value", val).time(datetime.now(), WritePrecision.MS)


p3 = Point("project_count").tag("instance", "server_2").tag("filter_x", "some_xyz").field("value", val).time(datetime.now(), WritePrecision.MS)

p4 = Point("project_count").tag("instance", "server_2").tag("filter_x", "some_abc").field("value", val).time(datetime.now(), WritePrecision.MS)


line_protocol = p1.to_line_protocol()
print(line_protocol)

# write using point structure
write_api.write(bucket=bucket, record=[p1,p2,p3])


