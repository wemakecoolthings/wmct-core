from endstone.plugin import Plugin
from endstone_wmctcore.processors.commands import CommandProcessor

class WMCTPlugin(Plugin):
    api_version = "0.6"
    authors = ["PrimeStrat", "Cra-ZGuy", "trainer jeo"]

    commands = {}
    permissions = {}

    def __init__(self):
        super().__init__()
        self.command_processor = CommandProcessor()

    def on_load(self):
        self.register_commands()

    def register_commands(self):
        # Load commands and permissions dynamically
        self.command_processor.load_commands()

        # Register commands and permissions to the plugin instance
        self.commands, self.permissions = self.command_processor.register_command()

        print("Commands and permissions successfully registered!\n")
