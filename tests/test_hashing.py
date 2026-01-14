import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import json
from ida4sims_cli.get_dataset_hashes import fetch_hashes_for_dataset
from ida4sims_cli.functions.hashing_utils import create_hash_request_async, poll_status_async

# Mocking the Datasets class and its method
@pytest.fixture
def mock_datasets():
    datasets = MagicMock()
    return datasets

@pytest.fixture
def mock_lexis_token():
    return "mock_token"

@pytest.fixture
def dataset_id():
    return "mock_dataset_id"

@pytest.mark.asyncio
async def test_fetch_hashes_for_dataset_success(mock_datasets, mock_lexis_token, dataset_id, capsys):
    # Setup mock content response
    mock_datasets.get_content_of_dataset.return_value = {
        'contents': [
            {'name': 'file1.txt', 'type': 'file'},
            {'name': 'dir1', 'type': 'directory', 'contents': [
                {'name': 'file2.txt', 'type': 'file'}
            ]}
        ]
    }

    # Mock the hashing utility functions
    with patch('ida4sims_cli.get_dataset_hashes.get_irods_file_hash_via_poll_async', new_callable=AsyncMock) as mock_get_hash:
        # Define side effects for the mock to return different hashes for different files
        async def side_effect(ds_id, path, token):
            if path.endswith('file1.txt'):
                return {'result': 'hash1', 'status': 'SUCCESS'}
            elif path.endswith('file2.txt'):
                return {'result': 'hash2', 'status': 'SUCCESS'}
            return None
        
        mock_get_hash.side_effect = side_effect

        # Run the function
        await fetch_hashes_for_dataset(mock_datasets, dataset_id, mock_lexis_token)

        # detailed assertions
        # Check if get_content_of_dataset was called correctly
        mock_datasets.get_content_of_dataset.assert_called_once_with(dataset_id=dataset_id)

        # Check if hash function was called for both files
        assert mock_get_hash.call_count == 2
        
        # Verify calls with correct paths (taking into account the path construction logic in the script)
        # The script constructs paths. For 'file1.txt' at root, it might be '/file1.txt' or 'file1.txt' depending on parent_path logic.
        # In the script: 
        # root item: parent_path="", current_path="file1.txt" -> final_path="/file1.txt" (if it doesn't start with /)
        # dir item: parent_path="", current_path="dir1"
        #   sub item: parent_path="dir1", name="file2.txt", current_path="dir1/file2.txt" -> final_path="/dir1/file2.txt"
        
        # We need to verify these exact calls
        calls = mock_get_hash.call_args_list
        # Extract paths from calls
        paths_called = [call.args[1] for call in calls]
        assert '/file1.txt' in paths_called
        assert '/dir1/file2.txt' in paths_called

    # verify output
    captured = capsys.readouterr()
    assert "file1.txt" in captured.out
    assert "hash1" in captured.out
    assert "file2.txt" in captured.out
    assert "hash2" in captured.out

@pytest.mark.asyncio
async def test_fetch_hashes_with_comparison(mock_datasets, mock_lexis_token, dataset_id, capsys, tmp_path):
    # Setup mock content response
    mock_datasets.get_content_of_dataset.return_value = {
        'contents': [
            {'name': 'file1.txt', 'type': 'file'}
        ]
    }
    
    # Create local file with known hash
    # "test" -> sha256: 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
    # base64: n4bQgYhMfWWaL+qgxVrQFaO/TxsrC4Is0V1sFbDwCgg=
    local_file = tmp_path / "file1.txt" 
    local_file.write_text("test")
    expected_hash = "sha2:n4bQgYhMfWWaL+qgxVrQFaO/TxsrC4Is0V1sFbDwCgg="
    
    with patch('ida4sims_cli.get_dataset_hashes.get_irods_file_hash_via_poll_async', new_callable=AsyncMock) as mock_get_hash:
        # Remote file matches local
        mock_get_hash.return_value = {'result': expected_hash, 'status': 'SUCCESS'}
        
        await fetch_hashes_for_dataset(mock_datasets, dataset_id, mock_lexis_token, compare_with=tmp_path)
        
        captured = capsys.readouterr()
        assert "MATCH" in captured.out
        assert expected_hash in captured.out
        
    with patch('ida4sims_cli.get_dataset_hashes.get_irods_file_hash_via_poll_async', new_callable=AsyncMock) as mock_get_hash:
        # Remote file differs
        mock_get_hash.return_value = {'result': 'sha2:differentHASH', 'status': 'SUCCESS'}
        
        await fetch_hashes_for_dataset(mock_datasets, dataset_id, mock_lexis_token, compare_with=tmp_path)
        
        captured = capsys.readouterr()
        assert "DIFFERS" in captured.out



@pytest.mark.asyncio
async def test_fetch_hashes_empty_dataset(mock_datasets, mock_lexis_token, dataset_id):
    mock_datasets.get_content_of_dataset.return_value = {'contents': []}
    
    with patch('ida4sims_cli.get_dataset_hashes.get_irods_file_hash_via_poll_async', new_callable=AsyncMock) as mock_get_hash:
        await fetch_hashes_for_dataset(mock_datasets, dataset_id, mock_lexis_token)
        mock_get_hash.assert_not_called()

@pytest.mark.asyncio
async def test_fetch_hashes_api_error(mock_datasets, mock_lexis_token, dataset_id):
    mock_datasets.get_content_of_dataset.side_effect = Exception("API Error")
    
    with patch('ida4sims_cli.get_dataset_hashes.get_irods_file_hash_via_poll_async', new_callable=AsyncMock) as mock_get_hash:
        await fetch_hashes_for_dataset(mock_datasets, dataset_id, mock_lexis_token)
        mock_get_hash.assert_not_called()

# Test hashing_utils logic (create_request and poll) via mocks on httpx
@pytest.mark.asyncio
async def test_create_hash_request_async():
    dataset_id = "ds1"
    path = "/file1"
    token = "tok"
    request_id = "req123"
    
    # We mock httpx.AsyncClient so that when instantiated it returns an AsyncMock
    with patch('httpx.AsyncClient') as MockClient:
        # The instance returned by AsyncClient()
        mock_client_instance = AsyncMock()
        MockClient.return_value = mock_client_instance
        
        # When used as context manager (async with ...), it should return itself
        mock_client_instance.__aenter__.return_value = mock_client_instance
        
        # Mock the response object
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"request_id": request_id}
        
        # client.get is async, so it returns the response when awaited
        mock_client_instance.get.return_value = mock_response
        
        # Test with implicit client creation
        res = await create_hash_request_async(dataset_id, path, token)
        assert res == request_id
