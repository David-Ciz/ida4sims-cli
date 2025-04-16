def check_if_dataset_contains_directory(
    dataset_content_list: list,
    expected_dataset_dirpath: str,
    local_dir_path: str
) -> bool:
    print(f"Checking cache for iRODS directory path: '{expected_dataset_dirpath}' (Local: '{local_dir_path}')")
    
    if dataset_content_list is None:
        print("  Dataset content list was not retrieved or is None. Cannot confirm existence.")
        return False

    if not dataset_content_list:
        print("  Dataset content list is empty. Directory does not exist in cache.")
        return False

    for item in dataset_content_list:
        item_name = item.get('name')
        item_type = item.get('type')

        if item_type == 'directory' and item_name == expected_dataset_dirpath:
            print(f"  Found match for directory '{item_name}' in dataset cache.")
            return True
        
    return False