from endstone import ColorFormat
from endstone.event import event_handler, EventPriority
from endstone.plugin import Plugin
from endstone.command import Command, CommandSender
from endstone_wmctcore.commands import (
    preloaded_commands,
    preloaded_permissions,
    preloaded_handlers
)

from endstone_wmctcore.utils.prefixUtil import errorLog
from endstone_wmctcore.utils.dbUtil import UserDB

def plugin_text():
    print(
        """
 _ _ _ _____ _____ _____ 
| | | |     |     |_   _|
| | | | | | |   --| | |  
|_____|_|_|_|_____| |_|                          

WMCT Core Loaded!
        """
    )

class WMCTPlugin(Plugin):
    api_version = "0.6"
    authors = ["PrimeStrat", "CraZ-Guy", "trainer jeo"]

    commands = preloaded_commands
    permissions = preloaded_permissions
    handlers = preloaded_handlers

    def __init__(self):
        super().__init__()
        self.user_db = None

    @event_handler()
    def on_load(self):
        plugin_text()
        
    @event_handler()
    def on_enable(self):
        self.user_db = UserDB("wmctcore_users.db")

    @event_handler()
    def on_disable(self):
        self.user_db.close_connection()

    # COMMAND HANDLER
    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        """Handle incoming commands dynamically."""
        try:
            if command.name in self.handlers:
                if any("@" in arg for arg in args):
                    sender.send_message(f"{errorLog()}Invalid argument: @ symbols are not allowed.")
                    return False
                else:
                    handler_func = self.handlers[command.name]  # Get the handler function
                    return handler_func(self, sender, args)  # Execute the handler
            else:
                sender.send_message(f"Command '{command.name}' not found.")
                return False
        except Exception as e:
            sender.send_message(f"\n========\nThis command generated an error -> please report this on our GitHub!\n========\n\n{errorLog()}{e}\n\n{ColorFormat.RESET}========")
            return False

