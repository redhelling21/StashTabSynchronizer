from datetime import datetime, timedelta
from . import oauth
import yaml
class APIToken:
    _instance = None

    def __init__(self):
        conf = cfg.loadConfig()
        if conf is not None and "token" in conf:
            yamlToken = conf["token"] # Trigger the constructor
            print("Loaded token from config")
            self.updateTokenWithYaml(yamlToken)
            print("Loaded token :", self.accessToken)
        else:
            self.accessToken = None
            self.expiresOn = datetime.min
            self.tokenType = None
            self.scope = None
            self.username = None
            self.sub = None
            self.refreshToken = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(APIToken, cls).__new__(cls)
        return cls._instance
    
    def isExpired(cls):
        return cls.expiresOn < datetime.now()
    
    def api_token_constructor(loader, node):
        fields = loader.construct_mapping(node)
        token = APIToken()
        token.accessToken = fields.get("accessToken")
        token.expiresOn = datetime.fromisoformat(fields.get("expiresOn"))
        token.tokenType = fields.get("tokenType")
        token.scope = fields.get("scope")
        token.username = fields.get("username")
        token.sub = fields.get("sub")
        token.refreshToken = fields.get("refreshToken")
        return token

    def updateTokenWithYaml(self, newToken):
        self.accessToken = newToken["accessToken"]
        self.expiresOn = datetime.strptime(newToken["expiresOn"], "%Y-%m-%dT%H:%M:%S.%f")
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

from confighandler import config as cfg