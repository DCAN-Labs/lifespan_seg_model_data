#!/bin/bash

source /home/faird/shared/code/external/envs/miniconda3/load_miniconda3.sh

# Check if directory argument was provided
if [ -z "$1" ]; then
  echo "Usage: $0 <directory_path>"
  echo "Please provide the directory containing your image files"
  exit 1
fi

INPUT_DIR="$1"

# Create a file with your custom lookup table labels
echo "0 1 2 3 4 5 6 7 8 10 11 12 13 14 15 16 17 18 24 26 28 30 31 41 42 43 44 46 47 49 50 51 52 53 54 58 60 62 63 77 85 172" > dcan_lookup_labels.txt

# Initialize the output file
echo "Summary of label differences:" > output.txt
echo "================================" >> output.txt

# Process files with Python
python -c "
import nibabel as nib
import numpy as np
import os
import sys
import glob

# Get input directory from command line argument
input_dir = '$INPUT_DIR'

# Initialize sets to track all unique missing and extra labels
all_missing_labels = set()
all_extra_labels = set()

# Load your custom lookup table labels
with open('dcan_lookup_labels.txt', 'r') as f:
    lookup_labels = set([int(x) for x in f.read().split()])

# Find all .mgz and .nii.gz files in the input directory
file_patterns = [
    os.path.join(input_dir, '*.nii.gz'),
    os.path.join(input_dir, '*.mgz')
]

files_to_process = []
for pattern in file_patterns:
    files_to_process.extend(glob.glob(pattern))

print(f'Found {len(files_to_process)} files to process')

# Process each file
for filename in files_to_process:
    try:
        print(f'Processing {filename}')
        # Load the file and get unique labels
        data = nib.load(filename).get_fdata()
        file_labels = set(np.unique(data).astype(int))
        
        # Find missing and extra labels
        missing_labels = lookup_labels - file_labels
        extra_labels = file_labels - lookup_labels
        
        # Update our master sets
        all_missing_labels.update(missing_labels)
        all_extra_labels.update(extra_labels)
        
        # Write individual file results
        with open('output.txt', 'a') as f:
            f.write(f'\\nFile: {os.path.basename(filename)}\\n')
            if missing_labels:
                f.write(f'Missing labels: {sorted(missing_labels)}\\n')
            else:
                f.write('No missing labels\\n')
            
            if extra_labels:
                f.write(f'Extra labels: {sorted(extra_labels)}\\n')
            else:
                f.write('No extra labels\\n')
            f.write('----------------------------------------\\n')
    except Exception as e:
        with open('output.txt', 'a') as f:
            f.write(f'\\nError processing file: {os.path.basename(filename)}\\n')
            f.write(f'Error message: {str(e)}\\n')
            f.write('----------------------------------------\\n')

# Write summary of all unique missing and extra labels
with open('output.txt', 'a') as f:
    f.write('\\n\\nSUMMARY OF ALL FILES\\n')
    f.write('====================\\n')
    if all_missing_labels:
        f.write(f'All unique missing labels: {sorted(all_missing_labels)}\\n')
    else:
        f.write('No missing labels in any file\\n')
    
    if all_extra_labels:
        f.write(f'All unique extra labels: {sorted(all_extra_labels)}\\n')
    else:
        f.write('No extra labels in any file\\n')
"

echo "Analysis complete. Results saved to output.txt"
