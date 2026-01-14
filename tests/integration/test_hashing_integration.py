import pytest
import os
import asyncio
import uuid
import logging
from pathlib import Path
import shutil

from ida4sims_cli.functions.LexisAuthManager import LexisAuthManager
from py4lexis.lexis_irods import iRODS
from py4lexis.ddi.datasets import Datasets
from ida4sims_cli.get_dataset_hashes import fetch_hashes_for_dataset
from ida4sims_cli.helpers.default_data import DEFAULT_ACCESS, PROJECT, STORAGE_NAME, STORAGE_RESOURCE

# Integration tests usually require real credentials and network access.
# They are often skipped by default or marked specially.
# use `pytest -m integration` if we had markers, but for now we just run it.

@pytest.mark.asyncio
async def test_hashing_integration(capsys, tmp_path):
    print("\n--- Starting Integration Test ---")
    
    # 1. Authenticate
    auth = LexisAuthManager()
    session = auth.login()
    assert session is not None, "Failed to login to LEXIS"
    
    irods = iRODS(session=session, suppress_print=True)
    datasets = Datasets(session=session, suppress_print=True)
    
    # 2. Setup Test Data
    dataset_title = f"IntegrationTest_Hashing_{uuid.uuid4()}"
    local_dir = tmp_path / "integration_data"
    local_dir.mkdir()
    
    file1 = local_dir / "test_file_1.txt"
    file1.write_text("Hello LEXIS")
    
    file2 = local_dir / "test_file_2.txt"
    file2.write_text("Another verification file")
    
    print(f"Created temporary local data at {local_dir}")
    
    dataset_id = None
    try:
        # 3. Create Dataset
        print(f"Creating dataset '{dataset_title}'...")
        # We assume simulation type or generic. Upload script uses explicit types.
        # Let's use 'generic' or 'simulation' if allowed.
        # Check create_dataset.py: uses cast(DatasetType, metadata["dataset_type"])
        # We'll try 'generic' if accepted, or 'simulation'.
        
        # NOTE: create_dataset signature in py4lexis might require specific enum
        # But looking at CLI code, it passes string.
        # Let's try to mimic create_dataset.py but calling irods directly
        
        # We need a valid dataset type. 'simulation' is commonly used in this CLI.
        metadata = {
             "dataset_type": "simulation",
             "description": "Integration test dataset for hashing"
        }
        
        response = irods.create_dataset(
            access=DEFAULT_ACCESS,
            project=PROJECT,
            storage_name=STORAGE_NAME,
            storage_resource=STORAGE_RESOURCE,
            title=dataset_title,
            additional_metadata=metadata,
            dataset_type="simulation" # Pass as string, py4lexis should handle or check
        )
        
        dataset_id = response['dataset_id']
        print(f"Dataset created: {dataset_id}")
        
        # 4. Upload Data
        print("Uploading data...")
        # Use upload_directory_to_dataset from irods
        # This is synchronous in py4lexis usually? Check imports. Yes, iRODS methods mostly blocking.
        # But we are in async test. It should be fine to call blocking io if it's not too long, 
        # or we might block the loop. For test it is acceptable.
        
        irods.upload_directory_to_dataset(
            local_directorypath=str(local_dir),
            dataset_id=dataset_id
        )
        print("Upload command finished.")
        
        # 5. Wait for content (consistency check)
        print("Waiting for file registration...")
        found = False
        for i in range(10):
            content = datasets.get_content_of_dataset(dataset_id)
            if content and content.get('contents'):
                print(f"Content found: {len(content['contents'])} items")
                found = True
                break
            await asyncio.sleep(2)
            
        assert found, "Dataset content not found after upload"

        # 6. Run Hashing Comparison
        print("Running fetching and comparison...")
        token = session.get_access_token()
        
        # We need to capture stdout
        # Note: fetch_hashes_for_dataset uses print(), capsys captures it.
        
        # The dataset contains 'integration_data/test_file_1.txt'.
        # We need to pass the parent of 'local_dir' so that joining 'integration_data/...' works.
        await fetch_hashes_for_dataset(datasets, dataset_id, token, compare_with=local_dir.parent)
        
        captured = capsys.readouterr()
        output = captured.out
        print("Output from hashing function:\n", output)
        
        # 7. Verify
        assert "test_file_1.txt" in output
        assert "test_file_2.txt" in output
        assert "MATCH" in output
        assert "DIFFERS" not in output
        assert "MISSING" not in output
        
    finally:
        # 8. Cleanup
        if dataset_id:
            print(f"Deleting dataset {dataset_id}...")
            try:
                datasets.delete_dataset_by_id(dataset_id=dataset_id)
                print("Dataset deleted.")
            except Exception as e:
                print(f"Failed to delete dataset: {e}")

if __name__ == "__main__":
    # Allow running this script directly
    logging.basicConfig(level=logging.INFO)
    sys.exit(pytest.main(["-v", __file__]))
