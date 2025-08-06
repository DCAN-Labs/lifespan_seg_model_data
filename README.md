# How to run the internal preprocessing for the data used in the lifespan segmentation model
## Notes before starting
- Only set up for T1_only model training at the moment
- For now, curated specifically for the ADNI and fragileX datasets
- The wrapper is split into two separate parts because the MSI modules for freesurfer and ants have conflicts
## Step 1a - Rename any files if necessary
T1w image files need to be in the format `${age}mo_ds-${dataset}_sub-${sub_id}_0000.${images_ext}` while the corresponding label files need to be in the format `${age}mo_ds-${dataset}_sub-${sub_id}.${labels_ext}` before feeding them in to the preprocessing wrapper. In order to get files into this format, we need to run the `rename_data_files.py` script on a BIDS valid input directory. A specific file is used below as an example when filling in the arguments to the script, but this script can work on all files within a set of subjects as long as a `participants.tsv` is utilized.

Information on the file name fields:
- `${age}` -> Integer value for the participant age in months. This information can be located in the participants.tsv for a given dataset, assuming it is BIDS valid. 
- `${dataset}` -> A unique identifier of source for a data file
- `${sub_id}` -> Unique subject identifier
- `${images_ext}` -> The file extension of a given image file. This is likely either going to be `nii.gz` or `mgz`. The preprocessing scripts are currently only set up for one or the other.
- `${labels_ext}` -> The file extension of a given label file. This is likely either going to be `nii.gz` or `mgz`. The preprocessing scripts are currently only set up for one or the other.  

### To rename the files, execute the following python command:  
`python ./rename_data_files.py <base_directory> <relative_path_template> <dataset_name> <participants_file> <t1_identifier> <aseg_identifier> <output_directory>`

### Information on the required arguments:
- `<base_directory>` is the path to the project root directory where the parent subject directories live. As an example, if attempting to rename a file with the path of `/usr/projects/bids_dataset/sub-1234/ses-1234/anat/sub-1234_ses-1234_acq-1234_T1w.mgz` the `<base_directory>` argument would be `/usr/projects/bids_dataset`.
- `<relative_path_template>` would be the relative path to the anatomical or segmentation files within each subject folder. The code utilizes the `participants.tsv` to gather the unique subject IDs and can also take into account a placeholder field for session IDs and will refer back to the `participants.tsv` again to fill that field in automatically based on what sessions are available for a given subject. Building off of the example above, the `<relative_path_template>` would be something like `/ses-{session}/anat`.
- `<dataset_name>` is a string that will get added as a unique identifier for files from a subject that belongs to a given dataset. For our example we will use the string "test".
- `<participants_file>` is the absolute path to the `participants.tsv` describing what is available within the base directory. The `participants.tsv` must have headers for "participant_id" and "age", while "session_id" is optional. The "age" information must be in years. Using our example above, the inputted `participants.tsv` would look something like `/usr/projects/bids_dataset/participants.tsv` and the contents would look something like:
```
participant_id  session_id  age
sub-1234    ses-1234    12
```
- `<t1_identifier>` is as string that is used to identify which file is the actual anatomical image that needs renaming. Based on the example above, the input to this argument would be the string "T1w.mgz"
- `<aseg_identifier>` is an input similar to the argument above, but instead distinguishes the segmentation file in particular from the other files in the directory. An example would be something like "aseg.mgz"
- `<output_directory>` would be the absolute path to where the renamed files will get produced. For our example, the input to this argument would be `/usr/projects/bids_dataset_renamed`, and after running the script, the full path of the renamed file will result in `/usr/projects/bids_dataset_renamed/images_test_renamed/144mo_ds-test_sub-1234_ses-1234_0000.mgz`

