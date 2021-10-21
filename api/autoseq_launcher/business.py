from paramiko.ssh_exception import AuthenticationException, BadHostKeyException
from database import db
# from database.models import CTMBarcode as barcodes
# from database.models import CTMProject as project
from datetime import datetime
from sqlalchemy import create_engine
from flask import current_app

import paramiko
import time
import requests
import json
import os 
import fnmatch
import subprocess
import shutil
from operator import itemgetter
from itertools import groupby
import pandas as pd


def connectSSHServer(ip_address, pwd, user, command):
	result = False
	try:
		ssh_client = paramiko.SSHClient()
		ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

		print("Server Connecting...")
		ssh_client.connect(hostname=ip_address,username=user, password=pwd, timeout=5)

		transport = ssh_client.get_transport()
		chan = transport.open_session()
		chan.exec_command(command)

		key = True

		while key:
			if chan.recv_ready():
				result = chan.recv(4096).decode('ascii')
			if chan.recv_stderr_ready():
				result = chan.recv_stderr(4096).decode('ascii')
			if chan.exit_status_ready():
				result = chan.recv_exit_status()
				key = False
				result = True
				ssh_client.close()

		'''
		for key,value in command.items():
			stdin,stdout,stderr=ssh_client.exec_command(value, get_pty=False)
			stdout.channel.recv_exit_status()
			outlines=stdout.readlines()
			result=''.join(outlines)
		'''
	except (AuthenticationException, Exception) as e:
		print("Exception : {}",format(e))
		result = False
		
	return result

def generate_list_to_dict(result):
	d, row = {}, []
	for rowproxy in result:
		for column, value in rowproxy.items():
			if isinstance(value, datetime):
				value = datetime.strftime(value, "%Y-%m-%d")
			else:
				value = str(value)
			d = {**d, **{column: value}}
		row.append(d)
	return row

def validate_cfdna_file_size(file_arr, anch_user, anch_pwd):

	cfdna_dict = {}
	for i,f in enumerate(file_arr):
		cfdna_boolean = f[3]
		sample_id = f[4]
		prev_cfdna = ''
		if(cfdna_boolean):
			if(sample_id in cfdna_dict):
				prev_cfdna = cfdna_dict[sample_id]
			cfdna_dict[sample_id] = f[1]+','+prev_cfdna

	# cfdna_group = [[[w,x] for w,x,y,z in g] for k,g in  groupby(file_arr,key=itemgetter(3))]
	group_cfdna = []
	for cf in cfdna_dict:
		cfdna_arr = cfdna_dict[cf].rstrip(',').split(',')

		if(len(cfdna_arr) >= 2):
			symb_source_dir = cfdna_arr[1]
			source_dir = cfdna_arr[0]
			target_dir = cfdna_arr[0] + '_orig'

			group_cfdna.append(source_dir)

			isdir = os.path.isdir(target_dir)
			if not isdir:
				src_fldr = os.path.join(source_dir)
				dest_fldr = os.path.join(target_dir)
				shutil.move(src_fldr,dest_fldr)
				#os.rename(src_fldr,dest_fldr)
				
				if os.path.isdir(source_dir):
					os.rmdir(source_dir)
					print("{} is moved to {}".format(source_dir, target_dir))
				else:
					print("{} is already moved to {}".format(source_dir, target_dir))
			else:
				print('Already folder config {}', format(target_dir))
			
			'''
			file_names = os.listdir(target_dir)
			for file_name in file_names:
				islink_filename = os.path.islink(os.path.join(symb_source_dir, file_name))
				if not islink_filename:
                                    os.symlink(os.path.join(target_dir, file_name), os.path.join(symb_source_dir, file_name))
			'''
			try:
			        
				ssh_cmd = "ln -s {}/* {}".format(os.path.join(target_dir), os.path.join(symb_source_dir))
				machine_config = current_app.config["ANCHORAGE"]
				ip_address = machine_config['address']
				out = connectSSHServer(ip_address, anch_pwd, anch_user, ssh_cmd)
				if(not out):
					return {'status': True, 'data': [], 'error': 'Server not connected'}, 200		

			except Exception as e:
				print("Exception : {}".format(e))

	return group_cfdna

