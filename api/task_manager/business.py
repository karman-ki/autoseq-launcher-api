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

def validate_cfdna_file_size(file_arr):
    cfdna_group = [[[w,x] for w,x,y,z in g] for k,g in  groupby(file_arr,key=itemgetter(2))]
    for cf in cfdna_group:
        if len(cf) >= 2:
            symb_source_dir = cf[1][1]
            source_dir = cf[0][1]
            target_dir = cf[0][1] + '_orig'

            isdir = os.path.isdir(target_dir)
            if(not isdir):
                os.makedirs(target_dir)
            else:
                print('directory already created : {}'.format(target_dir))

            file_names = os.listdir(source_dir)
            for file_name in file_names:
                shutil.move(os.path.join(source_dir, file_name), target_dir)
                os.symlink(os.path.join(target_dir, file_name), os.path.join(symb_source_dir, file_name))

            if len(os.listdir(source_dir) ) == 0:
                os.rmdir(source_dir)
                print("Directory is empty")
            else:
                print("Directory is not empty")

def generate_barcode_files(barcode_filename, files):
    with open(barcode_filename, 'w') as filehandle:
        for f in files:
            filehandle.write('%s\n' % f)

def get_file_list(proj_nfs_path, sample_pattern):
    lst = os.listdir(proj_nfs_path)
    lst.sort()
    file_lst_arr = []
    for f in os.listdir(proj_nfs_path):
        sample_id = f.split('-')[2]
        if fnmatch.fnmatch(f, sample_pattern):
            file_path = os.path.join(proj_nfs_path, f)
            file_size = subprocess.check_output(['du','-sh', file_path]).split()[0].decode('utf-8')
            file_lst_arr.append([file_size, file_path, f, fnmatch.fnmatch(f, '*-CFDNA-*')])
    return file_lst_arr

def generate_autoseq_config(barcode_filename, config_path):
    isdir = os.path.isdir(config_path)
    if(not isdir):
        os.makedirs(config_path)
    try:
        cmd = 'autoseq liqbio-prepare --outdir {} {}'.format(config_path, barcode_filename)
        subprocess.call(cmd , shell=True)
        return True
    except Exception as e:
        return {'status': True, 'data': [], 'error': str(e)}, 400


def insert_project_config(barcode_id, config_path):
    try : 
        file_list = os.listdir(config_path)
        for f in file_list:
            config_path = os.path.join(config_path, f)
            with open(config_path) as json_file:
                data = json.load(json_file)
                cfdna = '|'.join(data['CFDNA'])
                normal = '|'.join(data['N'])
                tumor = '|'.join(data['T'])
                sample_id = data['sdid']
                try:
                    db.session.execute("INSERT INTO projects_t(p_id, barcode_id, sample_id, cfdna, normal, tumor, config_path, pro_status, create_time, update_time) VALUES (DEFAULT, '{}', '{}', '{}', '{}', '{}', '{}', '0', NOW(), NOW())".format(barcode_id, sample_id, cfdna, normal, tumor, config_path))
                    db.session.commit()
                except Exception as e:
                    return {'status': True, 'data': [], 'error': str(e)}, 400
        return True
    except Exception as e:
        return {'status': True, 'data': [], 'error': str(e)}, 400


def check_db_connection():
    try:
        res = db.session.execute("select count(*) as count from barcodes_t")
        row = generate_list_to_dict(res)
        return {'status': True, 'data': row, 'error': ''}, 200
    except Exception as e:
        return {'status': True, 'data': [], 'error': str(e)}, 400

def generate_barcodes(project_name, search_pattern, sample_arr, file_name):

    nfs_path = current_app.config[project_name]
    project_name = 'PB' if project_name == 'PROBIO' else project_name

    project_nfs_path = nfs_path +'INBOX/'

    if(search_pattern):
        sample_pattern = project_name+'-*'+search_pattern
        file_info_arr = get_file_list(project_nfs_path, sample_pattern)
    else:
        search_pattern = file_name
        file_lst_arr = sample_arr.split(',')
        file_info_arr = []

        for f in file_lst_arr:
            proj_nfs_path = os.path.join(project_nfs_path, f)
            if(os.path.isdir(proj_nfs_path)):
                file_size = subprocess.check_output(['du','-sh', proj_nfs_path]).split()[0].decode('utf-8')
                file_info_arr.append([file_size, proj_nfs_path, f, fnmatch.fnmatch(f, '*-CFDNA-*')])
        

    if(file_info_arr):
        validate_cfdna_file_size(file_info_arr)

        curr_file_arr = [x[2] for i, x in enumerate(file_info_arr)]

        current_date = datetime.today().strftime("%Y-%m-%d")
        barcode_dir = nfs_path+'sample_lists/'
        barcode_filename = barcode_dir + 'clinseqBarcodes_'+current_date+'.txt'
        generate_barcode_files(barcode_filename, curr_file_arr)
        config_path = nfs_path+'config/'+current_date
        try:
            res = db.session.execute("INSERT INTO barcodes_t(b_id, project_name, search_pattern, barcode_path, config_path, bar_status, create_time, update_time) VALUES (DEFAULT, '{}', '{}', '{}', '{}', '0', NOW(), NOW()) RETURNING *".format(project_name, search_pattern, barcode_filename, config_path))
            db.session.commit()
            row = generate_list_to_dict(res)
            generate_autoseq_config(barcode_filename, config_path)
            row[0]['file_list'] = curr_file_arr

            return {'status': True, 'data': row, 'error': ''}, 200
        except Exception as e:
            return {'status': True, 'data': [], 'error': str(e)}, 400
    else:
        return {'status': True, 'data': file_info_arr, 'error': ''}, 200


