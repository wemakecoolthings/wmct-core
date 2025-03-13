import os
import time
import traceback
from endstone import ColorFormat, Player
from endstone.plugin import Plugin
from endstone.command import Command, CommandSender

from endstone_wmctcore.commands import (
    preloaded_commands,
    preloaded_permissions,
    preloaded_handlers
)

from endstone_wmctcore.events.intervalChecks import interval_function, stop_interval
from endstone_wmctcore.commands.Server_Management.monitor import clear_all_intervals
from endstone_wmctcore.utils.configUtil import load_config

from endstone_wmctcore.utils.dbUtil import UserDB, GriefLog
from endstone_wmctcore.utils.internalPermissionsUtil import get_permissions
from endstone_wmctcore.utils.prefixUtil import errorLog, infoLog


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
from endstone.event import (EventPriority, event_handler, PlayerLoginEvent, PlayerJoinEvent, PlayerQuitEvent,
                            ServerCommandEvent, PlayerCommandEvent, PlayerChatEvent, BlockBreakEvent, BlockPlaceEvent,
                            PlayerInteractEvent, DataPacketSendEvent, DataPacketReceiveEvent)
from endstone_wmctcore.events.chat_events import handle_chat_event
from endstone_wmctcore.events.command_processes import handle_command_preprocess, handle_server_command_preprocess
from endstone_wmctcore.events.player_connect import handle_login_event, handle_join_event, handle_leave_event
from endstone_wmctcore.events.grieflog_events import handle_block_break, handle_player_interact, handle_block_place


class WMCTPlugin(Plugin):
    api_version = "0.6"
    authors = ["PrimeStrat", "trainer jeo"]

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

    @event_handler(priority=EventPriority.HIGHEST)
    def on_player_chat(self, ev: PlayerChatEvent):
        handle_chat_event(self, ev)

    @event_handler()
    def on_block_break(self, ev: BlockBreakEvent):
        handle_block_break(self, ev)

    @event_handler()
    def on_block_place(self, ev: BlockPlaceEvent):
        handle_block_place(self, ev)

    @event_handler()
    def on_player_int(self, ev: PlayerInteractEvent):
        handle_player_interact(self, ev)

    def on_load(self):
        plugin_text()

    def on_enable(self):
        self.register_events(self)
        
        for player in self.server.online_players:
            self.reload_custom_perms(player)

        config = load_config()
        if config["modules"]["grieflog_storage_auto_delete"]["enabled"]:
            dbgl = GriefLog("wmctcore_gl.db")
            dbgl.delete_logs_older_than_seconds(config["modules"]["grieflog_storage_auto_delete"]["removal_time_in_seconds"], True)
            dbgl.close_connection()

        if config["modules"]["check_prolonged_death_screen"]["enabled"] or config["modules"]["check_afk"]["enabled"]:
            if config["modules"]["check_prolonged_death_screen"]["enabled"]:
                print(f"[CONFIG] doimmediaterespawn gamerule is now set to true since prolonged deathscreen check is enabled")
            interval_function(self)

    def on_disable(self):
        clear_all_intervals(self)
        stop_interval(self)

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
            # Hide file paths by removing drive letters and usernames
            def clean_traceback(tb):
                cleaned_lines = []
                for line in tb.splitlines():
                    if 'File "' in line:
                        # Replace file paths with "<hidden>"
                        path_start = line.find('"') + 1
                        path_end = line.find('"', path_start)
                        file_path = line[path_start:path_end]
                        hidden_path = os.path.basename(file_path)
                        line = line.replace(file_path, f"<hidden>/{hidden_path}")
                    cleaned_lines.append(line)
                return "\n".join(cleaned_lines)

            # Generate the error message
            error_message = (
                    f"{ColorFormat.RED}========\n"
                    f"{ColorFormat.GOLD}This command generated an error -> please report this on our GitHub and provide a copy of the error below!\n"
                    f"{ColorFormat.RED}========\n\n"
                    f"{ColorFormat.YELLOW}{e}\n\n"
                    + f"{ColorFormat.YELLOW}{clean_traceback(traceback.format_exc())}\n"
                      f"{ColorFormat.RESET}"
            )
            error_message_console = (
                    f"========\n"
                    f"This command generated an error -> please report this on our GitHub and provide a copy of the error below!\n"
                    f"========\n\n"
                    f"{e}\n\n"
                    + clean_traceback(traceback.format_exc())
            )

            sender.send_message(error_message)

            # Only log to console if the sender isn't the server itself
            if sender.name != "Server":
                print(error_message_console)

            return False