#!/usr/bin/env python
#
# Copyright 2020
# SPDX-License-Identifier: GPL-2.0
# Author: Darshan Kansagara <kansagara.darshan97@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

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


