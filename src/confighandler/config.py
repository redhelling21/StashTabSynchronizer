import yaml
import os
import sys

config_file_path = f"{os.path.dirname(sys.argv[0])}/config.yaml"

def loadConfig():
    if os.path.exists(config_file_path):
        with open(config_file_path, "r") as configYaml:
                config = yaml.unsafe_load(configYaml)
                configYaml.close()
        return config if config is not None else {}
    return {}

def dumpConfig(config):
      with open(config_file_path, "w") as configYaml:
            yaml.dump(config, configYaml, default_flow_style=False)
            configYaml.close()