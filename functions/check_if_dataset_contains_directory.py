from functions.get_local_directory_size import get_local_directory_size

def check_if_dataset_contains_directory(
    dataset_content_list: list,
    expected_dataset_dirpath: str,
    local_dir_path: str
):
    print(f"Checking cache for iRODS directory path: '{expected_dataset_dirpath}' (Local: '{local_dir_path}')")

    local_dir_size = get_local_directory_size(local_dir_path)
    if local_dir_size == -1:
        print("  WARNING: Could not calculate local directory size. Cannot confirm match.")
        return False

    if dataset_content_list is None:
        print("  Dataset content list was not retrieved or is empty. Cannot confirm existence.")
        return False

    if not dataset_content_list:
         print("  Dataset content list is empty. Directory does not exist.")
         return False

    for item in dataset_content_list:
        item_name = item.get('name')
        item_type = item.get('type')

        if item_type == 'directory' and item_name == expected_dataset_dirpath:
            remote_dir_size = item.get('size', -1)

            print(f"  Found existing directory '{item_name}' in dataset cache.")
            print(f"  Comparing sizes: Local={local_dir_size}, Remote={remote_dir_size}")

            if remote_dir_size >= 0 and remote_dir_size == local_dir_size:
                print(f"  MATCH: Directory '{expected_dataset_dirpath}' found with matching size ({local_dir_size} bytes).")
                return True
            elif remote_dir_size < 0:
                print(f"  WARNING: Directory '{expected_dataset_dirpath}' found but remote size is unknown ({remote_dir_size}). Cannot confirm match.")
                return False
            else:
                 print(f"  MISMATCH: Directory '{expected_dataset_dirpath}' found BUT sizes differ. Local: {local_dir_size}, Remote: {remote_dir_size}.")
                 return False

    print(f"  NOT FOUND: Directory '{expected_dataset_dirpath}' not found in dataset cache.")
    return False