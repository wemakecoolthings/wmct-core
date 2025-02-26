from endstone import ColorFormat
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.dbUtil import UserDB
from endstone_wmctcore.utils.prefixUtil import modLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "unmute",
    "Removes an active mute from a player!",
    ["/unmute <player: player>"],
    ["wmctcore.command.unmute"]
)

# UNMUTE COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    if len(args) < 1:
        sender.send_message(f"{modLog()}Usage: /unmute <player>")
        return False

    player_name = args[0].strip('"')
    db = UserDB("wmctcore_users.db")

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
    return True
