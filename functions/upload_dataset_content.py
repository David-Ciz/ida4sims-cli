import os
from py4lexis.lexis_irods import iRODS
from py4lexis.ddi.datasets import Datasets
from functions.sync_directory_contents import sync_directory_contents
from functions.list_directory_contents import list_directory_contents
from helpers.default_data import DEFAULT_ACCESS, PROJECT
from functions.check_if_dataset_contains_file import check_if_dataset_contains_file
from functions.check_if_dataset_contains_directory import check_if_dataset_contains_directory

def upload_dataset_content(irods: iRODS, datasets: Datasets, local_path: str, dataset_id: str):
    
    print(f"Processing local path: '{local_path}' for dataset '{dataset_id}'")

    if not os.path.exists(local_path):
        print(f"ERROR: Local path not found: '{local_path}'")
        raise FileNotFoundError(f"Local path not found: {local_path}")

    print(f"Fetching current content list for dataset '{dataset_id}' to check for existing items...")
    dataset_content_list = None
    try:
        filelist_response = datasets.get_content_of_dataset(dataset_id=dataset_id)
        if filelist_response and 'contents' in filelist_response:
             dataset_content_list = filelist_response.get('contents')
             if dataset_content_list:
                  print(f"  Found {len(dataset_content_list)} items in dataset root cache.")
             else:
                  print("  Dataset root cache is empty.")
        else:
            print("  Dataset is currently empty or content could not be retrieved.")
            dataset_content_list = []
    except Exception as e:
        print(f"WARNING: Could not fetch dataset contents: {e}. Proceeding without existence checks.")
        dataset_content_list = None

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
                    access=DEFAULT_ACCESS, project=PROJECT,
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
                    access=DEFAULT_ACCESS, project=PROJECT, 
                    dataset_id=dataset_id,
                )
                print(f"SUCCESS: Directory uploaded.")
            except Exception as e:
                print(f"ERROR: Failed to upload directory '{local_path}': {e}")
                raise e
        else:
             print(f"ERROR: Local path '{local_path}' is not a valid file or directory for upload.")
             raise ValueError(f"Local path '{local_path}' is not a file or directory.")
