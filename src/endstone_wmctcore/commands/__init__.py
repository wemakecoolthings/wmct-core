import importlib
import pkgutil
import os
import endstone_wmctcore

from endstone_wmctcore.utils.configUtil import load_config, save_config
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
            "commands": {"enabled": False, "webhook": ""},
            "moderation": {"enabled": False, "webhook": ""},
            "chat": {"enabled": False, "webhook": ""},
            "griefing": {"enabled": False, "webhook": ""}
        },
        "game_logging": {
            "custom_tags": [],
            "moderation": {"enabled": True},
            "commands": {"enabled": False}
        },
        "spectator_check": {"check_gamemode": True, "check_tags": False, "allow_tags": [], "ignore_tags": []},
        "custom_combat": {"enabled": False, "kb_delay": 10, "hkb_mult": 1, "vkb_mult": 1, "sprint_mult": 1},
        "me_crasher_patch": {"enabled": True, "ban": False},
        "grieflog_storage_auto_delete": {"enabled": True, "removal_time_in_seconds": 1209600},
        "check_prolonged_death_screen": {"enabled": True},
        "check_afk": {"enabeled": True}
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
        if category or commands:  # Only print "Root" if it has commands
            print(f"\n[{category if category else 'Root'}]")
            for cmd, desc in commands:
                status = "✓" if "Disabled by config" not in desc else "✗"
                print(f"{status} {cmd} - {desc}")

    print("\n")
    save_config(config)

# Run preload automatically when this file is imported
preload_settings()
preload_commands()

__all__ = [preloaded_commands, preloaded_permissions, preloaded_handlers, moderation_commands]
