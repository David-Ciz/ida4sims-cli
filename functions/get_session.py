from py4lexis.session import LexisSession

def get_session():
    print('Creating new session...')
    lexis_session = LexisSession(offline_access=False)
        
    return lexis_session