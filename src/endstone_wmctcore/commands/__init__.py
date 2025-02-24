import importlib
import pkgutil
import os
import json
from collections import defaultdict
import endstone_wmctcore

CONFIG_PATH = os.path.join(os.path.dirname(endstone_wmctcore.__file__), '../../../../wmctcore-config.json')

# Global storage for preloaded commands
preloaded_commands = {}
moderation_commands = set() # MOD SYSTEM REQ
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
    global preloaded_commands, preloaded_permissions, preloaded_handlers, moderation_commands

    commands_base_path = os.path.join(os.path.dirname(endstone_wmctcore.__file__), 'commands')
    config = load_config()

    grouped_commands = defaultdict(list)

    print("[WMCT CORE] Registering commands...")

    # Recursively find all submodules
    for root, _, _ in os.walk(commands_base_path):
        rel_path = os.path.relpath(root, commands_base_path)
        package_path = rel_path.replace(os.sep, ".") if rel_path != "." else ""

        for _, module_name, _ in pkgutil.iter_modules([root]):
            module_import_path = f"endstone_wmctcore.commands{('.' + package_path) if package_path else ''}.{module_name}"
            module = importlib.import_module(module_import_path)

            if hasattr(module, 'command') and hasattr(module, 'handler'):
                for cmd, details in module.command.items():
                    # Ensure command exists in config, default to enabled
                    if cmd not in config["commands"]:
                        config["commands"][cmd] = {"enabled": True}

                    if config["commands"][cmd]["enabled"]:
                        preloaded_commands[cmd] = details
                        preloaded_handlers[cmd] = module.handler

                        # Check if the command belongs to "Moderation"
                        if package_path.lower() == "moderation":
                            moderation_commands.add(cmd)  # Add the main command
                            aliases = details.get("aliases", [])  # Get aliases if available
                            moderation_commands.update(aliases)  # Add aliases to the set

                        grouped_commands[package_path].append((cmd, details.get('description', 'No description')))
                    else:
                        grouped_commands[package_path].append((cmd, "Disabled by config"))

                if hasattr(module, 'permission'):
                    for perm, details in module.permission.items():
                        preloaded_permissions[perm] = details

    # Print grouped commands
    for category, commands in grouped_commands.items():
        print(f"\n[{category if category else 'Root'}]")
        for cmd, desc in commands:
            status = "✓" if "Disabled by config" not in desc else "✗"
            print(f"{status} {cmd} - {desc}")

    print("\n")
    save_config(config)

# Run preload automatically when this file is imported
preload_commands()

__all__ = [preloaded_commands, preloaded_permissions, preloaded_handlers, moderation_commands]