def generate_barcode_files(barcode_filename, files):
	with open(barcode_filename, 'w') as filehandle:
		for f in files:
			filehandle.write('%s\n' % f)

def get_file_list(proj_nfs_path, sample_pattern, cfdna_boolean):
	lst = os.listdir(proj_nfs_path)
	lst.sort()
	file_lst_arr = []
	for f in os.listdir(proj_nfs_path):
		sample_id = '-'.join(f.split('-')[1:3])
		if fnmatch.fnmatch(f, sample_pattern):
			if(cfdna_boolean):
				file_path = os.path.join(proj_nfs_path, f)
				file_size = subprocess.check_output(['du','-sh', file_path]).split()[0].decode('utf-8')
				file_lst_arr.append([file_size, file_path, f, fnmatch.fnmatch(f, '*-CFDNA-*'), sample_id])
			else:
				file_lst_arr.append(f)
		else:
			if(not cfdna_boolean and not '_orig' in f and sample_pattern == ''):
				file_lst_arr.append(f)

	return file_lst_arr

def generate_autoseq_config(barcode_filename, config_path, anch_user, anch_pwd):
	isdir = os.path.isdir(config_path)
	if(not isdir):
		os.makedirs(config_path)
	try:
		
		ref_genome = current_app.config['REF_GENOME_PATH']
		cmd = "autoseq --ref {} liqbio-prepare --outdir {} {}".format(ref_genome, config_path, barcode_filename)

		liqbio_prod = current_app.config['LIQBIO_PROD']
		ssh_cmd = "{}; {}".format(liqbio_prod, cmd)

		machine_config = current_app.config['ANCHORAGE']
		ip_address = machine_config['address']

		out = connectSSHServer(ip_address, anch_pwd, anch_user, ssh_cmd)
		return out
	except Exception as e:
		return {'status': False, 'data': [], 'error': str(e)}, 400


def insert_project_config(barcode_id, config_path):
	try : 
		file_list = os.listdir(config_path)
		for f in file_list:
			json_path = os.path.join(config_path, f)
			with open(json_path) as json_file:
				data = json.load(json_file)
				cfdna = '|'.join(data['CFDNA'])
				normal = '|'.join(data['N'])
				tumor = '|'.join(data['T'])
				sample_id = data['sdid']
				machine_type = ''
				cores = 8
				try:
					db.session.execute("INSERT INTO projects_t(p_id, barcode_id, sample_id, cfdna, normal, tumor, config_path, pro_status, progress_bar, cores, machine_type, create_time, update_time) VALUES (DEFAULT, '{}', '{}', '{}', '{}', '{}', '{}','0', '0', '{}', '{}', NOW(), NOW())".format(barcode_id, sample_id, cfdna, normal, tumor, json_path, cores, machine_type))
					db.session.commit()
				except Exception as e:
					return {'status': True, 'data': [], 'error': str(e)}, 200
		return {'status': True, 'data': 'Insert Successfully', 'error': ''}, 200
	except Exception as e:
		return {'status': False, 'data': [], 'error': str(e)}, 400


def check_db_connection():
	try:
		res = db.session.execute("select count(*) as count from barcodes_t")
		row = generate_list_to_dict(res)
		return {'status': True, 'data': row, 'error': ''}, 200
	except Exception as e:
		return {'status': False, 'data': [], 'error': str(e)}, 400

