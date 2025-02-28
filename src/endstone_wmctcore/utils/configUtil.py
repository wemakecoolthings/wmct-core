import json
import endstone_wmctcore

CONFIG_PATH = os.path.join(os.path.dirname(endstone_wmctcore.__file__), '../../../../wmctcore-config.json')

def load_config():
    """Load or create a configuration file to enable/disable commands."""
    if not os.path.exists(CONFIG_PATH):
        default_config = {
            "commands": {}  # Will be populated dynamically
        }
        with open(CONFIG_PATH, "w") as config_file:
            json.dump(default_config, config_file, indent=4)

    with open(CONFIG_PATH, "r") as config_file:
        return json.load(config_file)

def save_config(config):
    """Save the current config state to disk."""
    with open(CONFIG_PATH, "w") as config_file:
        json.dump(config, config_file, indent=4)