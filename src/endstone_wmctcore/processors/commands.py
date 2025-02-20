import importlib
import pkgutil
import src.endstone_wmctcore.commands as commands_module

class CommandProcessor:
    def __init__(self):
        self.commands = {}
        self.permissions = {}

    def load_commands(self):
        """Dynamically load all command modules and extract command definitions."""
        package_path = commands_module.__path__

        for _, module_name, _ in pkgutil.iter_modules(package_path):
            module = importlib.import_module(f"src.endstone_wmctcore.commands.{module_name}")

            if hasattr(module, "command") and hasattr(module, "permission"):
                self.commands.update(module.command)
                self.permissions.update(module.permission)

    def register_command(self, plugin_instance):
        """Register loaded commands to the plugin."""
        for cmd, details in self.commands.items():
            plugin_instance.register_command(cmd, details)

        for perm, details in self.permissions.items():
            plugin_instance.register_permission(perm, details)
