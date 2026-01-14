import asyncio
import logging
from typing import List, Dict, Optional
import sys
import click
from pathlib import Path
import os

from py4lexis.ddi.datasets import Datasets
from ida4sims_cli.functions.LexisAuthManager import LexisAuthManager
from ida4sims_cli.functions.hashing_utils import get_irods_file_hash_via_poll_async, calculate_sha256


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def truncate_hash(h: str, length: int = 20) -> str:
    """
    Truncates a hash string to a specified length, keeping the prefix if present.
    """
    if not h or h == "N/A" or len(h) <= length:
        return h
    # Keep prefix if present (e.g. sha2:)
    if ":" in h:
        prefix, val = h.split(":", 1)
        if len(val) > length:
            return f"{prefix}:{val[:length]}..."
        return h
    return f"{h[:length]}..."

import csv

async def fetch_hashes_for_dataset(datasets: Datasets, dataset_id: str, lexis_token: str, compare_with: Optional[Path] = None, output_file: Optional[Path] = None):
    """
    Retrieves the content of a dataset and fetches hashes for all files.
    If compare_with is provided, compares with local files.
    If output_file is provided, saves hashes to a CSV file.
    """
    logging.info(f"Retrieving content for dataset ID: {dataset_id}")
    try:
        content_response = datasets.get_content_of_dataset(dataset_id=dataset_id)
    except Exception as e:
        logging.error(f"Failed to get dataset content: {e}")
        return

    if not content_response or 'contents' not in content_response:
        logging.warning("Dataset is empty or content list is missing.")
        return

    raw_files = content_response['contents']
    if not raw_files:
        logging.info("Dataset has no files.")
        return

    # Helper to recursively collect files with full paths
    files_to_hash = []

    def collect_files(items: List[Dict], parent_path: str = ""):
        for item in items:
            name = item.get('name')
            item_type = item.get('type')
            
            # Construct full path. Py4Lexis seems to return just the name for sub-items.
            # However, for the top level item 'simulation_data', it might be a name too.
            # We need to construct path properly.
            
            current_path = f"{parent_path}/{name}" if parent_path else name
            if parent_path == "/": # handle root edge case if any, though usually empty string is start
                 current_path = f"/{name}"
            
            # Ensure path starts with / if needed by API, or match get_file_hash.py
            # get_file_hash.py used "/simulation_data/..."
            
            if item_type == 'file':
                # We need to verify if the path should have a leading slash.
                # Usually iRODS paths in LEXIS start with /.
                # If current_path doesn't start with /, preprend it?
                # But let's look at the example: 'simulation_data' is at top. 
                # If we use parent_path="", current is "simulation_data".
                # To match "/simulation_data/...", we might need to prepend /.
                
                final_path = current_path
                if not final_path.startswith("/"):
                    final_path = "/" + final_path
                    
                files_to_hash.append(final_path)
            
            elif item_type == 'directory':
                 if 'contents' in item:
                     collect_files(item['contents'], current_path)

    collect_files(raw_files)


    # Suppress verbose logging from libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("py4lexis").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    logging.info(f"Found {len(files_to_hash)} files. Fetching hashes...")
    
    # Define column widths
    col_file = 80
    col_hash = 25
    col_status = 10
    col_check = 10
    col_local_hash = 25

    header_fmt = f"{{:<{col_file}}} | {{:<{col_hash}}} | {{:<{col_status}}}"
    border_len = col_file + col_hash + col_status + 6 # separators
    
    headers = ['File Path', 'Remote Hash', 'Status']

    if compare_with:
        header_fmt += f" | {{:<{col_check}}} | {{:<{col_local_hash}}}"
        border_len += col_check + col_local_hash + 6
        headers.extend(['Local Check', 'Local Hash'])
    
    print(f"\n{header_fmt.format(*headers)}")
    print("-" * border_len)

    csv_rows = []
    
    for file_path in files_to_hash:
        result = await get_irods_file_hash_via_poll_async(dataset_id, file_path, lexis_token)
        
        remote_hash = "N/A"
        status = "Unknown"
        
        if result:
            remote_hash = result.get('result', 'N/A')
            status = result.get('status', 'Unknown') or result.get('state', 'Unknown')
        
        # Truncate remote hash for display
        display_remote_hash = truncate_hash(remote_hash)

        row = [file_path, display_remote_hash, status]
        csv_row = {'File Path': file_path, 'Remote Hash': remote_hash, 'Status': status} # Full hash for CSV
        
        if compare_with:
            # Determine local path
            # dataset paths start with /, so strip it to join with local dir
            rel_path = file_path.lstrip('/')
            local_file = compare_with / rel_path
            
            local_status = "MISSING"
            local_hash = "-"
            
            if local_file.exists() and local_file.is_file():
                try:
                    local_hash_val = calculate_sha256(local_file)
                    local_hash = local_hash_val
                    
                    if remote_hash == local_hash_val:
                        local_status = "MATCH"
                    else:
                        local_status = "DIFFERS"
                        
                    if remote_hash == "N/A":
                         local_status = "REMOTE_NA"
                         
                except Exception as e:
                    local_status = "ERROR"
                    logging.debug(f"Error checking local file {local_file}: {e}")
            
            # Truncate local hash for display
            display_local_hash = truncate_hash(local_hash)

            row.extend([local_status, display_local_hash])
            print(header_fmt.format(*row))
            
            csv_row['Local Check'] = local_status
            csv_row['Local Hash'] = local_hash # Full hash for CSV
        else:
            print(header_fmt.format(*row))
        
        if output_file:
            csv_rows.append(csv_row)

    if output_file and csv_rows:
        try:
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=csv_rows[0].keys())
                writer.writeheader()
                writer.writerows(csv_rows)
            logging.info(f"Hashes exported to {output_file}")
        except Exception as e:
            logging.error(f"Failed to write output file {output_file}: {e}")


@click.command()
@click.argument('dataset_id', type=str, required=True)
@click.option('--compare-with', type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path), help="Local directory to compare hashes with.")
@click.option('--output-file', '-o', type=click.Path(file_okay=True, dir_okay=False, path_type=Path), help="Path to save hashes (CSV format).")
def cli(dataset_id, compare_with, output_file):
    """
    Get hashes for all files in a dataset.

    DATASET_ID: The UUID of the dataset.

    Optionally compare with a local directory using --compare-with.
    The script assumes the local directory structure mirrors the dataset structure.

    Optionally save results to a CSV file using --output-file / -o.
    """
    async def main():
        auth_manager = LexisAuthManager()
        session = auth_manager.login()
        if not session:
            logging.error("Failed to login.")
            sys.exit(1)

        lexis_token = session.get_access_token()
        datasets = Datasets(session=session, suppress_print=True) # suppress_print to keep output clean

        await fetch_hashes_for_dataset(datasets, dataset_id, lexis_token, compare_with, output_file)

    asyncio.run(main())

if __name__ == "__main__":
    cli()
