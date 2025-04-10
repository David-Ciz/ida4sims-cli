import os

def check_if_dataset_contains_file(
    dataset_content_list: list,
    expected_dataset_filepath: str,
    local_file_path: str
):
  
    print(f"Checking cache for iRODS path: '{expected_dataset_filepath}' (Local: '{local_file_path}')")

    if not os.path.exists(local_file_path):
        print(f"  Local file '{local_file_path}' not found for size check!")
        return False

    local_file_size = os.path.getsize(local_file_path)

    if dataset_content_list is None:
        print("  Dataset content list was not retrieved or is empty. Cannot confirm existence.")
        return False

    if not dataset_content_list:
         print("  Dataset content list is empty. File does not exist.")
         return False

    for item in dataset_content_list:
        item_path = item.get('name')
        item_type = item.get('type')
        item_size = item.get('size', -1)
        if item_type == 'file' and item_path == expected_dataset_filepath:
            if item_size >= 0 and item_size == local_file_size:
                print(f"  MATCH: File '{expected_dataset_filepath}' found in dataset cache with matching size ({item_size} bytes).")
                return True
            elif item_size >= 0:
                 print(f"  MISMATCH: File '{expected_dataset_filepath}' found in dataset cache BUT sizes differ. Local: {local_file_size}, Remote: {item_size}.")
                 return False
            else:
                 print(f"  WARNING: File '{expected_dataset_filepath}' found in dataset cache BUT remote size is unknown ({item_size}). Cannot confirm match.")
                 return False

    print(f"  NOT FOUND: File '{expected_dataset_filepath}' not found in dataset cache.")
    return False