def generate_configs(barcode_id):
    res = db.session.execute("SELECT b_id, config_path from barcodes_t WHERE b_id ='{}'".format(barcode_id))
    row = generate_list_to_dict(res)
    barcode_id = row[0]['b_id']
    config_path = row[0]['config_path']
    insert_project_config(barcode_id, config_path)
    return {'status': True, 'data': row, 'error': ''}, 200

def get_barcode_list():
    try:
        res = db.session.execute("select * from barcodes_t order by b_id desc")
        row = generate_list_to_dict(res)
        return {'status': True, 'data': row, 'error': ''}, 200
    except Exception as e:
        return {'status': True, 'data': [], 'error': str(e)}, 400

def get_project_list():
    try:
        res = db.session.execute("select * from projects_t order by p_id desc")
        row = generate_list_to_dict(res)
        return {'status': True, 'data': row, 'error': ''}, 200
    except Exception as e:
        return {'status': True, 'data': [], 'error': str(e)}, 400

def get_job_list():
    try:
        res = db.session.execute("select * from jobs_t order by job_id desc")
        row = generate_list_to_dict(res)
        return {'status': True, 'data': row, 'error': ''}, 200
    except Exception as e:
        return {'status': True, 'data': [], 'error': str(e)}, 400


def save_orderform(data):
    jsondata = json.loads(data)
    return {'status': True, 'data': jsondata, 'error': ''}, 200


def start_pipeline(project_id):
    print(project_id)
    res = db.session.execute("SELECT b.project_name, p.sample_id, p.cfdna, p.normal, p.config_path, p.pro_status, CASE WHEN p.cores IS NULL THEN '8' ELSE p.cores END as cores, CASE WHEN p.machine_type IS NULL THEN '' ELSE p.machine_type END as machine_type from projects_t as p INNER JOIN barcodes_t as b ON b.b_id = p.barcode_id WHERE p.p_id ='{}' and p.pro_status='0' order by p.p_id desc limit 1".format(project_id))
    row = generate_list_to_dict(res)
    print(row)
    project_name = row[0]['project_name']
    sdid = row[0]['sample_id']
    cfdna = row[0]['cfdna']
    normal = row[0]['normal']
    json_path = row[0]['config_path']

    ref_genome = current_app.config['REF_GENOME_PATH']
    scratch_path = current_app.config['SCRATCH_PATH']
    libdir = current_app.config['LIB_PATH']
    outdir_root = current_app.config[project_name]+'autoseq-output'
    cores = row[0]['cores']
    machine_type = row[0]['machine_type'].upper()


    id = cfdna+'_'+normal

    outdir = os.path.join(outdir_root, sdid, id)
    jobdb = os.path.join(outdir, id)+'.jobdb.json'
    log_path = os.path.join(outdir,id)+'.nohup.log'
    isdir = os.path.isdir(outdir)

    try:
        if(not isdir):
            os.makedirs(outdir)
        
        cmd = 'nohup autoseq --umi --ref {} --outdir {} --jobdb {} --cores {} --runner_name slurmrunner --scratch {} --libdir {} liqbio {} >> {} &'.format(ref_genome, outdir, jobdb, cores, scratch_path, libdir, json_path, log_path)


        if machine_type:
            machine_config = current_app.config[machine_type]
            ip_address = machine_config['address']
            username = machine_config['username']
            password = machine_config['password']

            print(ip_address, password, username)

            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=ip_address,username=username, password=password)

            print("Successful connection", ip_address)
            ssh_client.invoke_shell()

            ssh_cmd = 'source /nfs/PROBIO/liqbio-dotfiles/.bash_profile; {}'.format(cmd)

            print(ssh_cmd)

            command = {
                1:ssh_cmd
            }
            
            result = ''
            for key,value in command.items():
                stdin,stdout,stderr=ssh_client.exec_command(value, get_pty=True)
                outlines=stdout.readlines()
                result=''.join(outlines)
            

            ssh_client.close()
        else: 
            print('else', cmd)
            result = subprocess.check_output(cmd, shell=True, universal_newlines=True)

        db.session.execute("UPDATE projects_t SET pro_status='1' WHERE p_id='{}'" .format(project_id))
        db.session.commit()
        db.session.execute("INSERT INTO jobs_t(job_id, project_id, cores, machine_type, log_path, job_status, create_time, update_time) VALUES (DEFAULT, '{}', '{}', '{}', '{}', '0', NOW(), NOW())".format(project_id, cores, machine_type, log_path))
        db.session.commit()
        
        return {'status': True, 'data': result, 'error': str(e)}, 200
        
    except Exception as e:
        return {'status': True, 'data': [], 'error': str(e)}, 400


def edit_analysis_info(project_id):
    try:
        res = db.session.execute("SELECT p.p_id, p.sample_id, p.cores, p.machine_type from projects_t as p WHERE p.p_id ='{}'".format(project_id))
        row = generate_list_to_dict(res)
        return {'status': True, 'data': row, 'error': ''}, 200

    except Exception as e:
        return {'status': True, 'data': [], 'error': str(e)}, 400


def update_analysis_info(project_id, cores, machine_type):
    try:
        db.session.execute("UPDATE projects_t SET  cores = '{}', machine_type ='{}' WHERE p_id ='{}'".format(cores, machine_type, project_id))
        db.session.commit()
        return {'status': True, 'data': 'update successfully', 'error': ''}, 200

    except Exception as e:
        return {'status': True, 'data': [], 'error': str(e)}, 400