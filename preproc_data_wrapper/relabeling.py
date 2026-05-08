#!/usr/bin/env python3

import nibabel as nib
import numpy as np
import argparse
from pathlib import Path


def remap_indices_by_hemisphere(fdata, label_indices, affine, left_label, right_label, midline_tol_mm=0.5):
    # Fast exit when the source label is absent.
    if label_indices[0].size == 0:
        return fdata

    # Build homogeneous voxel coordinates [i, j, k, 1] for all voxels to remap.
    ijk = np.vstack(
        (
            label_indices[0],
            label_indices[1],
            label_indices[2],
            np.ones(label_indices[0].shape[0], dtype=np.float64),
        )
    )
    # Convert to world-space x (RAS+) using the affine first row.
    # In RAS space: x < 0 is anatomical left, x > 0 is anatomical right.
    world_x = affine[0, :] @ ijk

    # Treat a small band around x=0 as midline to avoid unstable flips from tiny
    # interpolation/rounding differences at the interhemispheric boundary.
    left_mask = world_x < -midline_tol_mm
    right_mask = world_x > midline_tol_mm
    midline_mask = ~(left_mask | right_mask)

    fdata[
        label_indices[0][left_mask],
        label_indices[1][left_mask],
        label_indices[2][left_mask],
    ] = left_label
    fdata[
        label_indices[0][right_mask],
        label_indices[1][right_mask],
        label_indices[2][right_mask],
    ] = right_label

    if np.any(midline_mask):
        # Deterministic fallback for true midline voxels:
        # 1) identify which voxel axis best maps to world-space left-right,
        # 2) split by that axis relative to the volume center.
        lr_axis = int(np.argmax(np.abs(affine[0, :3])))
        lr_axis_sign = np.sign(affine[0, lr_axis])
        if lr_axis_sign == 0:
            lr_axis_sign = 1.0

        lr_vox = label_indices[lr_axis][midline_mask]
        center = (fdata.shape[lr_axis] - 1) / 2.0
        # Positive sign means larger voxel index is more right in world space.
        # Negative sign means larger voxel index is more left.
        if lr_axis_sign > 0:
            is_right = lr_vox >= center
        else:
            is_right = lr_vox <= center

        mid_i = label_indices[0][midline_mask]
        mid_j = label_indices[1][midline_mask]
        mid_k = label_indices[2][midline_mask]
        fdata[mid_i[~is_right], mid_j[~is_right], mid_k[~is_right]] = left_label
        fdata[mid_i[is_right], mid_j[is_right], mid_k[is_right]] = right_label

    return fdata

def correct_corpus_callosum(fdata, affine):
    # Identify CC voxels in a single pass
    cc_mask = np.isin(fdata, [251, 252, 253, 254, 255])
    cc_indices = np.where(cc_mask)

    return remap_indices_by_hemisphere(fdata, cc_indices, affine, 2, 41)

# WM-hypointensities (77) and non-WM-hypointensities (80) need to be remapped based on whatever side of the brain it is on, similar to corpus callosum function above. We are running this function on fragileX dataset. 
def correct_wm_intensities_no_lesion(fdata, affine):
    # Identify WM intensity voxels in a single pass
    wm_mask = np.isin(fdata, [77, 80])
    wm_indices = np.where(wm_mask)

    return remap_indices_by_hemisphere(fdata, wm_indices, affine, 2, 41)

# We run this function on the NS and ADNI datases. If it is a WM-hypointensity label, it will be remapped as a lesion label (25 for left lesion and 57 for right lesion) instead of a white matter label (2 or 41), as is still done for the non-WM-hypointensity label. This is because WM-hypointensities are more likely to represent lesions in this dataset, while non-WM-hypointensities are more likely to represent normal white matter. This is a heuristic approach and may not be perfect, but it should help to improve the accuracy of the segmentation with lesion data in the future. It is important to validate this approach on a case-by-case basis and adjust as necessary based on the specific characteristics of the data being processed. Argument can be made to only run this on NS and run above on ADNI. 
def correct_wm_intensities_with_lesion(fdata, affine):
    # Identify WM intensity voxels in a single pass
    wm_hypo_mask = np.isin(fdata, 77)
    wm_nh_mask = np.isin(fdata, 80)
    wm_hypo_indices = np.where(wm_hypo_mask)
    wm_nh_indices = np.where(wm_nh_mask)

    remap_indices_by_hemisphere(fdata, wm_hypo_indices, affine, 25, 57)
    remap_indices_by_hemisphere(fdata, wm_nh_indices, affine, 2, 41)

    return fdata


def correct_wm_intensities(fdata, affine, use_lesion_labels=False):
    if use_lesion_labels:
        return correct_wm_intensities_with_lesion(fdata, affine)
    return correct_wm_intensities_no_lesion(fdata, affine)

def relabel_segmentation(input_file, output_file, use_lesion_labels=False):
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
    new_data = correct_corpus_callosum(new_data, img.affine)
    # Then correct WM intensities
    new_data = correct_wm_intensities(new_data, img.affine, use_lesion_labels=use_lesion_labels)

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
    parser.add_argument(
        '--use-lesion-labels',
        action='store_true',
        help='Map WM-hypointensity label 77 to lesion labels 25/57 instead of WM labels 2/41. Use this for datasets such as NS where 77 is treated as lesion-like.',
    )
    
    args = parser.parse_args()
    
    # Handle output filename
    if args.output:
        output_file = args.output
    else:
        input_path = Path(args.input)
        output_file = str(input_path.with_name(f"{input_path.stem}_relabeled{input_path.suffix}"))
    
    # Run the relabeling
    num_relabeled = relabel_segmentation(args.input, output_file, use_lesion_labels=args.use_lesion_labels)
    print(f"Relabeling complete. Modified {num_relabeled} label types.")

if __name__ == "__main__":
    main()