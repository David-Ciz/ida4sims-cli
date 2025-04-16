import logging
from py4lexis.ddi.datasets import Datasets
from ida4sims_cli.functions.LexisAuthManager import LexisAuthManager
from ida4sims_cli.helpers.default_data import DATASET_ID_FILE_NAME

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
lexisAuthManager = LexisAuthManager()

def print_dataset_content(datasets: Datasets, dataset_id: str):
    """Retrieves and prints the contents of a dataset."""
    try:
        logging.info(f"Attempting to retrieve content for dataset ID: {dataset_id}")
        filelist = datasets.get_content_of_dataset(dataset_id=dataset_id)

        print(f"\n--- Contents of dataset {dataset_id} ---")
        if filelist and 'contents' in filelist and len(filelist['contents']) > 0:
            for item in filelist['contents']:
                item_path = item.get('name', 'N/A')
                item_type = item.get('type', 'N/A')
                item_size = item.get('size', 'N/A')

                print(f"  - Path: {item_path}")
                print(f"    Type: {item_type}, Size: {item_size}")
                print("-" * 20)
            print("------------------------------------")
            return True

        elif filelist and 'contents' in filelist:
             print("  Dataset is empty.")
             print("------------------------------------")
             return True 
        else:
            logging.warning("Received empty or invalid response, or 'contents' key missing.")
            print("  Could not retrieve dataset contents or structure is invalid.")
            print("------------------------------------")
            return False

    except Exception as e:
        logging.error(f"Error retrieving/printing dataset contents for {dataset_id}: {e}", exc_info=True)
        print(f"  Error checking dataset contents: {e}")
        print("------------------------------------")
        return False

if __name__ == "__main__":
    dataset_id = None
    try:
        with open(DATASET_ID_FILE_NAME, "r") as text_file:
            dataset_id = text_file.read().strip()
            logging.info(f"Read dataset ID: {dataset_id} from {DATASET_ID_FILE_NAME}")
    except FileNotFoundError:
         logging.error(f"Error: Dataset ID file not found at {DATASET_ID_FILE_NAME}")
         exit() 
    except Exception as e:
         logging.error(f"Error reading dataset ID file: {e}")
         exit() 

    session = lexisAuthManager.login()
    if not session:
         logging.error("Failed to get LEXIS session. Exiting.")
         exit()

    datasets = Datasets(session=session, suppress_print=False)
    print_dataset_content(datasets, dataset_id)

    logging.info("Script finished.")
