#!/bin/bash

# this should work, just need to pull down the correct orig.mgz file for each NS subject on OpenNeuro first

antsRegistration \
  --dimensionality 3 \
  --output "[fs2native_,fs2native_Warped.nii.gz]" \
  --interpolation Linear \
  --winsorize-image-intensities "[0.005,0.995]" \
  --use-histogram-matching 0 \
  --initial-moving-transform "[./T1-only/images/336mo_ds-NS_sub-13_0000.nii.gz,./T1-only/orig.nii.gz,1]" \
  --transform Rigid["0.1"] \
  --metric MI["./T1-only/images/336mo_ds-NS_sub-13_0000.nii.gz","./T1-only/orig.nii.gz",1,32,Regular,0.25] \
  --convergence "[1000x500x250x100,1e-6,10]" \
  --shrink-factors 8x4x2x1 \
  --smoothing-sigmas 3x2x1x0vox \
  --transform Affine["0.1"] \
  --metric MI["./T1-only/images/336mo_ds-NS_sub-13_0000.nii.gz","./T1-only/orig.nii.gz",1,32,Regular,0.25] \
  --convergence "[1000x500x250x100,1e-6,10]" \
  --shrink-factors 8x4x2x1 \
  --smoothing-sigmas 3x2x1x0vox \
  --float 0 --verbose 1


antsApplyTransforms \
  -d 3 \
  -i ./T1-only/aparc_aseg_fsnative.nii.gz \
  -r ./T1-only/images/336mo_ds-NS_sub-13_0000.nii.gz \
  -o ./T1-only/labels/336mo_ds-NS_sub-13_fixed.nii.gz \
  -n NearestNeighbor \
  -t fs2native_0GenericAffine.mat