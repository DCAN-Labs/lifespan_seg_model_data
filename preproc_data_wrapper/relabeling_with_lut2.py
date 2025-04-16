#!/usr/bin/env python3

import nibabel as nib
import numpy as np
import os
import sys
import argparse
import subprocess
import shutil
from pathlib import Path

def relabel_segmentation(input_file, output_file):
    # Define the valid labels based on your list with RGB values
    valid_labels_with_rgb = {
        0:   (0, 0, 0),        # Unknown
        1:   (70, 130, 180),   # Left-Cerebral-Exterior
        2:   (245, 245, 245),  # Left-Cerebral-White-Matter
        3:   (205, 62, 78),    # Left-Cerebral-Cortex
        4:   (120, 18, 134),   # Left-Lateral-Ventricle
        5:   (196, 58, 250),   # Left-Inf-Lat-Vent
        6:   (0, 148, 0),      # Left-Cerebellum-Exterior
        7:   (220, 248, 164),  # Left-Cerebellum-White-Matter
        8:   (230, 148, 34),   # Left-Cerebellum-Cortex
        10:  (0, 118, 14),     # Left-Thalamus-Proper
        11:  (122, 186, 220),  # Left-Caudate
        12:  (236, 13, 176),   # Left-Putamen
        13:  (12, 48, 255),    # Left-Pallidum
        14:  (204, 182, 142),  # 3rd-Ventricle
        15:  (42, 204, 164),   # 4th-Ventricle
        16:  (119, 159, 176),  # Brain-Stem
        17:  (220, 216, 20),   # Left-Hippocampus
        18:  (103, 255, 255),  # Left-Amygdala
        24:  (60, 60, 60),     # CSF
        26:  (255, 165, 0),    # Left-Accumbens-area
        28:  (165, 42, 42),    # Left-VentralDC
        30:  (160, 32, 240),   # Left-vessel
        31:  (0, 200, 200),    # Left-choroid-plexus
        41:  (0, 225, 0),      # Right-Cerebral-White-Matter
        42:  (205, 62, 78),    # Right-Cerebral-Cortex
        43:  (120, 18, 134),   # Right-Lateral-Ventricle
        44:  (196, 58, 250),   # Right-Inf-Lat-Vent
        46:  (220, 248, 164),  # Right-Cerebellum-White-Matter
        47:  (230, 148, 34),   # Right-Cerebellum-Cortex
        49:  (0, 118, 14),     # Right-Thalamus-Proper
        50:  (122, 186, 220),  # Right-Caudate
        51:  (236, 13, 176),   # Right-Putamen
        52:  (13, 48, 255),    # Right-Pallidum
        53:  (220, 216, 20),   # Right-Hippocampus
        54:  (103, 255, 255),  # Right-Amygdala
        58:  (255, 165, 0),    # Right-Accumbens-area
        60:  (165, 42, 42),    # Right-VentralDC
        62:  (160, 32, 240),   # Right-vessel
        63:  (0, 200, 221),    # Right-choroid-plexus
        77:  (200, 70, 255),   # WM-hypointensities
        85:  (234, 169, 30),   # Optic-Chiasm
        172: (119, 100, 176),  # Vermis
    }
    
    # Create custom color LUT
    lut_file = create_color_lut(valid_labels_with_rgb, "custom_segmentation_lut.txt")
    
    valid_labels = set(valid_labels_with_rgb.keys())
    
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
        else:
            # For other unlisted subcortical labels, we could either:
            # 1. Keep them as is
            # 2. Map to nearest structure
            # For now, we'll keep them and just report
            print(f"Leaving unlisted subcortical label {label} as is")
            continue
        
        # Apply the new label
        new_data[data == label] = new_label
    
    # Convert to integer data type before saving
    new_data = new_data.astype(np.int16)
    
    # Save the intermediate result
    temp_output = f"temp_{os.path.basename(output_file)}"
    print(f"Saving relabeled segmentation to: {temp_output}")
    if input_file.endswith('.nii.gz'):
        new_img = nib.Nifti1Image(new_data, img.affine, img.header)
        new_img.set_data_dtype(np.int16)
    else:  # .mgz file
        new_img = nib.MGHImage(new_data, img.affine, img.header)
        new_img.set_data_dtype(np.int16)
    
    nib.save(new_img, temp_output)
    
    # Apply color LUT using FreeSurfer's mris_info_to_lut command or similar tool
    # Note: This step might need to be adjusted based on available FreeSurfer tools
    try:
        # Try to apply the LUT using FreeSurfer tools
        if shutil.which("mri_vol2vol"):
            cmd = f"mri_vol2vol --lut {lut_file} {temp_output} {output_file}"
            print(f"Applying color LUT: {cmd}")
            subprocess.run(cmd, shell=True, check=True)
            print(f"Successfully applied color LUT to create {output_file}")
        else:
            print("FreeSurfer's mri_convert not found. Copying temp file to output.")
            shutil.copy(temp_output, output_file)
    except Exception as e:
        print(f"Warning: Could not apply color LUT: {e}")
        print(f"Using intermediate file as final output: {temp_output} -> {output_file}")
        shutil.copy(temp_output, output_file)
    
    # Clean up
    if os.path.exists(temp_output):
        os.remove(temp_output)
    
    return len(invalid_labels), lut_file

