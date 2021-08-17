#!/usr/bin/env python
# coding: utf-8

import psycopg2
import psycopg2.extras
import os
import json
import pandas as pd
from configparser import ConfigParser
import yaml

def path():
    return os.path.dirname(__file__)

root_path = path()

def readConfig(section,filename=root_path+"/config.yml"):
    with open(filename, "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
        section = cfg[section]
    return section


### Execute SQL Query - Create and Execute 
def execute_sql_query(sql):
    try:
        params = readConfig('launcher')
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        try:
            cur.execute( sql )
            conn.commit()
            cur.close()
            return {'status' : True, 'message': 'successfully'}
        except (Exception, psycopg2.Error) as error:
            conn.rollback()
            return {'status' : False, 'error': str(error)}

    except (Exception, psycopg2.Error) as error:
        return {'status' : False, 'error': str(error)}

### Fetch SQL Query 
def fetch_sql_query(sql):
    conn = None
    try:
        params = readConfig('launcher')
        conn = psycopg2.connect(**params)
        cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor) # RealDictCursor, NamedTupleCursor
        cur.execute(sql)
        rows = cur.fetchall()
        data = [dict(r) for r in rows]
        cur.close()
        return data
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def getJsonFilePath():
    sql = "SELECT p.p_id, p.pro_status, j.json_path, j.job_id, j.job_status FROM projects_t as p INNER JOIN jobs_t as j ON p.p_id=j.project_id WHERE p.pro_status='1'"
    res_data = fetch_sql_query(sql)
    return res_data

def updateJobPercent(project_id , percentage, status):
    sql = "UPDATE projects_t SET progress_bar='{}', pro_status='{}' WHERE p_id='{}'".format(percentage, status, project_id)
    data = execute_sql_query(sql)
    return data

def updateJobStatus(job_id, status):
    sql = "UPDATE jobs_t SET job_status='{}' WHERE job_id='{}'".format(status, job_id)
    data = execute_sql_query(sql)
    return data

def readJsonFile(path):
    with open(path,'r') as f:
        data = json.loads(f.read())
        
    # Flatten data
    df_nested_list = pd.json_normalize(data, record_path =['jobs'])
    total_count = len(df_nested_list.index)
    status_df = df_nested_list['status'].value_counts()
    status_list = dict(status_df)
    completed_count = status_df['COMPLETED']
    if "FAILED" in status_list or "CANCELLED" in status_list:
    	fail_status = True
    job_percent = int((completed_count / total_count ) * 100)
    return job_percent,fail_status

def main():
    json_data = getJsonFilePath()
    if json_data:
      for js in json_data:
        project_id = js['p_id']
        file_path = js['json_path']
        job_id = js['job_id']
        percentage,fail_status = readJsonFile(file_path)
        pro_status = '2' if(fail_status) else js['pro_status']
        res = updateJobPercent(project_id, percentage, pro_status)
        if(fail_status):
           updateJobStatus(job_id, '2')
    else:
       print("No Records Found")

if __name__ == "__main__":
    main()

