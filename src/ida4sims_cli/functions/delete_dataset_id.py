from ida4sims_cli.helpers.default_data import DATASET_ID_FILE_NAME
import os

def delete_saved_dataset_id():
    try:
        if os.path.exists(DATASET_ID_FILE_NAME):
            os.remove(DATASET_ID_FILE_NAME)
            print(f"File '{DATASET_ID_FILE_NAME}' deleted successfully.")
        else:
            print(f"File '{DATASET_ID_FILE_NAME}' does not exist.")

    except Exception as e:
        print(f"Error deleting file: {e}")