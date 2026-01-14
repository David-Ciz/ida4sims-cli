import asyncio
import time
import hashlib
from typing import Optional
from pathlib import Path

import httpx
from py4lexis.core.session import LexisSession

BASE_URL = "https://api.lexis.tech/api/ddiapi/v2"


import base64

def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA256 hash of a local file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    digest_b64 = base64.b64encode(sha256_hash.digest()).decode('utf-8')
    return f"sha2:{digest_b64}"



async def create_hash_request_async(dataset_id: str, path: str, lexis_token: str, client: Optional[httpx.AsyncClient] = None) -> Optional[str]:
    """
    Call `/staging/hash` and return the `request_id` on success.
    """
    close_client = False
    if client is None:
        client = httpx.AsyncClient(timeout=10.0)
        close_client = True

    try:
        headers = {"Authorization": f"Bearer {lexis_token}", "Accept": "application/json"}
        params = {"dataset_id": dataset_id, "path": path}
        resp = await client.get(f"{BASE_URL}/staging/hash", headers=headers, params=params)
        if resp.status_code in (200, 202):
            data = resp.json()
            return data.get("request_id") or data.get("id")
        return None
    finally:
        if close_client:
            await client.aclose()


async def poll_status_async(request_id: str, lexis_token: str, interval: float = 1.0, timeout: float = 30.0, client: Optional[httpx.AsyncClient] = None) -> Optional[dict]:
    """
    Poll `/staging/status/{request_id}` until status is completed, failed, or timeout.
    Returns the JSON body when finished or on failure; None on timeout / network error.
    """
    close_client = False
    if client is None:
        client = httpx.AsyncClient(timeout=10.0)
        close_client = True

    try:
        headers = {"Authorization": f"Bearer {lexis_token}", "Accept": "application/json"}
        url = f"{BASE_URL}/staging/status/{request_id}"
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                status = (data.get("status") or data.get("state") or "").upper()
                if status in ("COMPLETED", "DONE", "SUCCESS"):
                    return data
                if status in ("FAILED", "ERROR"):
                    return data
                # still pending -> wait and retry
            elif resp.status_code in (202, 204):
                # accepted / no content -> still processing
                pass
            else:
                # unexpected http status: return server response for inspection
                try:
                    return resp.json()
                except Exception:
                    return {"http_status": resp.status_code, "text": resp.text}
            await asyncio.sleep(interval)
        return None
    finally:
        if close_client:
            await client.aclose()


async def get_irods_file_hash_via_poll_async(dataset_id: str, path: str, lexis_token: str, interval: float = 1.0, timeout: float = 30.0) -> Optional[dict]:
    """
    Convenience: create the hash job, then poll until finished and return final JSON.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        request_id = await create_hash_request_async(dataset_id, path, lexis_token, client=client)
        if not request_id:
            return None
        return await poll_status_async(request_id, lexis_token, interval=interval, timeout=timeout, client=client)
