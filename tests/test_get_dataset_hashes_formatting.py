
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from pathlib import Path
import logging
from ida4sims_cli.get_dataset_hashes import fetch_hashes_for_dataset, truncate_hash


# Test the helper function directly
def test_truncate_hash():
    assert truncate_hash("short") == "short"
    assert truncate_hash("sha2:verylonghashstringthatneedstruncating") == "sha2:verylonghashstringth..."
    assert truncate_hash("sha2:short", length=10) == "sha2:short"
    assert truncate_hash(None) is None
    assert truncate_hash("N/A") == "N/A"

@pytest.mark.asyncio
async def test_fetch_hashes_output_formatting(capsys):
    # Mock dependencies
    mock_datasets = MagicMock()
    # Mock content response
    mock_datasets.get_content_of_dataset.return_value = {
        'contents': [
             {'name': 'file1.txt', 'type': 'file'},
             {'name': 'dir1', 'type': 'directory', 'contents': [
                 {'name': 'file2.txt', 'type': 'file'}
             ]}
        ]
    }

    # Mock get_irods_file_hash_via_poll_async
    with patch('ida4sims_cli.get_dataset_hashes.get_irods_file_hash_via_poll_async', new_callable=AsyncMock) as mock_get_hash:
        # Return different hashes
        mock_get_hash.side_effect = [
            {'result': 'sha2:verylonghashthatshouldbetruncated123456', 'status': 'SUCCESS'}, # file1
            {'result': 'sha2:anotherlonghash78901234567890', 'status': 'SUCCESS'}   # file2
        ]

        await fetch_hashes_for_dataset(
            datasets=mock_datasets, 
            dataset_id="test-id", 
            lexis_token="token"
        )

        captured = capsys.readouterr()
        output = captured.out

        # Verify header
        assert "File Path" in output
        assert "Remote Hash" in output
        assert "Status" in output
        
        # Verify separators are present
        assert "|" in output
        assert "-" * 20 in output # check for some separator line

        # Verify content is present and truncated
        assert "/file1.txt" in output
        assert "/dir1/file2.txt" in output
        
        
        # Check truncation
        assert "sha2:verylonghashthatshou..." in output
        assert "sha2:verylonghashthatshouldbetruncated123456" not in output
        
        # Verify no INFO logs in stderr/stdout (capsys captures everything)
        # Note: logging.info still goes to stderr usually, but we silenced libraries, not root totally?
        # get_dataset_hashes.py: logging.info(f"Found {len(files_to_hash)} files. Fetching hashes...")
        # This one is allowed. We wanted to silence requests/urllib3. 
        # Since we mock them here, we can't really test the silencing of real requests, 
        # but we can verify our own logs are present.
