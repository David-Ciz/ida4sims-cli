from functions.get_dataset_content import get_dataset_content
from py4lexis.ddi.datasets import Datasets
from functions.get_session import get_offline_session

from helpers.default_data import DATASET_ID_FILE_NAME

def main():
    with open(DATASET_ID_FILE_NAME, "r") as text_file:
            dataset_id = text_file.read().strip()
             
    offline_session = get_offline_session()

    datasets = Datasets(session=offline_session, suppress_print=False)

    filelist = get_dataset_content(datasets, dataset_id)

    print(f"Contents of dataset {dataset_id}:")
    print(filelist)
    
if __name__ == "__main__":
    main()