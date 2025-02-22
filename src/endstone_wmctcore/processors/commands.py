import importlib
import pkgutil
import endstone_wmctcore.commands as commands_module
from endstone_wmctcore import wmctcore

class CommandProcessor:
    def __init__(self):
        super().__init__()
        self.commands = {}
        self.permissions = {}

    def load_commands(self):
        """Dynamically load all command modules and extract command definitions."""
        package_path = commands_module.__path__

        for _, module_name, _ in pkgutil.iter_modules(package_path):

            module = importlib.import_module(f"endstone_wmctcore.commands.{module_name}")

            if hasattr(module, "command") and hasattr(module, "permission"):
                self.commands.update(module.command)
                self.permissions.update(module.permission)

    def register_command(self):
        """Register loaded commands to the plugin and print them neatly."""
        print("\n=== Registered Commands ===")
        for cmd, details in self.commands.items():
            print(f"✓ {cmd} - {details.get('description', 'No description')}")

        return self.commands, self.permissions