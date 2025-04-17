#!/usr/bin/env python3

import nibabel as nib
import numpy as np
import os
import sys
import argparse
import random
from pathlib import Path

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
    
    # Get unique labels
    unique_labels = np.unique(data).astype(int)
    print(f"Found {len(unique_labels)} unique labels")
    
    # Identify labels not in our valid list
    invalid_labels = [label for label in unique_labels if label not in valid_labels]
    print(f"Found {len(invalid_labels)} labels to remap")
    
    random_int = random.randint(3, 4)
    print(f"Random integer for CC labels: {random_int}")
    
    # Process each invalid label
    for label in invalid_labels:
        if label == 0:  # Skip background
            continue
        
        # Determine new label based on range
        if label >= 1000 and label < 2000:
            new_label = 3  # Left cortex
            print(f"Remapping label {label} → {new_label} (Left cortex)")
        elif label >= 2000:
            new_label = 42  # Right cortex
            print(f"Remapping label {label} → {new_label} (Right cortex)")
        elif label in {251,252,253,254,255}:
            # set a random seed, if that seed is even then use 2, otherwise use 41
            new_label = 2 if random_int % 2 == 0 else 41
            print(f"Remapping label {label} → {new_label} (Randomly assigned all CC labels to L/R WM)")
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