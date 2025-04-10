from functions.get_local_directory_size import get_local_directory_size

def check_if_dataset_contains_directory(
    dataset_content_list: list,
    expected_dataset_dirpath: str,
    local_dir_path: str
) -> bool:
    print(f"Checking cache for iRODS directory path: '{expected_dataset_dirpath}' (Local: '{local_dir_path}')")

    local_dir_size = get_local_directory_size(local_dir_path)
    if local_dir_size == -1:
        print("  WARNING: Could not calculate local directory size. Cannot confirm match.")
        return False

    if dataset_content_list is None:
        print("  Dataset content list was not retrieved or is None. Cannot confirm existence.")
        return False

    if not dataset_content_list:
        print("  Dataset content list is empty. Directory does not exist in cache.")
        return False

    found_match = False
    for item in dataset_content_list:
        item_name = item.get('name')
        item_type = item.get('type')

        if item_type == 'directory' and item_name == expected_dataset_dirpath:
            print(f"  Found potential match for directory '{item_name}' in dataset cache.")

            remote_dir_size_raw = item.get('size')

            if remote_dir_size_raw is None:
                remote_dir_size = -1
                print(f"  WARNING: Remote size is missing for directory '{item_name}'. Cannot confirm match.")
                return False
            else:
                try:
                    remote_dir_size = int(remote_dir_size_raw)
                except (ValueError, TypeError):
                    print(f"  ERROR: Remote size value ('{remote_dir_size_raw}') for directory '{item_name}' is not a valid integer. Cannot compare.")
                    return False

            print(f"  Comparing sizes: Local={local_dir_size}, Remote={remote_dir_size}")

            if remote_dir_size < 0:
                print(f"  WARNING: Remote size is reported as invalid or negative ({remote_dir_size}). Cannot confirm match.")
                return False

            elif remote_dir_size == local_dir_size:
                print(f"  MATCH: Directory '{expected_dataset_dirpath}' found with matching size ({local_dir_size} bytes).")
                return True

            else:
                print(f"  MISMATCH: Directory '{expected_dataset_dirpath}' found BUT sizes differ. Local: {local_dir_size}, Remote: {remote_dir_size}.")
                return False

    if not found_match:
        print(f"  NOT FOUND: Directory '{expected_dataset_dirpath}' not found in dataset cache.")

    print(f"  NOT FOUND: Directory '{expected_dataset_dirpath}' not found in the dataset cache after checking all items.")
    return False