def create_color_lut(labels_with_rgb, output_file):
    """Create a FreeSurfer color lookup table file."""
    with open(output_file, 'w') as f:
        f.write("# FreeSurfer color lookup table for segmentation\n")
        f.write("# Label Name R G B A\n")
        
        # Add background
        #f.write("0 Background 0 0 0 0\n")
        
        # Add all other labels
        for label, rgb in labels_with_rgb.items():
            r, g, b = rgb
            name = get_label_name(label)
            f.write(f"{label} {name} {r} {g} {b} 0\n")
    
    print(f"Created color lookup table: {output_file}")
    return output_file

def get_label_name(label):
    """Get the name for a given label."""
    names = {
        0:   "Unknown",
        1:   "Left-Cerebral-Exterior",
        2:   "Left-Cerebral-White-Matter",
        3:   "Left-Cerebral-Cortex",
        4:   "Left-Lateral-Ventricle",
        5:   "Left-Inf-Lat-Vent",
        6:   "Left-Cerebellum-Exterior",
        7:   "Left-Cerebellum-White-Matter",
        8:   "Left-Cerebellum-Cortex",
        10:  "Left-Thalamus-Proper",
        11:  "Left-Caudate",
        12:  "Left-Putamen",
        13:  "Left-Pallidum",
        14:  "3rd-Ventricle",
        15:  "4th-Ventricle",
        16:  "Brain-Stem",
        17:  "Left-Hippocampus",
        18:  "Left-Amygdala",
        24:  "CSF",
        26:  "Left-Accumbens-area",
        28:  "Left-VentralDC",
        30:  "Left-vessel",
        31:  "Left-choroid-plexus",
        41:  "Right-Cerebral-White-Matter",
        42:  "Right-Cerebral-Cortex",
        43:  "Right-Lateral-Ventricle",
        44:  "Right-Inf-Lat-Vent",
        46:  "Right-Cerebellum-White-Matter",
        47:  "Right-Cerebellum-Cortex",
        49:  "Right-Thalamus-Proper",
        50:  "Right-Caudate",
        51:  "Right-Putamen",
        52:  "Right-Pallidum",
        53:  "Right-Hippocampus",
        54:  "Right-Amygdala",
        58:  "Right-Accumbens-area",
        60:  "Right-VentralDC",
        62:  "Right-vessel",
        63:  "Right-choroid-plexus",
        77:  "WM-hypointensities",
        85:  "Optic-Chiasm",
        172: "Vermis",
    }
    return names.get(label, f"Unknown-{label}")

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
    num_relabeled, lut_file = relabel_segmentation(args.input, output_file)
    print(f"Relabeling complete. Modified {num_relabeled} label types.")
    print(f"Custom color LUT created: {lut_file}")
    print(f"To visualize with correct colors in FreeSurfer, use: ")
    print(f"  freeview {output_file}:colormap=lut:{lut_file}")

if __name__ == "__main__":
    main()