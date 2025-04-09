# Python script to automate file renaming

# First argument should be project root directory
#   (e.g. /scratch.global/lundq163/lifespan-seg-model-data/raw/fragileX)
#   (e.g. /scratch.global/lundq163/lifespan-seg-model-data/raw/NS)
#   etc...
# Second argument should be path to participants.tsv to get the ages

import sys
import os
import csv
import shutil


def main():
    script_name = sys.argv[0]
    arguments = sys.argv[1:]

    if len(arguments) < 2:
        print("\nThis script requires 2 arguments. Too few provided!\n\nExpecting:")
        print("\tArg 1: path to project root directory")
        print("\tArg 2: path to the 'participants.tsv' file to retrieve ages\n")
        return

    project_root_path = arguments[0]
    project_name = os.path.basename(project_root_path)

    # create new directory to store renamed files if it doesn't exist, within the parent directory of the project root
    destination_directory_path = os.path.join(
        os.path.dirname(project_root_path), f"labels_{project_name}_renamed"
    )
    if not os.path.exists(destination_directory_path):
        os.makedirs(destination_directory_path)
        print(f"Created directory: {destination_directory_path}")
    else:
        print(f"Directory exists: {destination_directory_path}")

    participants_file = arguments[1]

    # Check if the participants.tsv file exists
    if not os.path.isfile(participants_file):
        print(f"The file {participants_file} does not exist!")
        return

    # Get the age column and participant_id column from the participants.tsv file to calculate ages for each subject
    participants_df = read_tsv(participants_file)

    # Extract the header row to find the indices of "participant_id" and "age"
    header = participants_df[0]
    try:
        participant_id_index = header.index("participant_id")
        age_index = header.index("age")
    except ValueError as e:
        print(
            f"Error: {e}. Ensure 'participant_id' and 'age' columns exist in the TSV file."
        )
        return

    # Create a dictionary to store the ages of each participant
    participant_ages = {}
    for row in participants_df[1:]:
        participant_id = row[participant_id_index]
        age = row[age_index]
        participant_ages[participant_id] = age

    # Loop through the /project_root/derivatives/freesurfer directory and rename the files named T1.mgz and aseg.mgz to {sub_age_in_months}mo_ds-fragileX_sub-{sub_id}_0000.mgz and {sub_age_in_months}mo_ds-fragileX_sub-{sub_id}.mgz respectively
    # Store the renamed files in the new directory created above
    # Structure of the freesurfer directory is as follows: /project_root/derivatives/freesurfer/{sub_id}/mri/{T1.mgz, aseg.mgz}
    freesurfer_directory = os.path.join(project_root_path, "derivatives", "freesurfer")
    for sub_id in os.listdir(freesurfer_directory):
        sub_directory = os.path.join(freesurfer_directory, sub_id, "mri")
        if os.path.isdir(sub_directory):
            # Get the age of the participant from the dictionary
            age = participant_ages.get(sub_id)
            if age is not None:
                # Convert age to months
                age_in_months = int(age) * 12

                # Rename T1.mgz and aseg.mgz files
                for file_name in os.listdir(sub_directory):
                    file_extension = os.path.splitext(file_name)[
                        1
                    ]  # Extract the file extension
                    if file_name.startswith("T1"):
                        new_file_name = f"{age_in_months}mo_ds-fragileX_sub-{sub_id}_0000.{file_extension}"
                        source_path = os.path.join(sub_directory, file_name)

                        destination_path = os.path.join(
                            destination_directory_path, new_file_name
                        )
                        shutil.copyfile(source_path, destination_path)
                        print(f"Copied and renamed {file_name} to {destination_path}")
                    elif file_name.startswith("aseg"):
                        new_file_name = f"{age_in_months}mo_ds-fragileX_sub-{sub_id}.{file_extension}"
                        source_path = os.path.join(sub_directory, file_name)
                        destination_path = os.path.join(
                            destination_directory_path, new_file_name
                        )
                        shutil.copyfile(source_path, destination_path)
                        print(f"Copied and renamed {file_name} to {destination_path}")
            else:
                print(f"Participant ID {sub_id} not found in the participants file.")

    print("File renaming completed.")


def read_tsv(file_path, delimiter="\t"):
    """
    Reads a TSV file and returns its content as a list of lists.

    Args:
        file_path (str): The path to the TSV file.
        delimiter (str, optional): The delimiter used in the TSV file. Defaults to tab ('\t').

    Returns:
        list: A list of lists representing the TSV file content,
              where each inner list is a row of the file.
    """
    data = []
    with open(file_path, "r") as file:
        tsv_reader = csv.reader(file, delimiter=delimiter)
        for row in tsv_reader:
            data.append(row)
    return data


if __name__ == "__main__":
    main()
