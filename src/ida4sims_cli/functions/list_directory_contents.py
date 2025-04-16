from pathlib import Path
from typing import List, Dict, Optional, Union, Any
import json

def _get_recursive_contents(dir_path: Path) -> Optional[List[Dict[str, Any]]]:
    
    contents_list = []
    try:
        for entry in dir_path.iterdir():
            item_info = {"name": entry.name}
            try:
                stat_result = entry.stat()

                if entry.is_file():
                    item_info["type"] = "file"
                    item_info["size"] = stat_result.st_size

                elif entry.is_dir():
                    item_info["type"] = "directory"
                    nested_contents = _get_recursive_contents(entry)
                    if nested_contents is not None:
                        item_info["contents"] = nested_contents
                        dir_content_size = sum(
                            item.get("size", 0) if isinstance(item.get("size"), (int, float)) else 0
                            for item in nested_contents
                        )
                        item_info["size"] = dir_content_size
                    else:
                        item_info["contents"] = []
                        item_info["size"] = 0
                        print(f"Warning: Could not fully scan subdirectory '{entry.name}'. Size/contents incomplete.")

                else:
                    item_info["type"] = "other"
                    try:
                        item_info["size"] = stat_result.st_size
                    except OSError:
                        item_info["size"] = 0
                        item_info["type"] = "broken_link"

                contents_list.append(item_info)

            except (FileNotFoundError, PermissionError, OSError) as e:
                print(f"Warning: Could not access item '{entry.name}' in '{dir_path}'. Error: {e}. Skipping.")
                contents_list.append({
                    "name": entry.name,
                    "type": "error",
                    "size": 0,
                    "error_message": str(e)
                })
        return contents_list

    except (PermissionError, OSError) as e:
         print(f"Error: Could not iterate directory '{dir_path}' during scan. Error: {e}")
         return None


def list_directory_contents(dir_path: Union[str, Path]) -> Optional[List[Dict[str, Any]]]:
   
    try:
        path_obj = Path(dir_path).resolve()
        if not path_obj.is_dir():
            if not path_obj.exists():
                 print(f"Error: Path '{dir_path}' does not exist.")
            else:
                 print(f"Error: Path '{path_obj}' is not a directory.")
            return None

        contents = _get_recursive_contents(path_obj)

        if contents is None:
             print(f"Error: Failed to retrieve contents for '{path_obj}'. Cannot generate entry details.")
             return None

        total_size = sum(
            item.get("size", 0) if isinstance(item.get("size"), (int, float)) else 0
            for item in contents 
        )

        dir_details = {
            "name": path_obj.name,
            "type": "directory",
            "size": total_size,
            "contents": contents
        }

        return [dir_details]

    except (PermissionError, OSError) as e:
        print(f"Error: Could not access or process directory '{dir_path}'. Error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred processing '{dir_path}': {e}")
        return None


if __name__ == "__main__":
    target_directory = '.' 

    print(f"Scanning directory: {Path(target_directory).resolve()}")
    
    local_structure_list = list_directory_contents(target_directory) 

    print("\n--- Generated Local Structure ---")
    if local_structure_list:
        print(json.dumps(local_structure_list, indent=2))
            
    else:
        print("Could not generate directory structure (check error messages above).")
    print("---------------------------------")