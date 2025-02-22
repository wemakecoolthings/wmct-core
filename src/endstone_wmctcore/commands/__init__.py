import importlib
import pkgutil
import os
import json
import endstone_wmctcore

CONFIG_PATH = os.path.join(os.path.dirname(endstone_wmctcore.__file__), '../../../../wmctcore-config.json')

# Global storage for preloaded commands
preloaded_commands = {}
preloaded_permissions = {}
preloaded_handlers = {}

def load_config():
    """Load or create a configuration file to enable/disable commands."""
    if not os.path.exists(CONFIG_PATH):
        print("[CONFIG] No config found, generating default config...\n")
        default_config = {
            "commands": {}  # Will be populated dynamically
        }
        with open(CONFIG_PATH, "w") as config_file:
            json.dump(default_config, config_file, indent=4)
    else:
        print("[CONFIG] Loading existing config...\n")

    with open(CONFIG_PATH, "r") as config_file:
        return json.load(config_file)


def save_config(config):
    """Save the current config state to disk."""
    with open(CONFIG_PATH, "w") as config_file:
        json.dump(config, config_file, indent=4)


def preload_commands():
    """Preload all command modules before WMCTPlugin is instantiated, respecting the config."""
    global preloaded_commands, preloaded_permissions, preloaded_handlers

    commands_path = os.path.join(os.path.dirname(endstone_wmctcore.__file__), 'commands')
    config = load_config()

    print("[COMMANDS] Registering...")
    for _, module_name, _ in pkgutil.iter_modules([commands_path]):
        module = importlib.import_module(f"endstone_wmctcore.commands.{module_name}")

        if hasattr(module, 'command') and hasattr(module, 'handler'):
            for cmd, details in module.command.items():
                # Ensure command exists in config, default to enabled
                if cmd not in config["commands"]:
                    config["commands"][cmd] = {"enabled": True}

                if config["commands"][cmd]["enabled"]:
                    preloaded_commands[cmd] = details
                    preloaded_handlers[cmd] = module.handler
                    print(f"✓ {cmd} - {details.get('description', 'No description')}")
                else:
                    print(f"✗ {cmd} - Disabled by config")

            if hasattr(module, 'permission'):
                for perm, details in module.permission.items():
                    preloaded_permissions[perm] = details

    # Save updated config if new commands were added
    save_config(config)

# Run preload automatically when this file is imported
preload_commands()

__all__ = [preloaded_commands, preloaded_permissions, preloaded_handlers]
