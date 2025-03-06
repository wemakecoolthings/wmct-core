from endstone import Player, ColorFormat
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.dbUtil import UserDB
from endstone_wmctcore.utils.prefixUtil import infoLog, errorLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "logs",
    "Toggles whether you receive admin logs!",
    ["/logs [toggle: bool]"],
    ["wmctcore.command.logs"]
)

# LOGS COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    if not isinstance(sender, Player):
        sender.send_error_message("This command can only be executed by a player")
        return False

    db = UserDB("wmctcore_users.db")

    # Fetch the current status of logs
    current_status = db.get_offline_user(sender.name).enabled_logs

    if not args:
        # No arguments: return current status
        status_message = f"{infoLog()}Admin logs are currently {f'{ColorFormat.GREEN}enabled' if current_status else f'{ColorFormat.RED}disabled'}"
        sender.send_message(status_message)
    else:
        # Toggle logs based on input
        new_status = args[0].lower() in ["true", "1", "yes", "enable"]
        db.update_user_data(sender.name, "enabled_logs", int(new_status))
        sender.send_message(f"{infoLog()}Admin logs have been {f'{ColorFormat.GREEN}enabled' if new_status else f'{ColorFormat.RED}disabled'}")

    db.close_connection()
    return True
