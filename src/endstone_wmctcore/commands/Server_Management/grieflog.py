from datetime import timedelta, datetime

from endstone import Player
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.configUtil import load_config
from endstone_wmctcore.utils.dbUtil import GriefLog
from endstone_wmctcore.utils.loggingUtil import sendGriefLog
from endstone_wmctcore.utils.prefixUtil import infoLog, errorLog, griefLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "grieflog",
    "Displays or manages grief logs based on the given parameters.",
    ["/grieflog <radius: int> (login|logout|block_break|block_place|opened_container|item_use)[filter: action_log] [player: player]",
            "/grieflog (flush)<clear_logs: clear_logs> (all|time)<all: all_gl> [time_in_minutes: int]"],
    ["wmctcore.command.grieflog"],
    "op",
    ["gl"]
)

# GRIEFLOG COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    config = load_config()
    is_gl_enabled = config["modules"]["grieflog"]["enabled"]

    if not is_gl_enabled:
        sender.send_message(f"{errorLog()}Grief Logger is currently disabled by config")
        return True

    if isinstance(sender, Player):
        # Default values
        radius = 0
        action_filter = None
        player_name = None
        dbgl = GriefLog("wmctcore_gl.db")

        # Parse arguments
        if len(args) > 0:
            try:
                # Check for radius argument
                radius = int(args[0]) if args[0].isdigit() else 0
            except ValueError:
                radius = 0

        if len(args) > 1:
            # Action filter (e.g. login, logout, block_break, etc.)
            action_filter = map_action_to_internal(args[1])  # Map the formatted action to internal

        if len(args) > 2:
            # Player name filter
            player_name = args[2]

        # Handle the "flush" functionality (delete logs)
        if len(args) > 0 and args[0].lower() == "flush":
            if len(args) == 2 and args[1].lower() == "all":
                # Clear all logs
                dbgl.delete_all_logs()
                sender.send_message(f"{griefLog()}All grief logs have been cleared")
                return True

            elif len(args) == 3 and args[1].lower() == "time" and args[2].isdigit():
                # Clear logs from the last x minutes
                minutes = int(args[2])
                cutoff_timestamp = int((datetime.utcnow() - timedelta(minutes=minutes)).timestamp())
                dbgl.delete_old_grief_logs(cutoff_timestamp)
                sender.send_message(f"{griefLog()}All grief logs from the last {minutes} minutes have been cleared")
                return True

            else:
                # Invalid arguments for flush
                sender.send_message(f"{errorLog()}Invalid arguments. Usage: /grieflog flush (all|time) [time_in_minutes]")
                return True

        # Fetch logs within the radius
        sender = self.server.get_player(sender.name)
        logs = dbgl.get_logs_within_radius(sender.location.x, sender.location.y, sender.location.z, radius)

        # Filter logs by action type if action_filter is provided
        if action_filter:
            logs = [log for log in logs if log['action'] == action_filter]

        # Filter logs by player name if player_name is provided
        if player_name:
            logs = [log for log in logs if log['name'].lower() == player_name.lower()]

        # If no logs were found
        if not logs:
            sender.send_message(f"{griefLog()}No grief logs found for the given parameters")
            return True

        # Send logs
        sendGriefLog(logs, sender)
        return True
    else:
        sender.send_error_message("This command can only be executed by a player")
    return True

def format_action(action: str) -> str:
    return " ".join(word.capitalize() for word in action.split("_"))

def map_action_to_internal(action: str) -> str:
    action_mapping = {
        "Block Break": "block_break",
        "Block Place": "block_place",
        "Opened Container": "opened_container",
        "Item Use": "item_use",
        "Login": "login",
        "Logout": "logout"
    }
    return action_mapping.get(action, None)
