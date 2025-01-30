from py4lexis.core.lexis_irods import iRODS
from py4lexis.core.session import LexisSessionOffline



# with open("refresh_token.txt", "r") as text_file:
#     access_token = text_file.read()
from py4lexis.session import LexisSession
lexis_session = LexisSession(offline_access=True)
offline_token = lexis_session.get_refresh_token()
# lexis_session.refresh_token()
with open("offline_token.txt", "w") as text_file:
     text_file.write(offline_token)



# # lexis_session = LexisSessionOffline(refresh_token=lexis_session)
# irods = iRODS(session=lexis_session,
#                     suppress_print=False)
# dataset_id = "3cb89562-0211-11ef-a690-0242c0a8f009"
# # project_id = "proj9d2a3a1adb900e37d0a881b3f219ca8e"
# #irods.download_dataset_as_directory(access='project', project='exa4mind_wp4', internal_id=dataset_id, local_directorypath='.')
#
# irods.create_dataset_and_upload_directory(access='project', project='exa4mind_wp4', local_directorypath='test.txt')
#
#
# #
# #
# # lexis_session = LexisSession()
# # lexis_refresh_token = lexis_session.get_refresh_token()
# with open("refresh_token.txt", "w") as text_file:
#     text_file.write(access_token)
#
# LexisSession.get_offline_token