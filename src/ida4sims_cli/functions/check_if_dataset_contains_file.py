import os
from typing import List, Dict, Any

def check_if_dataset_contains_file(
    dataset_content_list: List[Dict[str, Any]],
    expected_dataset_filepath: str,
    local_file_path: str
) -> bool:
    print(f"Checking cache for iRODS path: '{expected_dataset_filepath}' (Local: '{local_file_path}')")

    try:
        local_file_size = os.path.getsize(local_file_path)
    except FileNotFoundError:
        print(f"  Local file '{local_file_path}' not found. Cannot compare size.")
        return False
    except OSError as e:
        print(f"  Error accessing local file '{local_file_path}': {e}. Cannot compare size.")
        return False

    if dataset_content_list is None:
        print("  Dataset content list was not retrieved or is None. Cannot confirm existence.")
        return False

    if not dataset_content_list:
        print("  Dataset content list is empty. File does not exist in cache.")
        return False

    for item in dataset_content_list:
        item_path = item.get('name')
        item_type = item.get('type')

        if item_type == 'file' and item_path == expected_dataset_filepath:
            print(f"  Found potential match for file '{item_path}' in dataset cache.")

            remote_file_size_raw = item.get('size')

            if remote_file_size_raw is None:
                print(f"  WARNING: Remote size is missing for file '{item_path}'. Cannot confirm match.")
                return False
            else:
                try:
                    remote_file_size = int(remote_file_size_raw)
                except (ValueError, TypeError):
                    print(f"  ERROR: Remote size value ('{remote_file_size_raw}') for file '{item_path}' is not a valid integer. Cannot compare.")
                    return False

            print(f"  Comparing sizes: Local={local_file_size}, Remote={remote_file_size}")

            if remote_file_size < 0:
                print(f"  WARNING: Remote size is reported as invalid or negative ({remote_file_size}). Cannot confirm match.")
                return False

            elif remote_file_size == local_file_size:
                print(f"  MATCH: File '{expected_dataset_filepath}' found with matching size ({local_file_size} bytes).")
                return True

            else:
                print(f"  MISMATCH: File '{expected_dataset_filepath}' found BUT sizes differ. Local: {local_file_size}, Remote: {remote_file_size}.")
                return False

    print(f"  NOT FOUND: File '{expected_dataset_filepath}' not found in the dataset cache after checking all items.")
    return False