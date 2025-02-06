from py4lexis.lexis_irods import iRODS
from helpers.default_data import DEFAULT_ACCESS, PROJECT, DATASET_ID_FILE_NAME
import os

def create_lexis_dataset(irods: iRODS, title):

    if os.path.exists(DATASET_ID_FILE_NAME):
        with open(DATASET_ID_FILE_NAME, "r") as text_file:
            dataset_id = text_file.read().strip()
        print(f"Dataset ID file found. Using existing dataset ID: {dataset_id}")
        return dataset_id
    else:
        response = irods.create_dataset(
            access=DEFAULT_ACCESS, project=PROJECT, title=title
        )
        dataset_id = response["dataset_id"]

        with open(DATASET_ID_FILE_NAME, "w") as text_file:
            text_file.write(dataset_id)

        print(f"New dataset created with ID: {dataset_id}")
        return dataset_id