def upload_orderform(project_name, sample_arr, file_name,  anch_user, anch_pwd):

	file_lst_arr = sample_arr.split(',')

	file_info_arr = []

	nfs_path = current_app.config[project_name]

	project_nfs_path = nfs_path +'INBOX/'

	for f in file_lst_arr:
		sample_id = '-'.join(f.split('-')[1:3])
		c3_id = ''.join(f.split('-')[-1])
		proj_nfs_path = os.path.join(project_nfs_path, f)
		if(os.path.isdir(proj_nfs_path)):
			file_size = subprocess.check_output(['du','-sh', proj_nfs_path]).split()[0].decode('utf-8')
			file_info_arr.append([file_size, proj_nfs_path, f, fnmatch.fnmatch(f, '*-CFDNA-*'), sample_id, c3_id])

	if(file_info_arr):
		file_validate = {}
		for f1 in file_info_arr:
			if(f1[3] == False):
				if(f1[4] not in file_validate):
					file_validate[f1[4]] = f1[3]
				else:
					del file_validate[f1[4]]
			else:
				file_validate[f1[4]] = f1[3]

		for f in os.listdir(project_nfs_path):
			sample_id = '-'.join(f.split('-')[1:3])
			c3_id = ''.join(f.split('-')[-1])
			if sample_id in file_validate:
				sample_pattern = '*-'+sample_id+'-N-*'+c3_id if file_validate[sample_id] == True else '*-'+sample_id+'-CFDNA-*'+c3_id
				if fnmatch.fnmatch(f, sample_pattern):
					proj_nfs_path = os.path.join(project_nfs_path, f)
					if(os.path.isdir(proj_nfs_path)):
						file_size = subprocess.check_output(['du','-sh', proj_nfs_path]).split()[0].decode('utf-8')
						file_info_arr.append([file_size, proj_nfs_path, f, fnmatch.fnmatch(f, '*-CFDNA-*'), sample_id, c3_id])

		cfdna_val = validate_cfdna_file_size(file_info_arr, anch_user, anch_pwd)
		
		curr_file_arr = [ x[2] for x in file_info_arr if x[1] not in cfdna_val]
		curr_file_arr = list(set(curr_file_arr))

		current_date = datetime.today().strftime("%Y-%m-%d")
		barcode_dir = nfs_path+'sample_lists/'
		
		try:
			# Create target Directory
			os.mkdir(barcode_dir)
			print("Directory " , barcode_dir,  " Created ")
		except FileExistsError:
			print("Directory " , barcode_dir,  " already exists")
		
		barcode_filename = barcode_dir + 'clinseqBarcodes_'+current_date+'.txt'
		config_path = nfs_path+'config/'+current_date

		if os.path.isfile(barcode_filename):
			expand = 0
			while True:
				expand += 1
				new_file_name = barcode_filename.split(".txt")[0] + "_"+ str(expand) + ".txt"
				if os.path.isfile(new_file_name):
					continue
				else:
					barcode_filename = new_file_name
					config_path = nfs_path+'config/'+current_date + "_"+ str(expand)
					break

		generate_barcode_files(barcode_filename, curr_file_arr)
		conn_status = generate_autoseq_config(barcode_filename, config_path, anch_user, anch_pwd)

		if(conn_status):
			try:
				res = db.session.execute("INSERT INTO barcodes_t(b_id, project_name, barcode_path, config_path, launch_step, create_time, update_time) VALUES (DEFAULT, '{}', '{}', '{}', '0', NOW(), NOW()) RETURNING *".format(project_name, barcode_filename, config_path))
				db.session.commit()
				row = generate_list_to_dict(res)
				row[0]['file_list'] = curr_file_arr

				return {'status': True, 'data': row, 'error': ''}, 200
			except Exception as e:
				return {'status': False, 'data': [], 'error': str(e)}, 400
		else:
			return {'status': True, 'data': [], 'error': 'Server not connected'}, 200				
	else:
		return {'status': True, 'data': file_info_arr, 'error': 'Sample Id\'s are not found in the {}'.format(project_nfs_path)}, 200


