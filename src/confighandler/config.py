import yaml
import os
from datetime import datetime
from . import representers
from auth import token

yaml.add_representer(datetime, representers.datetime_representer)
yaml.add_constructor("tag:yaml.org,2002:python/object:auth.token.APIToken", token.APIToken.api_token_constructor)
yaml.add_representer(token.APIToken, representers.api_token_representer)

config_file_path = "config.yaml"

def loadConfig():
    if os.path.exists(config_file_path):
        print("Reading config file...")
        with open(config_file_path, "r") as configYaml:
                config = yaml.unsafe_load(configYaml)
                configYaml.close()
        return config if config is not None else {} 
    with open(config_file_path, "w"):
        print("Creating config file...")
    return {}

def dumpConfig(config):
      with open(config_file_path, "w") as configYaml:
            yaml.dump(config, configYaml, default_flow_style=False)
            configYaml.close()