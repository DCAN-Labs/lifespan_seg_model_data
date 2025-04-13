# Python script to automate file renaming

import sys
import os
import csv
import shutil


def main():
    script_name = sys.argv[0]
    arguments = sys.argv[1:]

    if len(arguments) < 7:
        print("\nThis script requires 6 arguments. Too few provided!\n\nExpecting:")
        print("\tArg 1: path to project root directory where the subject folders are located\n")
        print("\tArg 2: relative path to the T1 and aseg files within each subject folder\n")
        print("\tArg 3: dataset name to use in the renamed files (e.g. fragileX, NS, etc.)\n")
        print("\tArg 4: absolute path to the 'participants.tsv' file to retrieve ages\n")
        print("\tArg 5: unique identifier string for the T1 file\n")
        print("\tArg 6: name of the aseg file to rename with extension\n")
        print("\tArg 7: absolute path to the output directory where renamed files will be saved\n")
        print(f"Usage: {script_name} <base_directory> <relative_path> <dataset_name> <participants_file> <t1_identifier> <aseg_identifier> <output_directory>")
        return

    base_directory = arguments[0]
    relative_path = arguments[1]
    if relative_path.startswith("/"):
        relative_path = relative_path[1:]
    if not relative_path.endswith("/"):
        relative_path += "/" 
    dataset_name = arguments[2]
    participants_file = arguments[3]
    t1_identifier = arguments[4]
    aseg_identifier = arguments[5]
    output_directory = arguments[6]

    # create new directory to store renamed files if it doesn't exist, within the parent directory of the project root
    t1_destination_directory_path = os.path.join(os.path.dirname(output_directory), f"images_{dataset_name}_renamed")
    aseg_destination_directory_path = os.path.join(os.path.dirname(output_directory), f"labels_{dataset_name}_renamed")
    
    if not os.path.exists(t1_destination_directory_path) or not os.path.exists(aseg_destination_directory_path):
        # Create the destination directory if it doesn't exist
        os.makedirs(t1_destination_directory_path)
        os.makedirs(aseg_destination_directory_path)
        print(f"Created directories: {t1_destination_directory_path} and {aseg_destination_directory_path}")
    else:
        print(f"Directories exist: {t1_destination_directory_path} and {aseg_destination_directory_path}")

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

    
    for sub_id in os.listdir(base_directory):
        file_dir = os.path.join(base_directory, sub_id, relative_path)
        if os.path.isdir(file_dir):
            # Get the age of the participant from the dictionary
            age = participant_ages.get(sub_id)
            if age is not None:
                # Convert age to months
                age_in_months = int(age) * 12

                # Rename T1.mgz and aseg.mgz files
                for file_name in os.listdir(file_dir):
                    file_extension = os.path.splitext(file_name)[1]  # Extract the file extension
                    
                    if t1_identifier in file_name:
                        new_file_name = f"{age_in_months}mo_ds-{dataset_name}_{sub_id}_0000{file_extension}"
                        source_path = os.path.join(file_dir, file_name)
                        destination_path = os.path.join(t1_destination_directory_path, new_file_name)
                        shutil.copyfile(source_path, destination_path)
                        print(f"Renamed {file_name} to {new_file_name} and copied to {destination_path}")
                    elif file_name == aseg_identifier:
                        new_file_name = f"{age_in_months}mo_ds-{dataset_name}_{sub_id}_{aseg_identifier}"
                        source_path = os.path.join(file_dir, file_name)
                        destination_path = os.path.join(aseg_destination_directory_path, new_file_name)
                        shutil.copyfile(source_path, destination_path)
                        print(f"Renamed {file_name} to {new_file_name} and copied to {destination_path}")
            else:
                print(f"Participant ID {sub_id} not found in the participants file.")
    print(f"File renaming completed. Script execution completed. T1s renamed and copied to {t1_destination_directory_path} and aseg files renamed and copied to {aseg_destination_directory_path}.")


def read_tsv(file_path, delimiter="\t"):
    """
    Reads a TSV file and returns its content as a list of lists.

    Args:
        file_path (str): The path to the TSV file.
        delimiter (str, optional): The delimiter used in the TSV file. Defaults to tab ('\t').

    Returns:
        list: A list of lists representing the TSV file content, where each inner list is a row of the file.
    """
    data = []
    with open(file_path, "r") as file:
        tsv_reader = csv.reader(file, delimiter=delimiter)
        for row in tsv_reader:
            data.append(row)
    return data


if __name__ == "__main__":
    main()