#!/usr/bin/env python

import os
import fnmatch
import subprocess
from operator import itemgetter
from itertools import groupby
import shutil
from datetime import date
import argparse
import json
import time
import yaml


def readConfig(section,filename="curator_config.yml"):
    with open(filename, "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
        section = cfg[section]
    return section

def get_file_list(proj_path, file_pattern, size_boolean):
    lst = os.listdir(proj_path)
    lst.sort()
    file_lst_arr = []
    for file in lst:
        sample_id = file.split('-')[2]
        if fnmatch.fnmatch(file, file_pattern):
            file_size = subprocess.check_output(['du','-sh', os.path.join(proj_path, file)]).split()[0].decode('utf-8')
            if(size_boolean):
                file_lst_arr.append([file_size, os.path.join(proj_path, file), fnmatch.fnmatch(file, '*-CFDNA-*')])
            else:
                file_lst_arr.append(file)
    return file_lst_arr



def validate_cfdna_file_size(file_arr):
    cfdna_group = [[[x,y] for x,y,z in g] for k,g in  groupby(file_arr,key=itemgetter(2))]

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

def generate_autoseq_config(barcode_filename, config_path):
    isdir = os.path.isdir(config_path)
    if(not isdir):
        os.makedirs(config_path)

    try:
        cmd = 'autoseq liqbio-prepare --outdir {} {}'.format(config_path, barcode_filename)
        subprocess.call(cmd , shell=True)
    except OSError:
        pass

def start_pipeline(config_path, outdir_root, scratch_path, ref_genome, libdir, cores):
    file_list = os.listdir(config_path)
    for f in file_list:
        json_path = os.path.join(config_path, f)
        print(json_path)
        sdid = os.path.splitext(f)[0]
        with open(json_path) as json_file:
            outdir = ''
            data = json.load(json_file)
            cfdna = data['CFDNA'][0]
            normal = data['N'][0]
            sdid = data['sdid']
            tumor = data['T']
            id = cfdna+'_'+normal
            outdir = os.path.join(outdir_root, sdid, id)
            jobdb = os.path.join(outdir, id)+'.jobdb.json'
            log_path = os.path.join(outdir,id)+'.nohup.log'
            isdir = os.path.isdir(outdir)
            if(not isdir):
                os.makedirs(outdir)
            else:
                print('Output Directory already created : {} \n'.format(outdir))

            cmd = 'nohup autoseq --umi --ref {} --outdir {} --jobdb {} --cores {} --runner_name slurmrunner --scratch {} --libdir {} liqbio {} >> {} &'.format(ref_genome, outdir, jobdb, cores, scratch_path, libdir, json_path, log_path)
            subprocess.call(cmd , shell=True)
            time.sleep(10)



def main():
    
    parser = argparse.ArgumentParser(description='Curation Automation inputs')

    parser.add_argument("-p","--project_name", required=True, help="Project name")
    parser.add_argument("-s", "--sample_pattern", required=True, help="Sample pattern")
    parser.add_argument("-c", "--cores", default='8', help="Sample pattern")
    args = parser.parse_args()

    project_name = args.project_name
    sample_pattern = args.sample_pattern
    cores = args.cores

    config_params = readConfig('curator')
    
    nfs_path = config_params['nfs']
    ref_genome = config_params['refGenome']
    libdir = config_params['library']
    scratch_path = config_params['scratch']


    outdir = nfs_path + project_name+'/autoseq-output'

    proj_path = nfs_path + project_name + '/INBOX/'
    file_pattern  = project_name+'-*'+sample_pattern
    barcode_dir = nfs_path+'sample_lists/'
    
    file_arr = get_file_list(proj_path, file_pattern, True)

    validate_cfdna_file_size(file_arr)

    curr_file_arr = get_file_list(proj_path, file_pattern, False)

    today = date.today()
    d = today.strftime("%Y-%m-%d")
    barcode_filename = barcode_dir + 'clinseqBarcodes_'+d+'.txt'
    generate_barcode_files(barcode_filename, curr_file_arr)

    config_path = nfs_path+'config/'+d
    generate_autoseq_config(barcode_filename, config_path)

    start_pipeline(config_path, outdir, scratch_path, ref_genome, libdir, cores)

if __name__ == "__main__":
    main()