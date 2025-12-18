from typing import Dict
from typing import cast

from py4lexis.lexis_irods import iRODS
from py4lexis.core.typings.ddi import DatasetType

from ida4sims_cli.helpers.default_data import DEFAULT_ACCESS, PROJECT, DATASET_ID_FILE_NAME, STORAGE_NAME, STORAGE_RESOURCE
import os

def create_lexis_dataset(irods: iRODS, title: str, metadata: Dict[str, str]) -> str:

    if os.path.exists(DATASET_ID_FILE_NAME):
        with open(DATASET_ID_FILE_NAME, "r") as text_file:
            dataset_id = text_file.read().strip()
        print(f"Dataset ID file found. Using existing dataset ID: {dataset_id}")
        return dataset_id
    else:
        dataset_type_str = metadata["dataset_type"]
        dataset_type:  DatasetType = cast(DatasetType, dataset_type_str)

        response = irods.create_dataset(
            access=DEFAULT_ACCESS, project=PROJECT, storage_name=STORAGE_NAME, storage_resource=STORAGE_RESOURCE, title=title, additional_metadata=metadata, dataset_type= dataset_type
        )
        
        dataset_id = response["dataset_id"]

        with open(DATASET_ID_FILE_NAME, "w") as text_file:
            text_file.write(dataset_id)

        print(f"New dataset created with ID: {dataset_id}")
        return dataset_id