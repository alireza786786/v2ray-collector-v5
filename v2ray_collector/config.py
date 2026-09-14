import os
import yaml

def load_config(path="config.yaml"):
    """
    Loads configuration settings from the YAML file in the root directory.
    """
    config = {}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            user_cfg = yaml.safe_load(f)
            if user_cfg:
                config.update(user_cfg)
    return config
