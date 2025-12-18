import keyring
from py4lexis.session import LexisSession, LexisSessionToken
from ida4sims_cli.helpers.default_data import KEYRING_SERVICE_NAME, KEYRING_USERNAME


stored_token = keyring.get_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME)

### IN CASE OF TOKEN PROBLEM UNCOMMENT THIS ROW BELOW   
#stored_token=False

class LexisAuthManager:
    offline_lexis_session = None

    def login(self):
        print("--- Attempting LEXIS Login/Session Creation ---")
        print(f"Checking for stored token under service='{KEYRING_SERVICE_NAME}', username='{KEYRING_USERNAME}'")
        print("Stored token found:", "Yes" if stored_token else "No")

        self.offline_lexis_session = None

        if stored_token:
            print("Attempting to create session using stored token (may be refreshed)...")
            try:
                session_attempt = LexisSessionToken(refresh_token=stored_token)

                if session_attempt:
                    print("Session created successfully using stored/refreshed token.")
                    self.offline_lexis_session = session_attempt
                else:
                    print("Stored token did not result in a valid session (invalid/expired?).")

            except Exception as e:
                print(f"Error initializing session with stored token: {e}")
                print("Proceeding to perform a new login.")
                self.offline_lexis_session = None

        if self.offline_lexis_session is None:
            if not stored_token:
                print(f"No valid token found for '{KEYRING_SERVICE_NAME}'. Performing new login...")
            else:
                 print("Stored token failed. Performing new login...")

            try:
                lexis_session = LexisSession(offline_access=True)

                if lexis_session:
                    print("New login successful.")
                    new_offline_token = lexis_session.get_refresh_token()

                    if new_offline_token:
                        print("New offline token obtained.")
                        keyring.set_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME, new_offline_token)
                        print(f"Stored new offline token for '{KEYRING_SERVICE_NAME}'.")

                        self.offline_lexis_session = LexisSessionToken(refresh_token=new_offline_token)
                        print("Offline session created with new token.")
                    else:
                        print("Warning: Login succeeded, but failed to retrieve an offline token to store.")
                        self.offline_lexis_session = None
                else:
                    print("Error: New login failed or session could not be authenticated.")
                    self.offline_lexis_session = None

            except Exception as e:
                print(f"An unexpected error occurred during new login: {e}")
                self.offline_lexis_session = None

        if self.offline_lexis_session:
            print("--- LEXIS Login/Session Creation Successful ---")
        else:
            print("--- LEXIS Login/Session Creation Failed ---")

        return self.offline_lexis_session
    
    def logout (self):
        self.offline_lexis_session = LexisSessionToken(refresh_token=stored_token)
        
        if self.offline_lexis_session:
            print('Logging out...')
            self.offline_lexis_session.logout()
            keyring.delete_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME)
            print(f"Deleted stored token for '{KEYRING_SERVICE_NAME}'.")
            print('Logged out successfully.')
        else:
            print('No session to log out from.')
        print('------------------------Logout completed-------------------------')
        return True




