import yaml
from datetime import datetime

def datetime_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data.isoformat())

def api_token_representer(dumper, data):
    return dumper.represent_mapping("tag:yaml.org,2002:python/object:auth.token.APIToken", {
        "accessToken": data.accessToken,
        "expiresOn": data.expiresOn.isoformat(),
        "tokenType": data.tokenType,
        "scope": data.scope,
        "username": data.username,
        "sub": data.sub,
        "refreshToken": data.refreshToken,
    })