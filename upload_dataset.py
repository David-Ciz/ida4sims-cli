import argparse
from py4lexis.session import LexisSession
from py4lexis.lexis_irods import iRODS
import os

# Default values
default_access = 'project'
project = 'exa4mind_wp4'

parser = argparse.ArgumentParser(description='Upload a dataset to LEXIS')
parser.add_argument('title', type=str, help='Dataset')
parser.add_argument('directory', type=str, help='Local directory path to upload')
parser.add_argument('--access', type=str, default=default_access,
                    help='Access level for the dataset (e.g., public, private, project). Default: project')
args = parser.parse_args()

# Use the access level provided by the user or the default
access = args.access

# Generate token if it doesn't exist or regenerate if specified
def generate_token():
    print("Generating new token...")
    lexis_session = LexisSession(offline_access=True)
    offline_token = lexis_session.get_refresh_token()
    with open("offline_token.txt", "w") as text_file:
        text_file.write(offline_token)
    print("Token generated and saved to offline_token.txt")
    return offline_token

# Generate token if file doesn't exist
if not os.path.exists("offline_token.txt"):
    offline_token = generate_token()
else:
    with open("offline_token.txt", "r") as text_file:
        offline_token = text_file.read()

# Create session with the token
session = LexisSession(refresh_token=offline_token)
irods = iRODS(session=session,
              suppress_print=False)

response = irods.create_dataset(access=access,
                              project=project,
                              title=args.title)

print(response)
irods.upload_directory_to_dataset(local_directorypath=args.directory,
                                access=access,
                                project=project,
                                dataset_id=response["dataset_id"])