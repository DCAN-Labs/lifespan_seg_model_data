#!/usr/bin/env python3

import nibabel as nib
import numpy as np
import argparse
import random
from pathlib import Path

def correct_corpus_callosum(fdata):
    # Identify CC voxels in a single pass
    cc_mask = np.isin(fdata, [251, 252, 253, 254, 255])
    cc_indices = np.where(cc_mask)
    
    # Calculate means more efficiently
    y_z_pairs = set(zip(cc_indices[1], cc_indices[2]))
    y_z_to_mean_x = {}
    
    for y, z in y_z_pairs:
        x_values = cc_indices[0][np.logical_and(cc_indices[1] == y, cc_indices[2] == z)]
        y_z_to_mean_x[(y, z)] = np.mean(x_values)
    
    # Apply the new labels
    for x, y, z in zip(*cc_indices):
        m = int(y_z_to_mean_x[(y, z)])
        if x == m:
            new_label = 2 if random.randint(0, 1) == 0 else 41
        elif x >= m:
            new_label = 2  # Left cerebral white matter
        else:
            new_label = 41  # Right cerebral white matter
        fdata[x, y, z] = new_label
    
    return fdata

# WM-hypointensities (77) and non-WM-hypointensities (80) need to be remapped based on whatever side of the brain it is on, similar to corpus callosum function above
# However, if it is from the NS dataset, it may need to be remapped as a lesion (need to take a look at the data though and see first)
def correct_wm_intensities(fdata):
    # Identify WM intensity voxels in a single pass
    wm_mask = np.isin(fdata, [77, 80])
    wm_indices = np.where(wm_mask)

    # Calculate means more efficiently
    y_z_pairs = set(zip(wm_indices[1], wm_indices[2]))
    y_z_to_mean_x = {}

    for y, z in y_z_pairs:
        x_values = wm_indices[0][np.logical_and(wm_indices[1] == y, wm_indices[2] == z)]
        y_z_to_mean_x[(y, z)] = np.mean(x_values)

    # Apply the new labels
    for x, y, z in zip(*wm_indices):
        m = int(y_z_to_mean_x[(y, z)])
        if x == m:
            new_label = 2 if random.randint(0, 1) == 0 else 41
        elif x >= m:
            new_label = 2  # Left cerebral white matter
        else:
            new_label = 41  # Right cerebral white matter
        fdata[x, y, z] = new_label

    return fdata

def relabel_segmentation(input_file, output_file):
    # Define the valid labels based on your list
    # valid_labels_extended = {
    #     0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 24, 26, 28, 30, 31,
    #     40, 41, 42, 43, 44, 46, 47, 49, 50, 51, 52, 53, 54, 58, 60, 62, 63, 77, 80, 85, 172
    # }
    valid_labels = {
        2, 3, 4, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 24, 26, 28, 41, 42, 43, 47, 49, 50, 51, 52, 53, 54, 58, 60, 172
    }

    print(f"Reading segmentation file: {input_file}")
    img = nib.load(input_file)
    data = img.get_fdata()
    
    # Make a copy of the data for modification
    new_data = data.copy()

    # First correct corpus callosum
    new_data = correct_corpus_callosum(new_data)
    # Then correct WM intensities
    new_data = correct_wm_intensities(new_data)

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
        elif label == 77 or label == 80:
            assert False, 'Should have been handled by correct_wm_intensities.'
        elif label == 72:  # 5th ventricle
            new_label = 0
            print(f"Remapping label (5th ventricle) {label} → {new_label} (Unused label)")
        elif label == 29: #  Left-undetermined
            new_label = 0
            print(f"Remapping label (Left-undetermined) {label} → {new_label} (Unused label)")
        elif label == 1:  # Left-Cerebral-Exterior
            new_label = 0
            print(f"Remapping label (Left-Cerebral-Exterior) {label} → {new_label} (Unused label)")
        elif label == 5:  # Left-Inf-Lat-Vent
            new_label = 4  # Left-Lateral-Ventricle
            print(f"Remapping label (Left-Inf-Lat-Vent) {label} → {new_label} (Left-Lateral-Ventricle)")
        elif label == 44:  # Right-Inf-Lat-Vent
            new_label = 43  # Right-Lateral-Ventricle
            print(f"Remapping label (Right-Inf-Lat-Vent) {label} → {new_label} (Right-Lateral-Ventricle)")
        elif label == 31:  # Left-choroid-plexus
            new_label = 4  # Left-Lateral-Ventricle
            print(f"Remapping label (Left-choroid-plexus) {label} → {new_label} (Left-Lateral-Ventricle)")
        elif label == 63:  # Right-choroid-plexus
            new_label = 43  # Right-Lateral-Ventricle
            print(f"Remapping label (Right-choroid-plexus) {label} → {new_label} (Right-Lateral-Ventricle)")
        elif label == 6 or label == 7:  # Left-Cerebellum-Exterior or Left-Cerebellum-White-Matter
            new_label = 8  # Left-Cerebellum-Cortex
            print(f"Remapping label (Left-Cerebellum-Exterior/Left-Cerebellum-White-Matter) {label} → {new_label} (Left-Cerebellum-Cortex)")
        elif label == 45 or label == 46:  # Right-Cerebellum-Exterior or Right-Cerebellum-White-Matter
            new_label = 47  # Right-Cerebellum-Cortex
            print(f"Remapping label (Right-Cerebellum-Exterior/Right-Cerebellum-White-Matter) {label} → {new_label} (Right-Cerebellum-Cortex)")
        elif label == 30 or label == 62:  # Left-vessel or Right-vessel
            new_label = 0  # Unused label
            print(f"Remapping label (Left-vessel/Right-vessel) {label} → {new_label} (Unused label)")
        elif label == 85:  # Optic-Chiasm
            new_label = 0  # Unused label
            print(f"Remapping label (Optic-Chiasm) {label} → {new_label} (Unused label)")
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