from endstone import ColorFormat
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.dbUtil import UserDB
from endstone_wmctcore.utils.modUtil import format_time_remaining, ban_message
from endstone_wmctcore.utils.prefixUtil import errorLog, modLog
from datetime import timedelta, datetime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "permban",
    "Permanently bans a player from the server!",
    ["/permban <player: player> [reason: message]"],
    ["wmctcore.command.permban"]
)

# PERMBAN COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    if len(args) < 1:
        sender.send_message(f"{errorLog()}Usage: /permban <player> [reason]")
        return False

    player_name = args[0].strip('"')
    target = self.server.get_player(player_name)

    db = UserDB("wmctcore_users.db")

    # Check if the player is already banned (online or offline)
    if target:
        # Check if the player is already banned while online
        if db.get_mod_log(target.xuid).is_banned:
            sender.send_message(
                f"{modLog()}Player {ColorFormat.YELLOW}{player_name} {ColorFormat.RED}is already permanently banned.")
            db.close_connection()
            return False
    else:
        # If the player is offline, check the ban status in the database
        mod_log = db.get_offline_mod_log(player_name)
        if mod_log and mod_log.is_banned:
            sender.send_message(
                f"{modLog()}Player {ColorFormat.YELLOW}{player_name} {ColorFormat.RED}is already permanently banned.")
            db.close_connection()
            return False

        if not mod_log:
            sender.send_message(f"{errorLog()}Player '{player_name}' not found.")
            db.close_connection()
            return False

    # Proceed with the permanent ban if not already banned
    ban_duration = timedelta(days=365 * 300)  # This equals 300 years
    ban_expiration = datetime.now() + ban_duration
    reason = " ".join(args[1:]) if len(args) > 1 else "Negative Behavior"

    # Convert datetime to timestamp for format_time_remaining
    formatted_expiration = format_time_remaining(int(ban_expiration.timestamp()))
    message = ban_message(self.server.level.name, formatted_expiration, reason)

    if target:
        # If the player is online, add the ban directly
        db.add_ban(target.xuid, int(ban_expiration.timestamp()), reason)
        target.kick(message)
        sender.send_message(
            f"{modLog()}Player {ColorFormat.YELLOW}{player_name} {ColorFormat.GOLD}was permanently banned for {ColorFormat.YELLOW}\"{reason}\" {ColorFormat.GOLD}")
    else:
        # If the player is offline, use XUID to ban them
        xuid = db.get_xuid_by_name(player_name)
        db.add_ban(xuid, int(ban_expiration.timestamp()), reason)
        sender.send_message(
            f"{modLog()}Player {ColorFormat.YELLOW}{player_name} {ColorFormat.GOLD}was permanently banned for {ColorFormat.YELLOW}\"{reason}\" {ColorFormat.GRAY}{ColorFormat.ITALIC}(Offline)")

    db.close_connection()
    return True
