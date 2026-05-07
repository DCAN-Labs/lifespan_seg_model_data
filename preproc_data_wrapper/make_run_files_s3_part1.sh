#!/bin/bash 

# determine data directory, run folders, and run templates
dataset=$1
in_bucket="s3://lifespan-seg-model-data/raw"
out_bucket="s3://lifespan-seg-model-data/raw"
data_dir="/tmp"
run_folder=`pwd`

preproc_folder="${run_folder}/run_files_${dataset}.preproc_data_part1"
preproc_template="template.preproc_data_part1"

# if processing run folders exist delete them and recreate
if [ -d "${preproc_folder}" ]; then
	rm -rf "${preproc_folder}"
	mkdir -p "${preproc_folder}"
else
	mkdir -p "${preproc_folder}"
fi

# counter to create run numbers
k=0

# First, create an associative array to store image information
declare -A image_info
while IFS= read -r j; do
	j_trimmed=$(echo "$j" | sed 's/_0000//g' | awk -F"/" '{print $(NF-0)}' | awk -F"." '{print $1}')
	images_ext=$(echo "$j" | awk -F"/" '{print $(NF-0)}' | sed 's/^[^.]*\.//')
	image_info["$j_trimmed"]="$images_ext"
done < <(s3cmd ls "${in_bucket}/images_${dataset}_renamed/" | awk '{print $4}')

# Process labels with the cached image information
while IFS= read -r i; do
	sub_text=$(echo "$i" | awk -F"/" '{print $(NF-0)}' | awk -F"_" '{print $3}' | awk -F"-" '{print $1}')
	i_trimmed=$(echo "$i" | awk -F"/" '{print $(NF-0)}' | awk -F"." '{print $1}')
	
	if [ "sub" = "${sub_text}" ]; then
		subj_id=$(echo "$i" | awk -F"/" '{print $(NF-0)}' | awk -F"_" '{print $3}' | awk -F"-" '{split($2, a, /[_\.]/); print a[1]}')
		age=$(echo "$i" | awk -F"/" '{print $(NF-0)}' | awk -F"_" '{print $1}' | awk '{gsub(/mo$/,""); print}')
		labels_ext=$(echo "$i" | awk -F"/" '{print $(NF-0)}' | sed 's/^[^.]*\.//')
		images_ext="${image_info[$i_trimmed]}"
		
		if [[ $(echo "$i" | awk -F"/" '{print $(NF-0)}') == *"ses"* ]]; then
			ses_id=$(echo "$i" | awk -F"/" '{print $(NF-0)}' | awk -F"-" '{print $4}' | awk -F"[_.]" '{print $1}')
		else
			ses_id="None"
		fi
		
		sed -e "s|SUBJECTID|${subj_id}|g" \
			-e "s|AGEMO|${age}|g" \
			-e "s|SESID|${ses_id}|g" \
			-e "s|LABELSEXT|${labels_ext}|g" \
			-e "s|IMAGESEXT|${images_ext}|g" \
			-e "s|DATASET|${dataset}|g" \
			-e "s|INBUCKET|${in_bucket}|g" \
			-e "s|OUTBUCKET|${out_bucket}|g" \
			-e "s|DATADIR|${data_dir}|g" \
			-e "s|RUNDIR|${run_folder}|g" \
			"${run_folder}/${preproc_template}" > "${preproc_folder}/run${k}"
		
		k=$((k+1))
	fi
done < <(s3cmd ls "${in_bucket}/labels_${dataset}_renamed/" | awk '{print $4}')

chmod 775 -R ${preproc_folder}
