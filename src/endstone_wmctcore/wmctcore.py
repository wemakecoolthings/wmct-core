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

class WMCTPlugin(Plugin):
    api_version = "0.6"
    authors = ["PrimeStrat", "CraZ-Guy", "trainer jeo"]

    commands = preloaded_commands
    permissions = preloaded_permissions
    handlers = preloaded_handlers

    def __init__(self):
        super().__init__()
        self.check_commands()
        self.user_db = UserDB("wmctcore_users.db")

    # COMMAND HANDLER
    @event_handler(priority=EventPriority.HIGHEST)
    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        """Handle incoming commands dynamically."""
        try:
            if command.name in self.handlers:
                if any("@" in arg for arg in args):
                    sender.send_message(f"{errorLog()}Invalid argument: @ symbols are not allowed.")
                    return False
                else:
                    handler_func = self.handlers[command.name]  # Get the handler function
                    return handler_func(sender, args)  # Execute the handler
            else:
                sender.send_message(f"Command '{command.name}' not found.")
                return False
        except Exception as e:
            sender.send_message(f"\n========This command generated an error -> please report this on our GitHub!\n========\n\n{errorLog()}{e}\n\n========")
            return False