def sample_generate_barcode(project_name, anch_user, anch_pwd, file_lst_arr):

	file_lst_arr = file_lst_arr.replace('PROBIO', 'PB').split(',')

	nfs_path = current_app.config[project_name]
	pro_name = 'PB' if project_name == 'PROBIO' else project_name
	project_nfs_path = nfs_path +'INBOX/'

	file_info_arr = []

	for f in os.listdir(project_nfs_path):
		for s1 in file_lst_arr:
			if fnmatch.fnmatch(f, s1):
				proj_nfs_path = os.path.join(project_nfs_path, f)
				if(os.path.isdir(proj_nfs_path)):
					sample_id = '-'.join(f.split('-')[1:3])
					file_size = subprocess.check_output(['du','-sh', proj_nfs_path]).split()[0].decode('utf-8')
					file_info_arr.append([file_size, proj_nfs_path, f, fnmatch.fnmatch(f, '*-CFDNA-*'), sample_id])

	if(file_info_arr):
		
		cfdna_val = validate_cfdna_file_size(file_info_arr, anch_user, anch_pwd)

		curr_file_arr = [ x[2] for x in file_info_arr if x[1] not in cfdna_val]
		curr_file_arr = list(set(curr_file_arr))

		current_date = datetime.today().strftime("%Y-%m-%d")
		barcode_dir = nfs_path+'sample_lists/'
		
		try:
			# Create target Directory
			os.mkdir(barcode_dir)
			print("Directory " , barcode_dir,  " Created ")
		except FileExistsError:
			print("Directory " , barcode_dir,  " already exists")
		
		barcode_filename = barcode_dir + 'clinseqBarcodes_'+current_date+'.txt'
		config_path = nfs_path+'config/'+current_date

		if os.path.isfile(barcode_filename):
			expand = 0
			while True:
				expand += 1
				new_file_name = barcode_filename.split(".txt")[0] + "_"+ str(expand) + ".txt"
				if os.path.isfile(new_file_name):
					continue
				else:
					barcode_filename = new_file_name
					config_path = nfs_path+'config/'+current_date + "_"+ str(expand)
					break

		generate_barcode_files(barcode_filename, curr_file_arr)
		conn_status = generate_autoseq_config(barcode_filename, config_path, anch_user, anch_pwd)

		if(conn_status):
			try:
				res = db.session.execute("INSERT INTO barcodes_t(b_id, project_name, barcode_path, config_path, launch_step, create_time, update_time) VALUES (DEFAULT, '{}', '{}', '{}', '1', NOW(), NOW()) RETURNING *".format(project_name, barcode_filename, config_path))
				db.session.commit()
				row = generate_list_to_dict(res)
				row[0]['file_list'] = curr_file_arr

				return {'status': True, 'data': row, 'error': ''}, 200
			except Exception as e:
				return {'status': False, 'data': [], 'error': str(e)}, 400
		else:
			return {'status': True, 'data': [], 'error': 'Server Not Connected'}, 200
	else:
		return {'status': True, 'data': file_info_arr, 'error': 'Sample Id\'s are not found in the {}'.format(project_nfs_path)}, 200

# def generate_barcodes(project_name, search_pattern, sample_arr, file_name):

#     nfs_path = current_app.config[project_name]
#     project_name = 'PB' if project_name == 'PROBIO' else project_name

#     project_nfs_path = nfs_path +'INBOX/'
#     sample_pattern = ''
#     if(search_pattern):
#         sample_pattern = project_name+'-*'+search_pattern
#         file_info_arr = get_file_list(project_nfs_path, sample_pattern, True)
#     else:
#         # search_pattern = file_name
#         file_lst_arr = sample_arr.split(',')
#         file_info_arr = []

#         for f in file_lst_arr:
#             sample_id = '-'.join(f.split('-')[1:3])
#             proj_nfs_path = os.path.join(project_nfs_path, f)
#             if(os.path.isdir(proj_nfs_path)):
#                 file_size = subprocess.check_output(['du','-sh', proj_nfs_path]).split()[0].decode('utf-8')
#                 file_info_arr.append([file_size, proj_nfs_path, f, fnmatch.fnmatch(f, '*-CFDNA-*'), sample_id])
		
#     if(file_info_arr):

#         validate_cfdna_file_size(file_info_arr)

#         curr_file_arr = get_file_list(project_nfs_path, sample_pattern, False)

#         current_date = datetime.today().strftime("%Y-%m-%d")
#         barcode_dir = nfs_path+'sample_lists/'
		
#         try:
#             # Create target Directory
#             os.mkdir(barcode_dir)
#             print("Directory " , barcode_dir,  " Created ")
#         except FileExistsError:
#             print("Directory " , barcode_dir,  " already exists")
		
#         barcode_filename = barcode_dir + 'clinseqBarcodes_'+current_date+'.txt'
#         generate_barcode_files(barcode_filename, curr_file_arr)
#         config_path = nfs_path+'config/'+current_date
#         try:
#             res = db.session.execute("INSERT INTO barcodes_t(b_id, project_name, search_pattern, barcode_path, config_path, bar_status, create_time, update_time) VALUES (DEFAULT, '{}', '{}', '{}', '{}', '0', NOW(), NOW()) RETURNING *".format(project_name, search_pattern, barcode_filename, config_path))
#             db.session.commit()
#             row = generate_list_to_dict(res)
#             generate_autoseq_config(barcode_filename, config_path)
#             row[0]['file_list'] = curr_file_arr

