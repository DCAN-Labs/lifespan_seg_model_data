import tempfile
import nibabel as nib

from relabeling import relabel_segmentation


def relabel_segmentation_test():
    input_file = '/scratch.global/lundq163/lifespan-seg-model-data/raw/labels_ADNI_renamed/660mo_ds-ADNI_sub-053S0507_ses-20060515093647.mgz'
    output_file = 'relabeled.nii.gz'
    invalid_label_count = relabel_segmentation(input_file, output_file)
    print(invalid_label_count)

if __name__ == "__main__":
    relabel_segmentation_test()
