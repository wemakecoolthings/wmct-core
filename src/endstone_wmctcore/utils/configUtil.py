import json
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
while not (os.path.exists(os.path.join(current_dir, 'plugins')) and os.path.exists(os.path.join(current_dir, 'worlds'))):
    current_dir = os.path.dirname(current_dir)

CONFIG_PATH = os.path.join(current_dir, 'plugins', 'wmctcore-config.json')

def load_config():
    """Load or create a configuration file to enable/disable commands."""
    if not os.path.exists(CONFIG_PATH):
        default_config = {
            "commands": {} 
        }
        with open(CONFIG_PATH, "w") as config_file:
            json.dump(default_config, config_file, indent=4)

    with open(CONFIG_PATH, "r") as config_file:
        return json.load(config_file)

def save_config(config):
    """Save the current config state to disk."""
    with open(CONFIG_PATH, "w") as config_file:
        json.dump(config, config_file, indent=4)