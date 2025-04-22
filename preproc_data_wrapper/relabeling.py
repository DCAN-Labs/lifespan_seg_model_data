#!/usr/bin/env python3

import nibabel as nib
import numpy as np
import argparse
import random
from pathlib import Path
import tempfile
import statistics

def correct_corpus_callosum(fdata):
    shape = fdata.shape
    y_z_to_min_max_x = dict()
    x_len = shape[0]
    y_len = shape[1]
    z_len = shape[2]
    # old labels: CC_Posterior, CC_Mid_Posterior, CC_Central, CC_Mid_Anterior, CC_Anterior
    corpus_callosum_labels = [251,252,253,254,255]
    for x in range(x_len):
        for y in range(y_len):
            for z in range(z_len):
                label = int(fdata[x][y][z])
                if label in corpus_callosum_labels:
                    if (y, z) not in y_z_to_min_max_x:
                        y_z_to_min_max_x[(y, z)] = [x, x]
                    else:
                        new_min_max = y_z_to_min_max_x[(y, z)]
                        if x < new_min_max[0]:
                            new_min_max[0] = x
                        if x > new_min_max[1]:
                            new_min_max[1] = x
                        y_z_to_min_max_x[(y, z)] = new_min_max
    mean_x = np.zeros((y_len, z_len))
    for y in range(y_len):
        for z in range(z_len):
            if (y, z) in y_z_to_min_max_x:
                mean_x[y][z] = statistics.mean([y_z_to_min_max_x[(y, z)][0], y_z_to_min_max_x[(y, z)][1]])
    left_cerebral_white_matter_label = 2
    right_cerebral_white_matter_label = 41
    for x in range(x_len):
        for y in range(y_len):
            for z in range(z_len):
                label = int(fdata[x][y][z])
                if label in corpus_callosum_labels:
                    m = int(mean_x[y][z])
                    if x == m:
                        # Flip a coin
                        new_label = left_cerebral_white_matter_label if random.randint(0, 1) % 2 == 0 else right_cerebral_white_matter_label
                    elif x >= m:
                        new_label = left_cerebral_white_matter_label
                    else:
                        new_label = right_cerebral_white_matter_label
                    fdata[x][y][z] = new_label
                    print(f"Remapping label {label} to {new_label} (Assigned all CC labels to L/R WM)")
    return fdata

def relabel_segmentation(input_file, output_file):
    # Define the valid labels based on your list
    valid_labels = {
        0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 24, 26, 28, 30,
        31, 41, 42, 43, 44, 46, 47, 49, 50, 51, 52, 53, 54, 58, 60, 62, 63, 77, 80, 85, 172
    }
    
    print(f"Reading segmentation file: {input_file}")
    img = nib.load(input_file)
    data = img.get_fdata()
    
    # Make a copy of the data for modification
    new_data = data.copy()

    # First correct corpus callosum
    new_data = correct_corpus_callosum(new_data)
    
    # Get unique labels
    unique_labels = np.unique(new_data).astype(int)
    print(f"Found {len(unique_labels)} unique labels")
    
    # Identify labels not in our valid list
    invalid_labels = [label for label in unique_labels if label not in valid_labels]
    print(f"Found {len(invalid_labels)} labels to remap")
    
    # Process each invalid label
    for label in invalid_labels:
        print(f"Processing label: {label}")
        # Determine new label based on range
        if label >= 1000 and label < 2000:
            new_label = 3  # Left cortex
            print(f"Remapping label {label} → {new_label} (Left cortex)")
        elif label >= 2000:
            new_label = 42  # Right cortex
            print(f"Remapping label {label} → {new_label} (Right cortex)")
        elif label in {251,252,253,254,255}:
            # CC_Posterior, CC_Mid_Posterior, CC_Central, CC_Mid_Anterior, CC_Anterior
            assert False, 'Should have been handled by correct_corpus_callosum.'
        elif label == 72:
            new_label = 0
            print(f"Remapping label {label} → {new_label} (Unused label)")
        elif label == 29:
            new_label = 0
            print(f"Remapping label {label} → {new_label} (Unused label)")
        else:
            # For other unlisted subcortical labels, we could either:
            # 1. Keep them as is
            # 2. Map to nearest structure
            # For now, we'll keep them and just report
            print(f"Leaving unlisted subcortical label {label} as is")
            continue
        
        # Apply the new label
        new_data[data == label] = new_label
        
    new_data = new_data.astype(np.int16)  # Ensure the data type is consistent with the original
    
    # Save the result
    print(f"Saving relabeled segmentation to: {output_file}")
    new_img = nib.Nifti1Image(new_data, img.affine, img.header) if input_file.endswith('.nii.gz') else nib.MGHImage(new_data, img.affine, img.header)
    nib.save(new_img, output_file)
    
    return len(invalid_labels)

def main():
    parser = argparse.ArgumentParser(description='Relabel segmentation files to a standardized format')
    parser.add_argument('input', help='Input segmentation file (.mgz or .nii.gz)')
    parser.add_argument('--output', help='Output filename (default: adds "_relabeled" to input filename)')
    
    args = parser.parse_args()
    
    # Handle output filename
    if args.output:
        output_file = args.output
    else:
        input_path = Path(args.input)
        output_file = str(input_path.with_name(f"{input_path.stem}_relabeled{input_path.suffix}"))
    
    # Run the relabeling
    num_relabeled = relabel_segmentation(args.input, output_file)
    print(f"Relabeling complete. Modified {num_relabeled} label types.")

if __name__ == "__main__":
    main()