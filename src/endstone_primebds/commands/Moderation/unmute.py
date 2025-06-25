from endstone import ColorFormat
from endstone.command import CommandSender
from endstone_primebds.utils.commandUtil import create_command
from endstone_primebds.utils.configUtil import load_config
from endstone_primebds.utils.dbUtil import UserDB
from endstone_primebds.utils.loggingUtil import log
from endstone_primebds.utils.prefixUtil import modLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_primebds.primebds import PrimeBDS

# Register command
command, permission = create_command(
    "unmute",
    "Removes an active mute from a player!",
    ["/unmute <player: player>"],
    ["primebds.command.unmute"]
)

# UNMUTE COMMAND FUNCTIONALITY
def handler(self: "PrimeBDS", sender: CommandSender, args: list[str]) -> bool:
    if len(args) < 1:
        sender.send_message(f"{modLog()}Usage: /unmute <player>")
        return False

    player_name = args[0].strip('"')
    db = UserDB("primebds_users.db")

    # Get the mod log to check if the player is muted
    mod_log = db.get_offline_mod_log(player_name)

    if not mod_log or not mod_log.is_muted:
        # Player is not muted, return an error message
        sender.send_message(f"{modLog()}Player {ColorFormat.YELLOW}{player_name} {ColorFormat.GOLD}is not muted")
        db.close_connection()
        return False

    # Remove the mute
    db.remove_mute(player_name)
    db.close_connection()

    # Notify the sender that the mute has been removed
    sender.send_message(f"{modLog()}Player {ColorFormat.YELLOW}{player_name} {ColorFormat.GOLD}has been unmuted")

    config = load_config()
    mod_log_enabled = config["modules"]["game_logging"]["moderation"]["enabled"]
    if mod_log_enabled:
        log(self, f"{modLog()}Player {ColorFormat.YELLOW}{player_name} {ColorFormat.GOLD}was unmuted by {ColorFormat.YELLOW}{sender.name}", "mod")

    return True
