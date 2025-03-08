import json
import os
import endstone_wmctcore


current_dir = os.path.dirname(os.path.abspath(__file__))
for _ in range(4):
    current_dir = os.path.dirname(current_dir)

CONFIG_PATH = os.path.join(current_dir, 'wmctcore-config.json')

def load_config():
    """Load or create a configuration file to enable/disable commands."""
    if not os.path.exists(CONFIG_PATH):
        default_config = {
            "commands": {}  # Will be populated dynamically
        }
        with open(CONFIG_PATH, "w") as config_file:
            json.dump(default_config, config_file, indent=4)

    with open(CONFIG_PATH, "r") as config_file:
        # Log in the console where the config is loaded from
        print(f"[WMCT CORE] [DEBUG] Loaded config from {CONFIG_PATH}")
        return json.load(config_file)

def save_config(config):
    """Save the current config state to disk."""
    with open(CONFIG_PATH, "w") as config_file:
        # Log in the console  where the config saved
        print(f"[WMCT CORE] [DEBUG] Saved config to {CONFIG_PATH}")
        json.dump(config, config_file, indent=4)