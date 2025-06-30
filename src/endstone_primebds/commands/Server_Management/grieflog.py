from datetime import timedelta, datetime

from endstone import Player
from endstone.command import CommandSender
from endstone_primebds.utils.commandUtil import create_command
from endstone_primebds.utils.configUtil import load_config
from endstone_primebds.utils.dbUtil import GriefLog
from endstone_primebds.utils.loggingUtil import sendGriefLog
from endstone_primebds.utils.prefixUtil import errorLog, griefLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_primebds.primebds import PrimeBDS

# Register command
command, permission = create_command(
    "grieflog",
    "Displays or manages grief logs based on the given parameters.",
    ["/grieflog <radius: int> (login|logout|block_break|block_place|opened_container)[filter: action_log] [player: player]",
            "/grieflog (delete)<clear_logs: clear_logs> (all|time)<all: all_gl> [time_in_minutes: int]"],
    ["primebds.command.grieflog"],
    "op",
    ["gl"]
)

# GRIEFLOG COMMAND FUNCTIONALITY
def handler(self: "PrimeBDS", sender: CommandSender, args: list[str]) -> bool:
    config = load_config()
    is_gl_enabled = config["modules"]["grieflog"]["enabled"]

    if not is_gl_enabled:
        sender.send_message(f"{errorLog()}Grief Logger is currently disabled by config")
        return True

    if isinstance(sender, Player):
        radius = 0
        action_filter = None
        player_name = None
        dbgl = GriefLog("griefLog.db")

        if len(args) > 0:
            try:
                radius = int(args[0]) if args[0].isdigit() else 0
            except ValueError:
                radius = 0

        if len(args) > 1:
            action_input = args[1].lower()
            action_mapping = {
                "block_break": "Block Break",
                "block_place": "Block Place",
                "opened_container": "Opened Container",
                "login": "Login",
                "logout": "Logout"
            }
            action_filter = action_mapping.get(action_input)

        if len(args) > 2:
            player_name = args[2]

        if len(args) > 0 and args[0].lower() == "delete":
            if len(args) == 2 and args[1].lower() == "all":
                # Clear all logs
                dbgl.delete_all_logs()
                sender.send_message(f"{griefLog()}All grief logs have been cleared")
                return True

            elif len(args) == 3 and args[1].lower() == "time" and args[2].isdigit():
                # Clear logs from the last x minutes
                minutes = int(args[2])
                logs_cleared = dbgl.delete_logs_within_seconds(int(minutes * 60))
                sender.send_message(f"{griefLog()}Cleared {logs_cleared} grief logs from the last {minutes} minutes have been cleared")
                return True

            else:
                # Invalid arguments for flush
                sender.send_message(f"{errorLog()}Invalid arguments. Usage: /grieflog flush (all|time) [time_in_minutes]")
                return True

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

        sendGriefLog(logs, sender)
        return True
    else:
        sender.send_error_message("This command can only be executed by a player")
    return True

def format_action(action: str) -> str:
    return " ".join(word.capitalize() for word in action.split("_"))