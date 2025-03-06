from endstone import ColorFormat
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.configUtil import load_config
from endstone_wmctcore.utils.dbUtil import UserDB
from endstone_wmctcore.utils.loggingUtil import log
from endstone_wmctcore.utils.prefixUtil import modLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "removeban",
    "Removes an active ban from a player!",
    ["/removeban <player: player>"],
    ["wmctcore.command.pardon"]
)

# REMOVEBAN COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    if len(args) < 1:
        sender.send_message(f"{modLog()}Usage: /removeban <player>")
        return False

    player_name = args[0].strip('"')
    db = UserDB("wmctcore_users.db")

    # Get the mod log to check if the player is banned
    mod_log = db.get_offline_mod_log(player_name)

    if not mod_log or not mod_log.is_banned:
        # Player is not banned, return an error message
        sender.send_message(f"{modLog()}Player {ColorFormat.YELLOW}{player_name} {ColorFormat.GOLD}is not banned")
        db.close_connection()
        return False

    # Remove the ban
    db.remove_ban(player_name)
    db.close_connection()

    # Notify the sender that the ban has been removed
    sender.send_message(f"{modLog()}Player {ColorFormat.YELLOW}{player_name} {ColorFormat.GOLD}has been unbanned")

    config = load_config()
    mod_log_enabled = config["modules"]["game_logging"]["moderation"]["enabled"]
    if mod_log_enabled:
        log(self, f"{modLog()}Player {ColorFormat.YELLOW}{player_name} {ColorFormat.GOLD}was unbanned by {ColorFormat.YELLOW}{sender.name}")

    return True

