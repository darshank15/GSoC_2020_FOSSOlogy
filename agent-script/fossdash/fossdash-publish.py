#!/usr/bin/env python
#
# Copyright (C) 2020 Orange
# SPDX-License-Identifier: GPL-2.0
# Author: Nicolas Toussaint <nicolas1.toussaint@orange.com>
# Author: Bartlomiej Drozdz <bartlomiej.drozdz@orange.com>
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

import os
import time

import psycopg2
import datetime

# Fossology DB configuration file
#
# /!\ FIXME: Variable DB_CONFIG_FILE will not be availble in CRON context
#
DB_CONFIG_FILE = os.environ.get("DB_CONFIG_FILE","/usr/local/etc/fossology/Db.conf")
CONFIG = {}
# parse DB_CONFIG_FILE
with open(DB_CONFIG_FILE, mode="r") as dbf:
    config_entry = dbf.readline()
    while config_entry:
        config_entry = config_entry.split("=")
        CONFIG[config_entry[0]] = config_entry[1].strip().replace(";", "")
        config_entry = dbf.readline()

# produces "conf1=val1 conf2=val2 conf3=val3 ..."
config = " ".join(["=".join(config) for config in CONFIG.items()])

QUERIES_NAME = [
    "number_of_users", "number_of_groups", "number_of_file_uploads",
    "number_of_projects__theoretically", "number_of_url_uploads",
    "agents_count", "number_of_upload_status", "number_of_projects_per_size",
    "reportgen_count", "pfile_count", "avg_pfile_count", "job_count"
]

QUERIES = {
    'uuid': "SELECT instance_uuid uuid FROM instance;",
    'number_of_users': "SELECT count(u.*) AS users FROM users u;",
    'number_of_groups': "SELECT count(g.*) AS groups FROM groups g;",
    'number_of_projects__theoretically': "SELECT count(up.*) as uploads from (select distinct upload_mode, upload_origin from upload) up;",
    'number_of_file_uploads': "SELECT count(up1.upload_origin) as file_uploads FROM upload up1 WHERE up1.upload_mode = 104;",
    'number_of_url_uploads': "SELECT count(up2.upload_origin) as url_uploads FROM upload up2 WHERE up2.upload_mode = 100;",
    'agents_count': "SELECT ag.agent_name,count(jq.*) AS fired_jobs FROM agent ag LEFT OUTER JOIN jobqueue jq ON (jq.jq_type = ag.agent_name) GROUP BY ag.agent_name ORDER BY fired_jobs DESC;",
    'number_of_upload_status': "select CASE WHEN a.status=1 THEN 'open' WHEN a.status=2 THEN 'in_progres' WHEN a.status=3 THEN 'closed' WHEN a.status=3 THEN 'rejected' ELSE 'unknown' END status, a.count from (select status_fk status, count(1) as count from upload_clearing group by status_fk) a;",
    'number_of_projects_per_size': "select t.size, count(t.size) from (select CASE WHEN s.sx<2000 THEN 'small' WHEN s.sx>=2000 and s.sx<10000 THEN 'normal' ELSE 'big' END size from (select count(ut.ufile_name) sx from uploadtree ut group by upload_fk) s) t group by t.size;",
    "reportgen_count": "select count(*) from reportgen;",
    "pfile_count": "select count(*) from pfile;",
    "avg_pfile_count": "select round(avg(pfile_size)) from pfile;",
    "job_count": "select count(*) as jobs from job;"
}

def _query(connection, query, single=False):
    cur = connection.cursor()
    cur.execute(query)
    result = cur.fetchone() if single else cur.fetchall()
    return result


def report(connection):
    _result = {}
    for query in QUERIES_NAME:
        result = _query(connection, QUERIES[query])
        if result:
            _result[query] = result if len(result) > 1 else result[0]
            # print "==> ", _result[query]
    return _result


def prepare_report(data, uuid, prefix=None):

    # final report
    reported_metrics = []

    """ data : [('copyright', 1L), ('ecc', 1L),('pkgagent', 0L), ('monkbulk', 0L)]"""
    def getFormatedData(data):

        tuple_length = len(data)
        mask_length = tuple_length - 1  # if tuple_length > 1 else 0
        mask = ""
        if mask_length > 0:
            mask = ",type=%s"
        
        mask += " value=%s"
        
        return mask % data

    # resolves embedded metric names (when reports returns more than one value, with subnames)
    def dig(r, data, uuid):
        timestamp = datetime.datetime.now().strftime("%s000000000")
        if isinstance(data, list):
            multi = []
            for d in data:
                temp_data = getFormatedData(d)
                finaldata = "{},instance={}".format(r,uuid)
                finaldata += temp_data + " " + timestamp
                reported_metrics.append(finaldata)
            return multi

        else :
            temp_data = getFormatedData(data)
            finaldata = "{},instance={}".format(r,uuid)
            finaldata += temp_data + " " + timestamp
            return finaldata
        

    for metric, v in data.items():
        report_data = dig("{}".format(metric), v, uuid)
        if isinstance(report_data, list):
            for single_row in report_data :
                reported_metrics.append(single_row)
        else :
            reported_metrics.append(report_data)

    return reported_metrics

if __name__ == "__main__":
    connection = None
    try:
        connection = psycopg2.connect(config)
        uuid = _query(connection, QUERIES['uuid'], single=True)[0]  # tuple
        raw_report = report(connection)
        results = prepare_report(raw_report,uuid)
        for row in results :
            print row
    except (Exception, psycopg2.DatabaseError) as error:
        print error
    finally:
        if connection:
            connection.close()
    
    # for metric in results:
    #     metric_name, metric_value = metric.split(" ")
    #     print("{},instance={} value={} {}".format(metric_name, uuid, metric_value, timestamp))
