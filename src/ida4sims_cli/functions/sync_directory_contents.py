import os
from pathlib import Path
from py4lexis.lexis_irods import iRODS

from ida4sims_cli.helpers.default_data import DEFAULT_ACCESS, PROJECT


def sync_directory_contents(irods: iRODS, contents1, contents2, dataset_id: str, local_path='', parent_path=''):

    missing = []
    extra = []
    mismatched = []

    safe_contents1 = contents1 if contents1 is not None else []
    safe_contents2 = contents2 if contents2 is not None else []

    map1 = {item['name']: item for item in safe_contents1 if isinstance(item, dict) and 'name' in item}
    map2 = {item['name']: item for item in safe_contents2 if isinstance(item, dict) and 'name' in item}

    for name, item1 in map1.items():
        path = os.path.join(parent_path, name)
        if parent_path == '':
            local_item_full_path = local_path
        else:
            local_item_full_path = os.path.join(local_path, name)

        item2 = map2.get(name)

        if item2 is None:
            print(f"    🔴 MISSING LOCALLY: Dataset item '{name}' not found locally at expected path '{local_item_full_path}' (Dataset path: '{path}')")
            missing.append({
                'path': path, 
                'local_path': local_item_full_path,
                'item': item1,
                'reason': 'Missing in local data (source 2)'
            })
            if item1.get('type') == 'directory' and item1.get('contents'):
                print(f"      recursing into MISSING directory '{name}' to mark contents...")
                sub_diffs = sync_directory_contents(
                    irods,
                    item1.get('contents'),
                    None,
                    dataset_id,
                    local_item_full_path,
                    path
                )
                missing.extend(sub_diffs['missing_locally'])
        else:
            item1_type = item1.get('type')
            
            if item1_type == 'file':
                item1_size = item1.get('size')
                item2_size = item2.get('size')
                if item1_size != item2_size:
                    print(f"    🟡 MISMATCH: Size difference for file '{name}'. Dataset={item1_size} (at '{path}'), Local={item2_size} (at '{local_item_full_path}')")
                    mismatched.append({
                        'path': path,
                        'local_path': local_item_full_path,
                        'item1': item1,
                        'item2': item2,
                        'reason': f"Size mismatch: dataset is {item1_size}, local is {item2_size}"
                    })
                    print(f"Attempting to upload file '{local_item_full_path}' as '{path}'...")
                    print(dataset_id)
                    irods.put_data_object_to_dataset(
                        local_filepath=local_item_full_path,
                        dataset_filepath=str(Path(path).parent),
                        dataset_id=dataset_id,
                        overwrite=True,
                        use_sqlite_for_handle_management=True
                    )
                else:
                    pass

            elif item1_type == 'directory':
                 print(f"recursing into directory '{name}'...")
                 sub_diffs = sync_directory_contents(
                    irods,
                    item1.get('contents'),
                    item2.get('contents'),
                    dataset_id,
                    local_item_full_path, 
                    path
                 )
                 missing.extend(sub_diffs['missing_locally'])
                 extra.extend(sub_diffs['extra_locally'])
                 mismatched.extend(sub_diffs['mismatches'])

    for name, item2 in map2.items():
        if name not in map1:
            file_path = os.path.join(parent_path, name) 

            if parent_path == '':
                 local_item_full_path = local_path 
            else:
                 local_item_full_path = os.path.join(local_path, name)
                 print(local_path)
                 print(name)        
        
            if item2.get('type') == 'directory' and item2.get('contents'):
                
                print(f"    🔵 EXTRA LOCALLY Directory: Local item '{name}' not found in dataset at expected path '{path}' (Local path: '{local_item_full_path}')")
                extra.append({
                    'path': path,
                    'local_path': local_item_full_path, 
                    'item': item2,
                    'reason': 'Extra in local data (source 2), not in dataset'
                })
                
                irods.upload_directory_to_dataset(
                    local_directorypath=local_item_full_path,
                    dataset_id=dataset_id,
                    dataset_directorypath=parent_path,
                    use_sqlite_for_handle_management=True
                )
                
            elif item2.get('type') == 'file':
                print(f"    🔵 EXTRA LOCALLY File: Local item '{name}' not found in dataset at expected path '{file_path}' (Local path: '{local_item_full_path}')")
                extra.append({
                    'path': file_path,
                    'local_path': local_item_full_path, 
                    'item': item2,
                    'reason': 'Extra in local data (source 2), not in dataset'
                })
                print("EXTRA FILE")
                irods.put_data_object_to_dataset(
                    local_filepath=local_item_full_path,
                    dataset_filepath=str(Path(file_path).parent),
                    dataset_id=dataset_id,                    
                    overwrite=True,
                    use_sqlite_for_handle_management=True
                )

    return {'missing_locally': missing, 'extra_locally': extra, 'mismatches': mismatched}