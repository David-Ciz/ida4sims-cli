
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from pathlib import Path
import csv
import logging
from ida4sims_cli.get_dataset_hashes import fetch_hashes_for_dataset

@pytest.mark.asyncio
async def test_fetch_hashes_csv_export(tmp_path):
    # Mock dependencies
    mock_datasets = MagicMock()
    # Mock content response
    mock_datasets.get_content_of_dataset.return_value = {
        'contents': [
             {'name': 'file1.txt', 'type': 'file'},
        ]
    }

    output_file = tmp_path / "hashes.csv"
    
    # Mock get_irods_file_hash_via_poll_async
    with patch('ida4sims_cli.get_dataset_hashes.get_irods_file_hash_via_poll_async', new_callable=AsyncMock) as mock_get_hash:
        mock_get_hash.return_value = {'result': 'sha2:verylonghashvalue1234567890', 'status': 'SUCCESS'}

        await fetch_hashes_for_dataset(
            datasets=mock_datasets, 
            dataset_id="test-id", 
            lexis_token="token",
            output_file=output_file
        )

        assert output_file.exists()
        
        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]['File Path'] == '/file1.txt'
            # Check full hash is preserved (no truncation)
            assert rows[0]['Remote Hash'] == 'sha2:verylonghashvalue1234567890'
            assert rows[0]['Status'] == 'SUCCESS'
            
@pytest.mark.asyncio
async def test_fetch_hashes_csv_export_with_comparison(tmp_path):
    # Create a dummy local file
    local_dir = tmp_path / "local"
    local_dir.mkdir()
    local_file = local_dir / "file1.txt"
    local_file.write_text("content")
    
    # Mock dependencies
    mock_datasets = MagicMock()
    mock_datasets.get_content_of_dataset.return_value = {
        'contents': [{'name': 'file1.txt', 'type': 'file'}]
    }

    output_file = tmp_path / "hashes_compare.csv"
    
    # Mock helpers
    with patch('ida4sims_cli.get_dataset_hashes.get_irods_file_hash_via_poll_async', new_callable=AsyncMock) as mock_get_hash, \
         patch('ida4sims_cli.get_dataset_hashes.calculate_sha256', return_value='sha2:localhash') as mock_calc:
        
        mock_get_hash.return_value = {'result': 'sha2:remotehash', 'status': 'SUCCESS'}

        await fetch_hashes_for_dataset(
            datasets=mock_datasets, 
            dataset_id="test-id", 
            lexis_token="token",
            compare_with=local_dir,
            output_file=output_file
        )

        assert output_file.exists()
        
        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]['File Path'] == '/file1.txt'
            assert rows[0]['Remote Hash'] == 'sha2:remotehash'
            assert rows[0]['Local Hash'] == 'sha2:localhash'
            assert rows[0]['Local Check'] == 'DIFFERS'
