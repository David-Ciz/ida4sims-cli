import argparse
from functions.get_session import get_session
from functions.create_dataset import create_lexis_dataset
from functions.upload_dataset_content import upload_dataset_content
from functions.delete_dataset_id import delete_saved_dataset_id
from py4lexis.lexis_irods import iRODS
from py4lexis.ddi.datasets import Datasets
from helpers.default_data import DEFAULT_ACCESS

def main():
    parser = argparse.ArgumentParser(description='Upload a dataset to LEXIS')
    parser.add_argument('title', type=str, help='Dataset title')
    parser.add_argument('path', type=str, help='Local file or directory path to upload')
    parser.add_argument('--access', type=str, default=DEFAULT_ACCESS,
                        help=f'Access level for the dataset (e.g., public, user, project). Default: {DEFAULT_ACCESS}')

    args = parser.parse_args()

    print(f"Processing dataset '{args.title}' with path '{args.path}'...")
    print("Checking for refresh token...(main.py)")
    session = get_session()

    print("Creating iRODS object...(main.py)")
    irods = iRODS(session=session, suppress_print=False)

    print("Creating Datasets object...(main.py)") 
    datasets = Datasets(session=session, suppress_print=False)
    print("Creating dataset...(main.py)")
    dataset_id = create_lexis_dataset(irods, args.title)


    print(f"Created dataset '{dataset_id}'...")
    print("Uploading content to dataset...(main.py)")

    try:
        upload_dataset_content(irods, datasets, args.path, dataset_id)

        print("Deleting saved dataset ID...(main.py)")
        delete_saved_dataset_id()
        print(f"Dataset '{args.title}' created with ID: {dataset_id}")
        print(f"Content from '{args.path}' uploaded to dataset.")

    except Exception as e:
        print(f"\n--- ERROR during upload ---")
        print(f"Dataset '{dataset_id}' was created, but content upload failed.")
        print(f"Local path: '{args.path}'")
        print(f"Error details: {e}")
        print("Consider manually uploading the content or deleting the dataset.")

if __name__ == "__main__":
    main()