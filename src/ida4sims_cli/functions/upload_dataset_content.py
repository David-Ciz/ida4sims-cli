import os
import time
from py4lexis.lexis_irods import iRODS
from py4lexis.ddi.datasets import Datasets
from ida4sims_cli.functions.sync_directory_contents import sync_directory_contents
from ida4sims_cli.functions.list_directory_contents import list_directory_contents
from ida4sims_cli.functions.check_if_dataset_contains_file import check_if_dataset_contains_file
from ida4sims_cli.functions.check_if_dataset_contains_directory import check_if_dataset_contains_directory

def upload_dataset_content(irods: iRODS, datasets: Datasets, local_path: str, dataset_id: str) -> None:
    
    print(f"Processing local path: '{local_path}' for dataset '{dataset_id}'")

    if not os.path.exists(local_path):
        print(f"ERROR: Local path not found: '{local_path}'")
        raise FileNotFoundError(f"Local path not found: {local_path}")

    print(f"Fetching current content list for dataset '{dataset_id}' to check for existing items...")
    dataset_content_list = None

    # Retry logic to wait for dataset creation propagation
    max_retries = 24
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            filelist_response = datasets.get_content_of_dataset(dataset_id=dataset_id)

            if filelist_response is None:
                # py4lexis returns None and prints error if dataset doesn't exist yet
                print(f"  Dataset content retrieval returned None (attempt {attempt + 1}/{max_retries}). Waiting {retry_delay}s...")
                time.sleep(retry_delay)
                continue

            if 'contents' in filelist_response:
                 dataset_content_list = filelist_response.get('contents')
                 if dataset_content_list:
                      print(f"  Found {len(dataset_content_list)} items in dataset root cache.")
                 else:
                      print("  Dataset root cache is empty.")
                 break
            else:
                print("  Dataset is currently empty or content could not be retrieved.")
                dataset_content_list = []
                break
        except Exception as e:
            print(f"WARNING: Could not fetch dataset contents: {e}. Retrying (attempt {attempt + 1}/{max_retries})...")
            time.sleep(retry_delay)

    if dataset_content_list is None:
        print("WARNING: Could not fetch dataset contents after retries. Proceeding without existence checks.")
        dataset_content_list = []

    should_skip = False
    target_name = os.path.basename(local_path)

    if not target_name and os.path.isdir(local_path):
        target_name = "uploaded_directory"

    if os.path.isfile(local_path):
        print(f"Path is a file. Target name: '{target_name}'. Checking existence and size...")
        if check_if_dataset_contains_file(dataset_content_list, target_name, local_path):
            should_skip = True

    elif os.path.isdir(local_path):
        print(f"Path is a directory. Target name: '{target_name}'. Checking existence and size...")
        print(f"...................check_if_dataset_contains_directory: {check_if_dataset_contains_directory(dataset_content_list, target_name, local_path)}")
        if check_if_dataset_contains_directory(dataset_content_list, target_name, local_path):
            should_skip = True
            local_dir_content = list_directory_contents(local_path)   
            print("---------------------------------------sync_directory_contents-----------------------------------: ")
            sync_directory_contents(irods, dataset_content_list, local_dir_content, dataset_id, local_path)        
        
    if not should_skip:
        if os.path.isfile(local_path):
            print(f"Attempting to upload file '{local_path}' as '{target_name}'...")
            try:
                irods.put_data_object_to_dataset(
                    local_filepath=local_path,
                    dataset_filepath=target_name,
                    dataset_id=dataset_id,
                )
                print(f"SUCCESS: File '{target_name}' uploaded.")
            except Exception as e:
                print(f"ERROR: Failed to upload file '{local_path}': {e}")
                raise e
        elif os.path.isdir(local_path):
            print(f"Attempting to upload directory '{local_path}'...")
            try:
                irods.upload_directory_to_dataset(
                    local_directorypath=local_path,
                    dataset_id=dataset_id,
                )
                print(f"SUCCESS: Directory uploaded.")
            except Exception as e:
                print(f"ERROR: Failed to upload directory '{local_path}': {e}")
                raise e
        else:
             print(f"ERROR: Local path '{local_path}' is not a valid file or directory for upload.")
             raise ValueError(f"Local path '{local_path}' is not a file or directory.")

def upload_dataset_as_files(irods: iRODS, local_path: str, dataset_id: str, dataset_type: str, metadata: dict) -> None:
    """
    Uploads individual files from metadata to the dataset as separate data objects.
    The metadata contains only the file names, not full paths.
    Files that are None or do not exist in local_path are skipped.
    """
    if dataset_type == "simulation":
        # This function should not be used for simulation datasets
        print("upload_dataset_as_files is not intended for dataset_type=simulation")
        return
    
    elif dataset_type=="force_field":
        file_keys = [
            'dat_file',
            'library_files',
            'leaprc_file',
            'frcmod_files',
            'fixcommand_file'
        ]

    elif dataset_type=="experimental_data":
        file_keys = [
            '3j_coupling_files',
            'noe_files'
        ]
    else:
        print(f"ERROR: Unsupported dataset type '{dataset_type}' for file upload.")
        return
    
    for key in file_keys:
        filename = metadata.get(key)
        if filename is None:
            # No file specified for this key, skip to next
            print(f"File '{key}' not specified, skipping.")
            continue
        # If the value is a list or tuple (e.g., multiple frcmod files)
        if isinstance(filename, (list, tuple)):
            for fname in filename:
                if fname is None:
                    # Skip if the list contains None
                    continue
                file_path = os.path.join(local_path, fname)
                if not os.path.isfile(file_path):
                    # File does not exist at the constructed path, skip
                    print(f"File '{file_path}' does not exist, skipping.")
                    continue
                target_name = os.path.basename(file_path)
                print(f"Uploading file '{file_path}' as '{target_name}' to dataset '{dataset_id}'...")
                try:
                    irods.put_data_object_to_dataset(
                        local_filepath=file_path,
                        dataset_filepath="./",
                        dataset_id=dataset_id,
                    )
                    print(f"SUCCESS: File '{target_name}' uploaded.")
                except Exception as e:
                    print(f"ERROR: Failed to upload file '{file_path}': {e}")
                    raise e
        else:
            # Single file case
            file_path = os.path.join(local_path, filename)
            if not os.path.isfile(file_path):
                # File does not exist at the constructed path, skip
                print(f"File '{file_path}' does not exist, skipping.")
                continue
            target_name = os.path.basename(file_path)
            print(f"Uploading file '{file_path}' as '{target_name}' to dataset '{dataset_id}'...")
            try:
                irods.put_data_object_to_dataset(
                    local_filepath=file_path,
                    dataset_filepath="./",
                    dataset_id=dataset_id,
                )
                print(f"SUCCESS: File '{target_name}' uploaded.")
            except Exception as e:
                print(f"ERROR: Failed to upload file '{file_path}': {e}")
                raise e