#             return {'status': True, 'data': row, 'error': ''}, 200
#         except Exception as e:
#             return {'status': False, 'data': [], 'error': str(e)}, 400
#     else:
#         return {'status': True, 'data': file_info_arr, 'error': 'Sample Id\'s are not found in the {}'.format(project_nfs_path)}, 200


def generate_config_file(barcode_id):
	res = db.session.execute("SELECT b_id, config_path from barcodes_t WHERE b_id ='{}'".format(barcode_id))
	row = generate_list_to_dict(res)
	b_id = row[0]['b_id']
	config_path = row[0]['config_path']
	try:
		if not os.listdir(config_path):
			return {'status': True, 'data': [], 'error': 'Config directory is empty'}, 200
		else:
			response, errorcode = insert_project_config(b_id, config_path)
			return response, errorcode 
	except Exception as e:
			return {'status': False, 'data': [], 'error': str(e)}, 400
	

def get_barcode_list():
	try:
		res = db.session.execute("select * from barcodes_t order by b_id desc")
		row = generate_list_to_dict(res)
		return {'status': True, 'data': row, 'error': ''}, 200
	except Exception as e:
		return {'status': False, 'data': [], 'error': str(e)}, 400

def del_barcode_info(barcode_id):
	try:
		res = db.session.execute("DELETE FROM  barcodes_t WHERE b_id ='{}'".format(barcode_id))
		db.session.commit()
		return {'status': True, 'data': 'Barcode information deleted successfully', 'error': ''}, 200
	except Exception as e:
		return {'status': False, 'data': [], 'error': str(e)}, 400

def get_project_list():
	try:
		res = db.session.execute("SELECT b.project_name, p.* from projects_t as p INNER JOIN barcodes_t as b ON b.b_id = p.barcode_id order by p.p_id desc")
		row = generate_list_to_dict(res)
		return {'status': True, 'data': row, 'error': ''}, 200
	except Exception as e:
		return {'status': False, 'data': [], 'error': str(e)}, 400

def get_job_list():
	try:
		res = db.session.execute("select p.sample_id, jb.* from jobs_t as jb INNER JOIN projects_t as p ON p.p_id=jb.project_id order by job_id desc")
		row = generate_list_to_dict(res)
		return {'status': True, 'data': row, 'error': ''}, 200
	except Exception as e:
		return {'status': False, 'data': [], 'error': str(e)}, 400

