#!/usr/bin/env python3
"""
Script to get all datasets using py4lexis CLI with stored refresh token.
"""

import subprocess
import sys
import keyring
from py4lexis.session import LexisSession, LexisSessionToken
from ida4sims_cli.helpers.default_data import KEYRING_SERVICE_NAME, KEYRING_USERNAME

def get_refresh_token():
    stored_token = keyring.get_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME)
    print("--- Attempting to get LEXIS refresh token ---")
    print(f"Checking for stored token under service='{KEYRING_SERVICE_NAME}', username='{KEYRING_USERNAME}'")
    print("Stored token found:", "Yes" if stored_token else "No")

    if stored_token:
        print("Attempting to refresh session using stored token...")
        try:
            session_attempt = LexisSessionToken(refresh_token=stored_token)
            if session_attempt:
                try:
                    refreshed_token = session_attempt.get_refresh_token()
                    if refreshed_token:
                        print("Token refreshed successfully.")
                        keyring.set_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME, refreshed_token)
                        return refreshed_token
                    else:
                        print("Failed to refresh token.")
                except Exception as e:
                    print(f"Error during token refresh: {e}")
            else:
                print("Stored token did not result in a valid session.")
        except Exception as e:
            print(f"Error initializing session with stored token: {e}")
        # If stored token failed, delete it
        keyring.delete_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME)
        print("Deleted invalid stored token.")

    print("Performing new login...")
    try:
        lexis_session = LexisSession(offline_access=True)
        if lexis_session:
            print("New login successful.")
            new_token = lexis_session.get_refresh_token()
            if new_token:
                print("New token obtained.")
                keyring.set_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME, new_token)
                return new_token
            else:
                print("Failed to obtain new token.")
        else:
            print("New login failed.")
    except Exception as e:
        print(f"Error during new login: {e}")

    return None

def main():
    refresh_token = get_refresh_token()
    if not refresh_token:
        print("ERROR: Failed to obtain refresh token.", file=sys.stderr)
        sys.exit(1)

    # Command to run
    cmd = [
        "python", "-m", "py4lexis.cli.datasets", "get-all-datasets",
        "--filter-project", "exa4mind_wp4",
        "--filter-access", "project",
        "--users-datasets",
        "--refresh-token", refresh_token
    ]

    # Run the command
    try:
        result = subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed with return code {e.returncode}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()