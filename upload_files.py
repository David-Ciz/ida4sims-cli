from py4lexis.lexis_irods import iRODS
import os
from default_data import DEFAULT_ACCESS, PROJECT
from check_if_dataset_contains_file import check_if_dataset_contains_file
from py4lexis.ddi.datasets import Datasets

def upload_files_to_lexis(irods: iRODS, datasets: Datasets, directory, dataset_id):
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)

        # Skip directories, only handle files for now
        if os.path.isdir(item_path):
            print(f"Skipping directory: {item_path}")
            continue
        
        relative_path = os.path.relpath(item_path, directory)
        dataset_filepath = relative_path.replace("\\", "/")

        print(f"Checking if {item_path} exists in dataset {dataset_id}...")

        # Check if the file already exists in the dataset
        if check_if_dataset_contains_file(datasets, dataset_id, item_path):
            print(f"File {item_path} already exists in dataset {dataset_id}. Skipping upload.")
            continue  # Skip to the next file

        print(f"Uploading {item_path} to {dataset_filepath} in dataset {dataset_id}...")

        irods.put_data_object_to_dataset(
            local_filepath=item_path,
            dataset_filepath=dataset_filepath,
            access=DEFAULT_ACCESS,
            project=PROJECT,
            dataset_id=dataset_id
        )

        # Verify upload (optional, but good practice)
        if check_if_dataset_contains_file(datasets, dataset_id, item_path):
            print(f"Uploaded {item_path} successfully.")
        else:
            print(f"ERROR: Failed to upload {item_path}.")

    print("Finished checking/uploading files.")