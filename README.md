# How to run the internal preprocessing for the data used in the lifespan segmentation model
## Notes before starting
- Only set up for T1_only model training at the moment
- For now, curated specifically for the ADNI and fragileX datasets
## Step 1a - Rename any files if necessary
T1w image files need to be in the format `${age}mo_ds-${dataset}_sub-${sub_id}_0000.${images_ext}` while the corresponding label files need to be in the format `${age}mo_ds-${dataset}_sub-${sub_id}.${labels_ext}` before feeding them in to the preprocessing wrapper. 
Information on the file name fields:
- `${age}` -> Integer value for the participant age in months. This information can be located in the participants.tsv for a given dataset, assuming it is BIDS valid. 
- `${dataset}` -> A unique identifier of source for a data file
- `${sub_id}` -> Unique subject identifier
- `${images_ext}` -> The file extension of a given image file. This is likely either going to be `nii.gz` or `mgz`. The preprocessing scripts are currently only set up for one or the other.
- `${labels_ext}` -> The file extension of a given label file. This is likely either going to be `nii.gz` or `mgz`. The preprocessing scripts are currently only set up for one or the other.