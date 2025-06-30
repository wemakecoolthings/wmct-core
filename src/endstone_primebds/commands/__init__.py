import importlib
import json
import pkgutil
import os
import time

import endstone_primebds

from endstone_primebds.utils.configUtil import load_config, save_config
from collections import defaultdict

# Global storage for preloaded commands
moderation_commands = set() # MOD SYSTEM REQ
preloaded_commands = {}
preloaded_permissions = {}
preloaded_handlers = {}

def preload_settings():
    """Preload all plugin settings with defaults if missing."""
    config = load_config()

    # Define default modules and settings
    default_modules = {
        "discord_logging": {
            "embed": {
                "color": 781919,
                "title": "Logger"
            },
            "commands": {
                "enabled": False,
                "webhook": ""
            },
            "moderation": {
                "enabled": False,
                "webhook": ""
            },
            "chat": {
                "enabled": False,
                "webhook": ""
            },
            "griefing": {
                "enabled": False,
                "webhook": ""
            }
        },
        "game_logging": {
            "custom_tags": [],
            "moderation": {
                "enabled": True
            },
            "commands": {
                "enabled": False
            }
        },
        "spectator_check": {
            "check_gamemode": True,
            "check_tags": False,
            "allow_tags": [],
            "ignore_tags": []
        },
        "me_crasher_patch": {
            "enabled": True,
            "ban": False
        },
        "grieflog": {
            "enabled": False
        },
        "grieflog_storage_auto_delete": {
            "enabled": False,
            "removal_time_in_seconds": 1209600
        },
        "check_prolonged_death_screen": {
            "enabled": False,
            "kick": False,
            "time_in_seconds": 10
        },
        "check_afk": {
            "enabled": False,
            "kick": False,
            "time_in_seconds": 180
        },
        "combat": {
            "hit_cooldown_in_seconds": 0.0,
            "base_damage": 1.0,
            "horizontal_knockback_modifier": 1.0,
            "vertical_knockback_modifier": 1.0,
            "horizontal_sprint_knockback_modifier": 0.0,
            "vertical_sprint_knockback_modifier": 0.0,
            "tag_modifiers": {
                "example_tag": {
                    "hit_cooldown_in_seconds": 2,
                    "base_damage": 5,
                    "horizontal_knockback_modifier": 2,
                    "vertical_knockback_modifier":2,
                    "horizontal_sprint_knockback_modifier": 3,
                    "vertical_sprint_knockback_modifier": 3
                }
            }
        },
        "allowlist": {
            "profile": "default",
            "WARNING": "⚠️ DO NOT EDIT 'profile' AS IT CAN RESULT IN UNEXPECTED BEHAVIOR",
        }
    }

    # Ensure 'modules' key exists in config
    if "modules" not in config:
        config["modules"] = {}

    # Add missing modules with default settings
    for module, settings in default_modules.items():
        if module not in config["modules"]:
            config["modules"][module] = settings

    save_config(config)

def preload_commands():
    """Preload all command modules before PrimeBDS is instantiated, respecting the config."""
    global preloaded_commands, preloaded_permissions, preloaded_handlers, moderation_commands

    commands_base_path = os.path.join(os.path.dirname(endstone_primebds.__file__), 'commands')
    config = load_config()

    grouped_commands = defaultdict(list)
    found_commands = set()  # Track commands that are found

    print("[PrimeBDS] Registering commands...")

    # Recursively find all submodules
    for root, _, _ in os.walk(commands_base_path):
        rel_path = os.path.relpath(root, commands_base_path)
        package_path = rel_path.replace(os.sep, ".") if rel_path != "." else ""

        for _, module_name, _ in pkgutil.iter_modules([root]):
            module_import_path = f"endstone_primebds.commands{('.' + package_path) if package_path else ''}.{module_name}"
            module = importlib.import_module(module_import_path)

            if hasattr(module, 'command') and hasattr(module, 'handler'):
                for cmd, details in module.command.items():
                    found_commands.add(cmd)  # Mark command as found

                    # Ensure command exists in config, default to enabled
                    if cmd not in config["commands"]:
                        config["commands"][cmd] = {"enabled": True}

                    if config["commands"][cmd]["enabled"]:
                        preloaded_commands[cmd] = details
                        preloaded_handlers[cmd] = module.handler

                        # Check if the command belongs to "Moderation"
                        if package_path.lower() == "moderation":
                            moderation_commands.add(cmd)  # Add main command
                            aliases = details.get("aliases", [])  # Get aliases if available
                            moderation_commands.update(aliases)  # Add aliases to the set

                        grouped_commands[package_path].append((cmd, details.get('description', 'No description')))
                    else:
                        grouped_commands[package_path].append((cmd, "Disabled by config"))

                if hasattr(module, 'permission'):
                    for perm, details in module.permission.items():
                        preloaded_permissions[perm] = details

    # Remove commands that are no longer found
    removed_commands = set(config["commands"].keys()) - found_commands
    for cmd in removed_commands:
        del config["commands"][cmd]

    # Print grouped commands
    for category, commands in grouped_commands.items():
        if category or commands:  # Only print "Root" if it has commands
            clean_category = category.replace("_", " ") if category else "Root"
            print(f"\n[{clean_category}]")
            for cmd, desc in commands:
                status = "✓" if "Disabled by config" not in desc else "✗"
                print(f"{status} {cmd} - {desc}")

    # Print removed commands
    if removed_commands:
        print("\n[PrimeBDS] Removed missing commands:")
        for cmd in removed_commands:
            print(f"✗ {cmd}")

    print("\n")
    save_config(config)

# Run preload automatically when this file is imported
preload_settings()
preload_commands()

__all__ = [preloaded_commands, preloaded_permissions, preloaded_handlers, moderation_commands]
