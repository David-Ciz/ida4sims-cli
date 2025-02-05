import argparse
from get_session import get_offline_session
from create_dataset import create_lexis_dataset, DEFAULT_ACCESS, PROJECT
from upload_files import upload_files_to_lexis
from py4lexis.lexis_irods import iRODS
from py4lexis.ddi.datasets import Datasets

def main():
    parser = argparse.ArgumentParser(description='Upload a dataset to LEXIS')
    parser.add_argument('title', type=str, help='Dataset title')
    parser.add_argument('directory', type=str, help='Local directory path to upload')
    parser.add_argument('--access', type=str, default=DEFAULT_ACCESS,
                        help=f'Access level for the dataset (e.g., public, private, project). Default: {DEFAULT_ACCESS}')
    parser.add_argument('--project', type=str, default=PROJECT,
                        help=f'Project for the dataset. Default: {PROJECT}')

    args = parser.parse_args()

    print(f"Creating dataset '{args.title}'...")
    print("Checking for refresh token...(main.py)")
    offline_session = get_offline_session()
        
    print("Creating iRODS object...(main.py)")
    irods = iRODS(session=offline_session, suppress_print=False)
    datasets = Datasets(session=offline_session, suppress_print=False)
    
    print("Creating dataset...(main.py)")
    dataset_id = create_lexis_dataset(irods, args.title)

    print("Uploading files to dataset...(main.py)")
    upload_files_to_lexis(irods, datasets, args.directory, dataset_id)

    print(f"Dataset '{args.title}' created with ID: {dataset_id}")
    print(f"Files from '{args.directory}' uploaded to dataset.")

if __name__ == "__main__":
    main()