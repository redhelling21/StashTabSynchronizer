from datetime import datetime, timedelta
from . import oauth
from confighandler import config as cfg

class APIToken:
    _instance = None

    def __init_once(self):
        conf = cfg.loadConfig()
        if conf is not None and "token" in conf:
            yamlToken = conf["token"] # Trigger the constructor
            self.updateTokenWithYaml(yamlToken)
            print("Loaded token from config")
        else:
            self.accessToken = None
            self.expiresOn = datetime.min
            self.tokenType = None
            self.scope = None
            self.username = None
            self.sub = None
            self.refreshToken = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(APIToken, cls).__new__(cls)
            cls._instance.__init_once()
        return cls._instance
    
    def isExpired(self):
        return self.expiresOn < datetime.now()

    def updateTokenWithYaml(self, newToken):
        self.accessToken = newToken["accessToken"]
        self.expiresOn = newToken["expiresOn"]
        self.tokenType = newToken["tokenType"]
        self.scope = newToken["scope"]
        self.username = newToken["username"]
        self.sub = newToken["sub"]
        self.refreshToken = newToken["refreshToken"]

    def updateTokenWithJson(self, newToken):
        self.accessToken = newToken["access_token"]
        self.expiresOn = datetime.now() + timedelta(seconds=newToken["expires_in"])
        self.tokenType = newToken["token_type"]
        self.scope = newToken["scope"]
        self.username = newToken["username"]
        self.sub = newToken["sub"]
        self.refreshToken = newToken["refresh_token"]
        conf = cfg.loadConfig()
        conf["token"] = vars(self)
        cfg.dumpConfig(conf)
        print("Saved token in config")

def get_token():
    token = APIToken()
    if(not token.isExpired()):
        return token
    newToken = oauth.oauth_process()
    token.updateTokenWithJson(newToken)
    return token