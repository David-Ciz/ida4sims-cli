from py4lexis.ddi.datasets import Datasets

def get_dataset_content(datasets: Datasets, dataset_id: str):
    try:
        filelist = datasets.get_content_of_dataset(dataset_id=dataset_id)

        print(f"Contents of dataset {dataset_id}:")
        if filelist and 'contents' in filelist:
            for item in filelist['contents']:
                item_path = item['name']
                item_type = item['type']
                item_size = item.get('size', 'N/A') 
                create_time = item.get('create_time', 'N/A')
                print(f"  - {item_path} ({item_type}), Size: {item_size}, Created: {create_time}")

        else:
            print("  - Dataset is empty or 'contents' key is missing.")
            return False
        return True

    except Exception as e:
        print(f"Error checking dataset contents: {e}")
        return False