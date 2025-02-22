from endstone.event import event_handler, EventPriority
from endstone.plugin import Plugin
from endstone.command import Command, CommandSender
from endstone_wmctcore.commands import (
    preloaded_commands,
    preloaded_permissions,
    preloaded_handlers
)

from endstone_wmctcore.utils.prefixUtil import errorLog

class WMCTPlugin(Plugin):
    api_version = "0.6"
    authors = ["PrimeStrat", "CraZ-Guy", "trainer jeo"]

    commands = preloaded_commands
    permissions = preloaded_permissions
    handlers = preloaded_handlers

    def __init__(self):
        super().__init__()
        self.check_commands()

    def check_commands(self):
        """Preload commands at the earliest possible moment."""
        for cmd, details in self.commands.items():
            print(f"✓ {cmd} - {details.get('description', 'No description')}")

    @event_handler(priority=EventPriority.HIGHEST)
    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        """Handle incoming commands dynamically."""
        try:
            if command.name in self.handlers:
                handler_func = self.handlers[command.name]  # Get the handler function
                return handler_func(sender, args)  # Execute the handler
            else:
                sender.send_message(f"Command '{command.name}' not found.")
                return False
        except Exception as e:
            sender.send_message(f"\n========This command generated an error -> please report this on our GitHub!\n========\n\n{errorLog()}{e}\n\n========")
            return False