def start_pipeline(project_id):
	res = db.session.execute("SELECT b.project_name, p.sample_id, p.cfdna, p.normal, p.tumor, p.config_path, p.pro_status, CASE WHEN p.cores IS NULL THEN '8' ELSE p.cores END as cores, CASE WHEN p.machine_type IS NULL THEN '' ELSE p.machine_type END as machine_type from projects_t as p INNER JOIN barcodes_t as b ON b.b_id = p.barcode_id WHERE p.p_id ='{}' and p.pro_status !='1' order by p.p_id desc limit 1".format(project_id))
	row = generate_list_to_dict(res)
	project_name = row[0]['project_name']
	sdid = row[0]['sample_id']
	cfdna = row[0]['cfdna'] 
	normal = row[0]['normal']
	tumor = row[0]['tumor']
	json_path = row[0]['config_path']

	ref_genome = current_app.config['REF_GENOME_PATH']
	scratch_path = current_app.config['SCRATCH_PATH']
	libdir = current_app.config[project_name] + 'INBOX/'
	outdir_root = current_app.config[project_name]+'autoseq-output' if project_name != "LPC" else "/nfs/PROBIO3/LPC/autoseq-output"

	cores = row[0]['cores']
	machine_type = row[0]['machine_type'].upper()


	if(cfdna):
		id = cfdna+'_'+normal
	else:
		id = tumor+'_'+normal

	outdir = os.path.join(outdir_root, sdid, id)
	jobdb = os.path.join(outdir, id)+'.jobdb.json'
	log_path = os.path.join(outdir,id)+'.nohup.log'
	isdir = os.path.isdir(outdir)
	
	#script_dir = '/home/prosp/develop/'+ project_name

	try:
		if(not isdir):
			os.makedirs(outdir)
		
		liqbio_prod = current_app.config['LIQBIO_PROD']

		cmd = "nohup autoseq --umi --ref {} --outdir {} --jobdb {} --cores {} --runner_name slurmrunner --scratch {} --libdir {} liqbio {} >> {} &".format(ref_genome, outdir, jobdb, cores, scratch_path, libdir, json_path, log_path)

		#cmd = 'nohup autoseq --umi --ref {} --outdir {} --jobdb {} --cores {} --script-dir {} --runner_name slurmrunner --scratch {} --libdir {} liqbio {} >> {} &'.format(ref_genome, outdir, jobdb, cores, script_dir, scratch_path, libdir, json_path, log_path)

		ssh_cmd = '{};{}'.format(liqbio_prod, cmd)

		machine_type = machine_type if machine_type != '' else 'ANCHORAGE'
		
		# if machine_type:
		machine_config = current_app.config[machine_type]
		ip_address = machine_config['address']
		username = machine_config['username']
		password = machine_config['password']

		out = connectSSHServer(ip_address, password, username, ssh_cmd)

		if(out):
			db.session.execute("UPDATE projects_t SET pro_status='1' WHERE p_id='{}'" .format(project_id))
			db.session.commit()
			db.session.execute("INSERT INTO jobs_t(job_id, project_id, cores, machine_type, pipeline_cmd, log_path, json_path, job_status, create_time, update_time) VALUES (DEFAULT, '{}', '{}', '{}', '{}', '{}', '{}', '0', NOW(), NOW())".format(project_id, cores, machine_type, ssh_cmd, log_path, jobdb))
			db.session.commit()
			
			return {'status': True, 'data': 'Pipeline started successfully', 'error': ''}, 200
		else:
			return {'status': True, 'data': [], 'error': 'Server not connected'}, 200	

	except Exception as e:
		return {'status': False, 'data': [], 'error': str(e)}, 400

def stop_pipeline(project_id):
	try:
		res = db.session.execute("SELECT j.json_path, p.machine_type FROM jobs_t as j INNER JOIN projects_t as p ON p.p_id = j.project_id WHERE p.p_id = '{}'".format(project_id))
		row = generate_list_to_dict(res)
		json_path = row[0]['json_path']
		machine_type = row[0]['machine_type'].upper()

		if os.path.isfile(json_path):
			with open(json_path) as data_file:
				data = json.load(data_file) 

			df = pd.json_normalize(data, 'jobs')
			job_ids = set(df['jobid'])
			job_ids = [x.strip(' ') for x in job_ids]
			cmd = "scancel {}".format(job_ids).replace("', '", "','")

			machine_type = machine_type if machine_type != '' else 'ANCHORAGE'
		
			# if machine_type:
			machine_config = current_app.config[machine_type]
			ip_address = machine_config['address']
			username = machine_config['username']
			password = machine_config['password']
			
			print(cmd)
			'''out = connectSSHServer(ip_address, password, username, cmd)

			if(out):
				db.session.execute("UPDATE projects_t SET pro_status='0' WHERE p_id='{}'" .format(project_id))
				db.session.commit()
				return {'status': True, 'data': 'Pipeline stopped successfully', 'error': ''}, 200
			else:
				return {'status': True, 'data': [], 'error': 'Server not connected'}, 200	
		       '''
		else:
			return {'status': True, 'data': [], 'error': 'Json db file not found'}, 200
		

	except Exception as e:
		return {'status': False, 'data': [], 'error': str(e)}, 400


def edit_analysis_info(project_id):
	try:
		res = db.session.execute("SELECT p.p_id, p.sample_id, p.cores, p.machine_type from projects_t as p WHERE p.p_id ='{}'".format(project_id))
		row = generate_list_to_dict(res)
		return {'status': True, 'data': row, 'error': ''}, 200

	except Exception as e:
		return {'status': False, 'data': [], 'error': str(e)}, 400


