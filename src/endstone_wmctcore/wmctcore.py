from endstone._internal.endstone_python import Plugin
from .processors.commands import CommandProcessor

class WMCTPlugin(Plugin):
    api_version = "0.6.0"
    authors = ["PrimeStrat", "Cra-ZGuy", "trainer jeo"]

    def __init__(self):
        super().__init__()
        # self.command_processor = CommandProcessor()
        # self.command_processor.load_commands()
        # self.command_processor.register_command(self)

