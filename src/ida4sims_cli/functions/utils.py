import time
import contextlib
import io
from typing import Optional, List, Any, Tuple
from py4lexis.ddi.datasets import Datasets

def wait_for_dataset_contents(datasets: Datasets, dataset_id: str, max_retries: int = 24, retry_delay: int = 5) -> Tuple[Optional[List[Any]], int]:
    """
    Waits for a dataset to be created and propagated in iRODS by polling its content.
    
    Args:
        datasets: The py4lexis Datasets object.
        dataset_id: The ID of the dataset to check.
        max_retries: Maximum number of polling attempts.
        retry_delay: Delay in seconds between attempts.
        
    Returns:
        A tuple containing:
        - The list of content items if found (or empty list if empty), or None if it never appeared.
        - The number of attempts made.
    """
    dataset_content_list = None
    attempts_used = 0

    # Use a suppressed-output wrapper around calls to py4lexis to avoid noisy prints
    for attempt in range(1, max_retries + 1):
        attempts_used = attempt
        try:
            # Suppress stdout/stderr produced by py4lexis internals during the call
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                filelist_response = datasets.get_content_of_dataset(dataset_id=dataset_id)

            if filelist_response is None:
                # py4lexis returns None and prints error if dataset doesn't exist yet
                print(f"  (Attempt {attempt}/{max_retries}) Dataset content not visible yet. Waiting {retry_delay}s...")
                time.sleep(retry_delay)
                continue

            if isinstance(filelist_response, dict) and 'contents' in filelist_response:
                 dataset_content_list = filelist_response.get('contents')
                 if dataset_content_list:
                      print(f"  Found {len(dataset_content_list)} item(s) in dataset root (after {attempt} attempt(s)).")
                 else:
                      print(f"  Dataset root is empty (checked {attempt} time(s)).")
                 break
            else:
                print(f"  Dataset is currently empty or content could not be retrieved (checked {attempt} time(s)).")
                dataset_content_list = []
                break
        except Exception as e:
            # Hide noisy py4lexis output but show concise retry info to user
            print(f"  WARNING: Could not fetch dataset contents (attempt {attempt}/{max_retries}): {e}. Retrying in {retry_delay}s...")
            time.sleep(retry_delay)

    return dataset_content_list, attempts_used
