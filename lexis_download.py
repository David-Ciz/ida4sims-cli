import os
os.environ["PY4LEXIS_RERAISE_EXCEPTIONS"] = "True"

from py4lexis.core.lexis_irods import iRODS
from py4lexis.core.session import LexisSession
session = LexisSession(reraise_exceptions=True)

irods = iRODS(session=session, suppress_print=False, reraise_exceptions=True)
directory_path = "."
result = irods.download_dataset_as_directory(
        
        dataset_id="eb89af42-1131-11f0-96b7-0242ac140003",
        local_directorypath=str(directory_path),
    )