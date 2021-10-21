#!/usr/bin/env python
# coding: utf-8

import psycopg2
import psycopg2.extras
import os
import json
import pandas as pd
from configparser import ConfigParser
import yaml
import slack
import requests

def path():
	return os.path.dirname(__file__)

root_path = path()

def slackPostMsg(text):
	#web_hook_url = "https://hooks.slack.com/services/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"
	web_hook_url = "https://hooks.slack.com/services/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"
	requests.post(web_hook_url, data=str(text))
	return True

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
		print("Error :", error)
	finally:
		if conn is not None:
			conn.close()

def getJsonFilePath():
	#sql = "SELECT p.p_id, b.project_name, p.sample_id, p.pro_status, j.json_path, j.job_id, j.job_status FROM projects_t as p INNER JOIN jobs_t as j ON p.p_id=j.project_id INNER JOIN barcodes_t as b ON b.b_id =p.barcode_id WHERE p.pro_status='1'"
	sql = "SELECT p.p_id, b.project_name, p.sample_id, p.cfdna, p.normal, p.tumor, p.pro_status, j.json_path, j.job_id, j.job_status FROM projects_t as p INNER JOIN jobs_t as j ON p.p_id=j.project_id INNER JOIN barcodes_t as b ON b.b_id =p.barcode_id WHERE p.pro_status='1'"
	res_data = fetch_sql_query(sql)
	return res_data

def updateJobPercent(project_id , percentage, status):
	sql = "UPDATE projects_t SET progress_bar='{}', pro_status='{}' WHERE p_id='{}'".format(percentage, status, project_id)
	data = execute_sql_query(sql)


def updatePojectStatus(pro_id, status):
	sql = "UPDATE projects_t SET pro_status='{}' WHERE p_id='{}'".format(status, pro_id)
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
	df_nested_list = pd.json_normalizie(data, record_path =['jobs'])
	print(df_nested_list)
	total_count = len(df_nested_list.index)
	status_df = df_nested_list['status'].value_counts()
	status_list = dict(status_df)
	completed_count = 0

	if "COMPLETED" in status_list:
	  completed_count = status_df['COMPLETED']

	fail_status = False
	if "FAILED" in status_list:
	  fail_status = True

	cancel_status = False
	if "CANCELLED" in status_list:
	   cancel_status = True
		#completed_count = completed_count + status_df['CANCELLED']

	job_percent = int((completed_count / total_count ) * 100)
	return job_percent,fail_status,cancel_status


def main():
	json_data = getJsonFilePath()
	if json_data:
		for js in json_data:
			project_id = js['p_id']
			file_path = js['json_path']
			job_id = js['job_id']
			sample_id =js["sample_id"]
			project_name = js["project_name"]
			cfdna = js["cfdna"]
			tumor = js["tumor"]
			if cfdna != "" :
				sample_details = "cfDNA"
				capture_id = cfdna
			else:
				sample_details = "Tumor"
				capture_id = tumor
			
			if(os.path.exists(file_path)):
				percentage,fail_status,cancel_status = readJsonFile(file_path)
				pro_status = '2' if(fail_status) else ("-1" if (percentage==100) else js['pro_status'])
				if(fail_status):
					updateJobStatus(job_id, '2')
					text = {"text": "Project : {} | Sample ID :{} | {} : {} - Failed".format(project_name, sample_id, sample_details, capture_id)}
					#slackPostMsg(text)

				if(percentage == 100):
					updateJobStatus(job_id, '-1')
					#text = {"text": "Project : {} | {} sample completed".format(project_name, sample_id)}
					text = {"text": "Project : {} | Sample ID :{} | {} : {} - Completed".format(project_name, sample_id, sample_details, capture_id)}
					#slackPostMsg(text)

				if(cancel_status):
					print("PROJECT NAME : ",project_name," || SAMPLE ID :", sample_id, " || PROJECT ID : ", project_id, " || PERCENTAGE :", percentage," || FAIL STATUS :", fail_status, " || PROJECT STATUS :", pro_status, " || Cancel Status : ",cancel_status)
					updateJobStatus(job_id, '-2')
					updatePojectStatus(project_id, '-2')
					#text = {"text": "Project : {} | {} sample cancelled".format(project_name,sample_id)}
					text = {"text": "Project : {} | Sample ID :{} | {} : {} - Cancelled".format(project_name, sample_id, sample_details, capture_id)}
					#slackPostMsg(text)

				print("PROJECT NAME : ",project_name," || PERCENTAGE :",percentage," || SAMPLE ID :", sample_id)
				res = updateJobPercent(project_id, percentage, pro_status)
			else:
				print("File Not Found")
				updateJobStatus(job_id, '-2')
				updatePojectStatus(project_id, '-2')

	else:
		print("No Records Found")

if __name__ == "__main__":
	main()


