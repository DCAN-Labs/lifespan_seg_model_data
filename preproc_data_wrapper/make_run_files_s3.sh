#!/bin/bash 

set +x 
# determine data directory, run folders, and run templates
dataset=$1
in_bucket="s3://lifespan-seg-model-data/raw"
out_bucket="s3://lifespan-seg-model-data/preprocessed/T1-only"
data_dir="/tmp"
run_folder=`pwd`

preproc_folder="${run_folder}/run_files_${dataset}.preproc_data"
preproc_template="template.preproc_data"

# if processing run folders exist delete them and recreate
if [ -d "${preproc_folder}" ]; then
	rm -rf "${preproc_folder}"
	mkdir -p "${preproc_folder}/logs"
else
	mkdir -p "${preproc_folder}/logs"
fi

# counter to create run numbers
k=0

for i in `s3cmd ls ${in_bucket}/labels_${dataset}_renamed/ | awk '{print $4}'`; do
	sub_text=`echo ${i} | awk -F"/" '{print $(NF-0)}' | awk -F"_" '{print $3}' | awk -F"-" '{print $1}'`
	i_trimmed=`echo ${i} | awk -F"/" '{print $(NF-0)}'`
	if [ "sub" = "${sub_text}" ]; then # if parsed text matches to "sub", continue
		subj_id=`echo ${i} | awk -F"/" '{print $(NF-0)}' | awk -F"_" '{print $3}' | awk -F"-" '{split($2, a, /[_\.]/); print a[1]}'`
		age=`echo $i | awk -F"/" '{print $(NF-0)}' | awk -F"_" '{print $1}' | awk '{gsub(/mo$/,""); print}'`
		if [[ `echo ${i} | awk -F"/" '{print $(NF-0)}'` == *"ses"* ]]; then
			ses_id=`echo ${i} | awk -F"/" '{print $(NF-0)}' | awk -F"_" '{print $3}' | awk -F"-" '{split($3, a, /[_\.]/); print a[1]}'`
			labels_ext=`echo ${i} | awk -F"/" '{print $(NF-0)}' | sed 's/^[^.]*\.//'`
			for j in `s3cmd ls ${in_bucket}/images_${dataset}_renamed/ | awk '{print $4}'`; do
				j_trimmed=`echo ${j} | sed 's/_0000//g' | awk -F"/" '{print $(NF-0)}'`
				if [[ ${i_trimmed} == ${j_trimmed} ]]; then
					images_ext=`echo ${j} | awk -F"/" '{print $(NF-0)}' | sed 's/^[^.]*\.//'`
				fi
			done
			sed -e "s|SUBJECTID|${subj_id}|g" -e "s|AGEMO|${age}|g" -e "s|SESID|${ses_id}|g" -e "s|LABELSEXT|${labels_ext}|g" -e "s|IMAGESEXT|${images_ext}|g" -e "s|DATASET|${dataset}|g" -e "s|INBUCKET|${in_bucket}|g" -e "s|OUTBUCKET|${out_bucket}|g" -e "s|DATADIR|${data_dir}|g" -e "s|RUNDIR|${run_folder}|g" ${run_folder}/${preproc_template} > ${preproc_folder}/run${k}
			k=$((k+1))
		else
			ses_id="None"
			labels_ext=`echo ${i} | awk -F"/" '{print $(NF-0)}' | sed 's/^[^.]*\.//'`
			for j in `s3cmd ls ${in_bucket}/images_${dataset}_renamed/ | awk '{print $4}'`; do
				j_trimmed=`echo ${j} | sed 's/_0000//g' | awk -F"/" '{print $(NF-0)}'`
				if [[ ${i_trimmed} == ${j_trimmed} ]]; then
					images_ext=`echo ${j} | awk -F"/" '{print $(NF-0)}' | sed 's/^[^.]*\.//'`
				fi
			done
			sed -e "s|SUBJECTID|${subj_id}|g" -e "s|AGEMO|${age}|g" -e "s|SESID|${ses_id}|g" -e "s|LABELSEXT|${labels_ext}|g" -e "s|IMAGESEXT|${images_ext}|g" -e "s|DATASET|${dataset}|g" -e "s|INBUCKET|${in_bucket}|g" -e "s|OUTBUCKET|${out_bucket}|g" -e "s|DATADIR|${data_dir}|g" -e "s|RUNDIR|${run_folder}|g" ${run_folder}/${preproc_template} > ${preproc_folder}/run${k}
			k=$((k+1))
		fi
	fi
done

chmod 775 -R ${preproc_folder}