def view_analysis_info(project_id):
	try:
		res = db.session.execute("SELECT b.project_name, p.* from projects_t as p INNER JOIN barcodes_t as b ON b.b_id = p.barcode_id WHERE p.p_id ='{}'".format(project_id))
		row = generate_list_to_dict(res)
		return {'status': True, 'data': row, 'error': ''}, 200

	except Exception as e:
		return {'status': False, 'data': [], 'error': str(e)}, 400

def del_analysis_info(project_id):
	try:
		res = db.session.execute("DELETE FROM  projects_t WHERE p_id ='{}'".format(project_id))
		db.session.commit()
		return {'status': True, 'data': 'Sample information deleted successfully', 'error': ''}, 200
	except Exception as e:
		return {'status': False, 'data': [], 'error': str(e)}, 400

def update_analysis_info(project_id, cores, machine_type):
	try:
		db.session.execute("UPDATE projects_t SET  cores = '{}', machine_type ='{}' WHERE p_id ='{}'".format(cores, machine_type, project_id))
		db.session.commit()
		return {'status': True, 'data': 'Machine Core and Type updated successfully', 'error': ''}, 200

	except Exception as e:
		return {'status': False, 'data': [], 'error': str(e)}, 400

def view_log_analysis_info(job_id):
	try:
		res = db.session.execute("SELECT log_path from jobs_t WHERE job_id ='{}' limit 1".format(job_id))
		row = generate_list_to_dict(res)
		log_path = row[0]['log_path']
		if(os.path.isfile(log_path)):
			f=open(log_path, "r")
			contents =f.read()
			f.close()
			if(contents != ""):
				return {'status': True, 'data': contents, 'error': ''}, 200
			else:
				return {'status': True, 'data': '', 'error': 'Log file is empty'}, 200
		else:
			return {'status': True, 'data': [], 'error': 'Log file not found'}, 200
	except Exception as e:
		return {'status': False, 'data': [], 'error': str(e)}, 400


def get_job_status_info(job_id):
	try:
		res = db.session.execute("SELECT json_path from jobs_t WHERE job_id ='{}' limit 1".format(job_id))
		row = generate_list_to_dict(res)
		json_path = row[0]['json_path']
		if(os.path.isfile(json_path)):
			with open(json_path) as json_file:
				json_data = json.load(json_file)
			
			return {'status': True, 'data': json_data, 'error': ''}, 200
		else:
			return {'status': True, 'data': [], 'error': 'Job flow file not found'}, 200
	except Exception as e:
		return {'status': False, 'data': [], 'error': str(e)}, 400

def del_job_info(job_id):
	try:
		res = db.session.execute("DELETE FROM  jobs_t WHERE job_id ='{}'".format(job_id))
		db.session.commit()
		return {'status': True, 'data': 'Job information deleted successfully', 'error': ''}, 200
	except Exception as e:
		return {'status': False, 'data': [], 'error': str(e)}, 400

def get_out_log_info(out_path):
	try:
		if(os.path.isfile(out_path)):
			f=open(out_path, "r")
			contents =f.read()
			f.close()
			return {'status': True, 'data': contents, 'error': ''}, 200
		else:
			return {'status': True, 'data': [], 'error': 'Out log file not found'}, 200
	except Exception as e:
		return {'status': False, 'data': [], 'error': str(e)}, 400


def syn_data_server(project_name, cutm_id, anch_user, anch_pwd):
	try:
		project_folder = "PB-" if (project_name == "PROBIO") else "PSFF"
		current_date = datetime.today().strftime("%Y-%m-%d")

		log_path = current_app.config[project_name]+'rsyn_'+cutm_id+'_'+current_date+'.nohup.log'

		cmd = "nohup rsync -e ssh -avP cust001@caesar.scilifelab.se:/home/cust001/inbox/{}/{}* /nfs/{}/INBOX >> {} &".format(cutm_id, project_folder, project_name, log_path)
		machine_config = current_app.config['ANCHORAGE']
		ip_address = machine_config['address']

		out = connectSSHServer(ip_address, anch_pwd, anch_user, cmd)
		if(out):
			return {'status': True, 'data': 'Data Sync started successfully', 'error': ''}, 200
		else:
			return {'status': True, 'data': '', 'error': 'Server not connected'}, 200

	except Exception as e:
		return {'status': False, 'data': [], 'error': str(e)}, 400
