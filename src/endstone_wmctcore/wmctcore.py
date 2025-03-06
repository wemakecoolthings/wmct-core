import traceback

from endstone import ColorFormat, Player
from endstone.plugin import Plugin
from endstone.command import Command, CommandSender

from endstone_wmctcore.commands import (
    preloaded_commands,
    preloaded_permissions,
    preloaded_handlers
)

from endstone_wmctcore.utils.dbUtil import UserDB
from endstone_wmctcore.utils.internalPermissionsUtil import get_permissions, PERMISSIONS
from endstone_wmctcore.utils.prefixUtil import errorLog

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

# EVENT IMPORTS
from endstone.event import event_handler, PlayerLoginEvent, PlayerJoinEvent, PlayerQuitEvent, ServerCommandEvent, PlayerCommandEvent, PlayerChatEvent, BlockBreakEvent
from endstone_wmctcore.events.chat_events import handle_chat_event
from endstone_wmctcore.events.command_processes import handle_command_preprocess, handle_server_command_preprocess
from endstone_wmctcore.events.player_connect import handle_login_event, handle_join_event, handle_leave_event

class WMCTPlugin(Plugin):
    api_version = "0.6"
    authors = ["PrimeStrat", "CraZ-Guy", "trainer jeo"]

    commands = preloaded_commands
    permissions = preloaded_permissions
    handlers = preloaded_handlers

    def __init__(self):
        super().__init__()

    # EVENT HANDLER
    @event_handler()
    def on_player_login(self, ev: PlayerLoginEvent):
        handle_login_event(self, ev)

    @event_handler()
    def on_player_join(self, ev: PlayerJoinEvent):
        handle_join_event(self, ev)

    @event_handler()
    def on_player_quit(self, ev: PlayerQuitEvent):
        handle_leave_event(self, ev)

    @event_handler()
    def on_player_command_preprocess(self, ev: PlayerCommandEvent) -> None:
        handle_command_preprocess(self, ev)

    @event_handler()
    def on_player_server_command_preprocess(self, ev: ServerCommandEvent) -> None:
        handle_server_command_preprocess(self, ev)

    @event_handler()
    def on_player_chat(self: "WMCTPlugin", ev: PlayerChatEvent):
        handle_chat_event(self, ev)

    def on_load(self):
        plugin_text()

    def on_enable(self):
        self.register_events(self)

        for player in self.server.online_players:
            self.reload_custom_perms(player)

    # PERMISSIONS HANDLER
    def reload_custom_perms(self, player: Player):
        # Update Internal DB
        db = UserDB("wmctcore_users.db")
        db.save_user(player)
        user = db.get_online_user(player.xuid)

        permissions = get_permissions(user.internal_rank)

        # Reset Permissions
        perms = self.permissions
        for p in perms:
            player.add_attachment(self, p, False)

        # Apply Perms
        if "*" in permissions:
            for perm in perms:
                player.add_attachment(self, perm, True)
        else:
            for perm in permissions:
                player.add_attachment(self, perm, True)

        # Remove Overwritten Permissions
        player.add_attachment(self, "endstone.command.ban", False)
        player.add_attachment(self, "endstone.command.banip", False)
        player.add_attachment(self, "endstone.command.unban", False)
        player.add_attachment(self, "endstone.command.unbanip", False)
        player.add_attachment(self, "endstone.command.banlist", False)

        player.update_commands()
        player.recalculate_permissions()

        db.close_connection()

    # COMMAND HANDLER
    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        """Handle incoming commands dynamically."""
        try:
            if command.name in self.handlers:
                if any("@" in arg for arg in args):
                    sender.send_message(f"{errorLog()}Invalid argument: @ symbols are not allowed for managed commands.")
                    return False
                else:
                    handler_func = self.handlers[command.name]  # Get the handler function
                    return handler_func(self, sender, args)  # Execute the handler
            else:
                sender.send_message(f"{errorLog()}Command '{command.name}' not found.")
                return False
        except Exception as e:
            error_message = (
                    f"{ColorFormat.RED}========\n"
                    f"{ColorFormat.GOLD}This command generated an error -> please report this on our GitHub and provide a copy of the error below!\n"
                    f"{ColorFormat.RED}========\n\n"
                    f"{ColorFormat.YELLOW}{e}\n\n"
                    + "\n".join(f"{ColorFormat.YELLOW}{line}" for line in traceback.format_exc().splitlines()) +
                    f"{ColorFormat.RESET}"
            )
            error_message_console = (
                    f"========\n"
                    f"This command generated an error -> please report this on our GitHub and provide a copy of the error below!\n"
                    f"========\n\n"
                    f"{e}\n\n"
                    + "\n".join(f"{line}" for line in traceback.format_exc().splitlines())
            )
            sender.send_message(error_message)

            if sender.name != "Server":
                print(error_message_console)

            return False