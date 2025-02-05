from py4lexis.session import LexisSession, LexisSessionOffline
import os
from default_data import OFFLINE_TOKEN_FILE_NAME

def get_offline_session():
    print("Checking for refresh token... (get_token)")
    if os.path.isfile(OFFLINE_TOKEN_FILE_NAME):
        print("Found refresh token.")
        try:
            with open(OFFLINE_TOKEN_FILE_NAME, "r") as text_file:
                offline_token = text_file.read()

            try:
                offline_session = LexisSessionOffline(refresh_token=offline_token)
                print('Check: Token validated successfully.')
                return offline_session 

            except Exception as logout_exception:
                print(f"Logout failed, indicating an invalid token: {logout_exception}")

        except Exception as e:
            print(f"Error using existing token: {e}")
            if os.path.isfile(OFFLINE_TOKEN_FILE_NAME):
                try:
                    os.remove(OFFLINE_TOKEN_FILE_NAME)
                    print("Invalid token file deleted successfully.")
                except PermissionError as pe:
                    print(f"Error deleting token file: {pe}")
                    print("This usually means the file is still in use. Ensure no other processes are using the token.")
                    raise 

            return get_offline_session() 

    else:
        print("No refresh token found. Generating new token...")
        lexis_session = LexisSession(offline_access=True)
        print("Generating new token.")
        offline_token = lexis_session.get_offline_token()
        offline_session = LexisSessionOffline(refresh_token=offline_token)
        with open(OFFLINE_TOKEN_FILE_NAME, "w") as text_file:
            text_file.write(offline_token)

        return offline_session