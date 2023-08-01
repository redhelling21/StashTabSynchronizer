import yaml
import os

config_file_path = "config.yaml"

def loadConfig():
    if os.path.exists(config_file_path):
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