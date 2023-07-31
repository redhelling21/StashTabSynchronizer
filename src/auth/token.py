from datetime import datetime, timedelta
from . import oauth

class APIToken:
    _instance = None

    accessToken = None
    expiresOn = datetime.min
    tokenType = None
    scope = None
    username = None
    sub = None
    refreshToken = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)

        return cls._instance
    
    def isExpired(cls):
        return cls.expiresOn < datetime.now()
    
    def updateToken(cls, newToken):
        cls.accessToken = newToken["access_token"]
        cls.expiresOn = datetime.now() + timedelta(seconds=newToken["expires_in"])
        cls.tokenType = newToken["token_type"]
        cls.scope = newToken["scope"]
        cls.username = newToken["username"]
        cls.sub = newToken["sub"]
        cls.refreshToken = newToken["refresh_token"]

def get_token():
    token = APIToken()
    if(not token.isExpired()):
        return token
    newToken = oauth.oauth_process()
    token.updateToken(newToken)
    return token