## Step 1b - Running part 1 of data preprocessing
Part 1 of data preprocessing includes converting anatomical images and label files to `.nii.gz` if needed, reorienting and overwriting the image and label file, then relabeling the segmentations using `./preproc_data_wrapper/relabeling.py`. Note that these preprocessing steps are currently only catered for the ADNI and fragileX datasets. 
1. Within the `preproc_data_wrapper` folder, edit the following variables in the `make_run_files_s3_part1.sh` file if needed: `in_bucket` and `out_bucket`. These likely wont need to be edited though, as the variables are typically just `"s3://lifespan-seg-model-data/raw"` for both. 
2. Execute the `make_run_files_s3_part1.sh` script. This will require one argument identifying the dataset name. So based on our example above, the command will look something like `./preproc_data_wrapper/make_run_files_s3_part1.sh test`. This will then make a unique run file based on the template `template.preproc_data_part1` for whatever file is available within `${in_bucket}/labels_${dataset}_renamed/`, and the run files will then be stored in a folder called `./preproc_data_wrapper/run_files_test.preproc_data_part1`. 
3. Check the `./preproc_data_wrapper/resources_preproc_data_part1.sh` to make sure parameters are properly specified. Parameters that may need editing in particular are `--mail-user`, `-p`, `-o`, `-e`, and `-A`.
4. Submit the jobs with the following command: `./preproc_data_wrapper/submit_preproc_data_part1.sh 0-10 test`. The two additional arguments are an example array and example name for the dataset. The final outputs from our example will be here: `${out_bucket}/images_test_renamed_relabeled/` and `${out_bucket}/labels_test_renamed_relabeled/`

## Step 2 - Running part 2 of data preprocessing
Part 2 of data preprocessing includes applying spatial transformations with antsApplyTransforms to align segmentations with the anatomical image using nearest neighbor interpolation, then converts the datatypes of the data within both the image and label files to integer values.
1. Within the `preproc_data_wrapper` folder, edit the following variables in the `make_run_files_s3_part2.sh` file if needed: `in_bucket` and `out_bucket`. These likely wont need to be edited though, as the variables are typically just `"s3://lifespan-seg-model-data/raw"` and `"s3://lifespan-seg-model-data/preprocessed/T1-only"` respectively.
2. Execute the `make_run_files_s3_part2.sh` script. This will require one argument identifying the dataset name. So based on our example above, the command will look something like `./preproc_data_wrapper/make_run_files_s3_part2.sh test`. This will then make a unique run file based on the template `template.preproc_data_part2` for whatever file is available within `${in_bucket}/labels_${dataset}_renamed_relabeled/`, and the run files will then be stored in a folder called `./preproc_data_wrapper/run_files_test.preproc_data_part2`.
3. Check the `./preproc_data_wrapper/resources_preproc_data_part2.sh` to make sure parameters are properly specified. Parameters that may need editing in particular are `--mail-user`, `-p`, `-o`, `-e`, and `-A`.  
4. Submit the jobs with the following command: `./preproc_data_wrapper/submit_preproc_data_part2.sh 0-10 test`. The two additional arguments are an example array and example name for the dataset. The final outputs from our example will be here: `${out_bucket}/images/` and `${out_bucket}/labels/`

## Further information about current files and directories in this project
### Additional scripts within the `preproc_data_wrapper` folder
- There are currently 4 python scripts that could be used for relabeling the input segmentations, however, only `relabeling.py` is relevant at the moment. 
- There is also an additional script for making run files called `make_run_files_based_on_csv.py` and may become relevant if ABCD data is included in the future. 
### `data-for-lssm` and `notebooks-for-lssm` directories
- `data-for-lssm` is used to store open access information on all of the images and labels that could be used for training.
- `notebooks-for-lssm` contains jupyter notebooks used to curate the specific images and labels from the open access data that had exceptional quality scores in which we can use for training. 
### `harmonize_adni_for_curated.sh` and `label_check.sh`
- `harmonize_adni_for_curated.sh` is a script that is used to determine if there are any preprocessed label files that are missing a corresponding image file. If there is a missing image file, then the corresponding label file will be removed. The inputs for this script are a directory containing all available image files for a given dataset and a directory containing all available label files for a given dataset.  
- `label_check.sh` is a script that checks what labels are currently present within a given label file, and what labels are missing from a given label file. The input is a directory containing all label files of interest that need to be checked. 