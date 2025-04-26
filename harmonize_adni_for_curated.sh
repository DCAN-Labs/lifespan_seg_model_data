#!/bin/bash

# Check if both directories are provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <images_directory> <labels_directory>"
    exit 1
fi

IMAGES_DIR="$1"
LABELS_DIR="$2"

echo "Checking files in $LABELS_DIR against matches in $IMAGES_DIR"
echo "Files to be deleted (labels without matching images):"

count_deleted=0
count_kept=0

# Process each label file in the labels directory
for label_file in "$LABELS_DIR"/*.nii.gz; do
    if [ -f "$label_file" ]; then
        # Extract the base name (everything before .nii.gz)
        basename=$(basename "$label_file" ".nii.gz")
        
        # Check if a matching image file exists in the images directory
        if [ -f "$IMAGES_DIR/${basename}_0000.nii.gz" ]; then
            echo "  Keeping: $(basename "$label_file") (match found: ${basename}_0000.nii.gz)"
            ((count_kept++))
        else
            echo "  Deleting: $(basename "$label_file") (no matching image found)"
            rm "$label_file"
            ((count_deleted++))
        fi
    fi
done

echo "Summary: $count_deleted files deleted, $count_kept files kept"