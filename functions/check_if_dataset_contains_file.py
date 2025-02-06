from py4lexis.ddi.datasets import Datasets
import os

def check_if_dataset_contains_file(datasets: Datasets, dataset_id: str, local_file_path: str):
    base_local_path = os.getcwd()
    print(f"Checking if file '{local_file_path}' exists in dataset '{dataset_id}'...")
    print(f"Base local path: {base_local_path}")

    try:
        file_name = os.path.basename(local_file_path)
        print(f"Filename: {file_name}")
        file_path = file_name 
        print(f"Expected iRODS file path: {file_path}")

        local_file_size = os.path.getsize(local_file_path) if os.path.exists(local_file_path) else -1 
        if local_file_size == -1:
          print(f"Local file '{local_file_path}' not found!")
          return False

        filelist = datasets.get_content_of_dataset(dataset_id=dataset_id)

        print(f"Contents of dataset {dataset_id}:")
        if filelist and 'contents' in filelist:
            for item in filelist['contents']:
                item_path = item['name']
                item_size = item.get('size', -1)

                print(f"  - {item_path} ({item['type']}), Size: {item_size}")

                if item['type'] == 'file' and item_path == file_path:
                    if item_size == local_file_size:
                        print(f"File '{file_path}' exists in dataset '{dataset_id}' with matching size ({item_size} bytes).")
                        return True
                    else:
                        print(f"File '{file_path}' exists in dataset '{dataset_id}' but sizes differ. Local: {local_file_size} bytes, Remote: {item_size} bytes.")
                        return False
        else:
            print("  - Dataset is empty or 'contents' key is missing.")

        print(f"File '{file_path}' does not exist in dataset '{dataset_id}'.")
        return False

    except Exception as e:
        print(f"Error checking dataset contents: {e}")
        return False