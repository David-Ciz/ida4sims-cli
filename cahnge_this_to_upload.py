from py4lexis.core.lexis_irods import iRODS
from py4lexis.core.session import LexisSessionOffline, LexisSession

with open("refresh_token.txt", "r") as text_file:
    access_token = text_file.read()

lexis_session = LexisSession()
irods = iRODS(session=lexis_session,
              suppress_print=False)
local_dataset_directory_path = '../../airflow'
irods.download_dataset_as_directory(access='project', project='exa4mind_wp4', internal_id="e3006346-8196-11ef-83f2-0242c0a87004",
                                    local_directorypath=local_dataset_directory_path)