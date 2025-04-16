#!/usr/bin/env python

import os

# determine data directory, run folders, and run templates
in_bucket="s3://lifespan-seg-model-data/raw/images_fragileX_renamed" # where to output data
out_bucket="s3://lifespan-seg-model-data/preprocessed/T1-only/images" # bucket that BIDS data will be pulled from and processed outputs will be pushed to
run_folder="/users/1/lundq163/projects/lifespan_preproc/preproc_data_wrapper"
# ses_id="2YearFollowUpYArm1" #comment out if using csv
preproc_data_folder="{run_folder}/run_files.preproc_data".format(run_folder=run_folder)
preproc_data_template="template.preproc_data_ABCD"

# if run folders exist delete them and recreate
if os.path.isdir(preproc_data_folder):
	os.system('rm -rf {preproc_data_folder}'.format(preproc_data_folder=preproc_data_folder))
	os.makedirs("{preproc_data_folder}/logs".format(preproc_data_folder=preproc_data_folder))
else:
	os.makedirs("{preproc_data_folder}/logs".format(preproc_data_folder=preproc_data_folder))

#if you have a two column csv

with open(os.path.join(run_folder, 'abcd_qc_zero.csv')) as f:
    lines=f.readlines()
    bids_subjs = list()
    bids_ses = list()
    for line in lines:
      subj,ses=line.split(",")
      bids_subjs.append(subj)
      bids_ses.append(ses.strip('\n'))
      
count=0
for bids_subj in bids_subjs:
      sub_id=bids_subj.strip('sub-')
      ses_id=bids_ses[count].strip('ses-')
      os.system('sed -e "s|SUBJECTID|{sub_id}|g" -e "s|SESSIONID|{ses_id}|g" -e "s|INBUCKET|{in_bucket}|g" -e "s|OUTBUCKET|{out_bucket}|g" -e "s|RUNDIR|{run_folder}|g" {run_folder}/{preproc_data_template} > {preproc_data_folder}/run{k}'.format(k=count,preproc_data_folder=preproc_data_folder,run_folder=run_folder,sub_id=sub_id,ses_id=ses_id,in_bucket=in_bucket,preproc_data_template=preproc_data_template,out_bucket=out_bucket))
      count+=1
# change permissions of generated run files
os.system('chmod 775 -R {preproc_data_folder}'.format(preproc_data_folder=preproc_data_folder))
 

