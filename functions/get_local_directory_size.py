import os

def get_local_directory_size(directory_path):
    total_size = 0
    print(f"Calculating local directory size for: '{directory_path}'...")
    try:
        for dirpath, dirnames, filenames in os.walk(directory_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    try:
                        total_size += os.path.getsize(fp)
                    except OSError as e:
                        print(f"  WARNING: Could not get size of file '{fp}': {e}. Skipping file.")
    except OSError as e:
         print(f"  ERROR: Could not access directory '{directory_path}' to calculate size: {e}.")
         return -1

    print(f"  Calculated local size: {total_size} bytes.")
    return total_size