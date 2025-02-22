import importlib
import pkgutil
import os
import endstone_wmctcore

# Global storage for preloaded commands
preloaded_commands = {}
preloaded_permissions = {}
preloaded_handlers = {}

def preload_commands():
    """Preload all command modules before WMCTPlugin is instantiated."""
    commands_path = os.path.join(os.path.dirname(endstone_wmctcore.__file__), 'commands')

    for _, module_name, _ in pkgutil.iter_modules([commands_path]):
        module = importlib.import_module(f"endstone_wmctcore.commands.{module_name}")

        if hasattr(module, 'command') and hasattr(module, 'handler'):
            for cmd, details in module.command.items():
                preloaded_commands[cmd] = details
                preloaded_handlers[cmd] = module.handler

            if hasattr(module, 'permission'):
                for perm, details in module.permission.items():
                    preloaded_permissions[perm] = details

# Run preload automatically when this file is imported
preload_commands()

__all__ = [preloaded_commands, preloaded_permissions]
