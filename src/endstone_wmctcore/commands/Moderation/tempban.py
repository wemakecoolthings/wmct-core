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
    "tempban",
    "Temporarily bans a player from the server!",
    ["/tempban <player: player> <duration_number: int> (second|minute|hour|day|week|month|year)<duration_length: length> [reason: message]"],
    ["wmctcore.command.tempban"]
)

# TEMPBAN COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    if len(args) < 3:
        sender.send_message(f"{errorLog()}Usage: /tempban <player> <duration_number> (second|minute|hour|day|week|month|year) [reason]")
        return False

    player_name = args[0].strip('"')
    target = self.server.get_player(player_name)

    if not target:
        # If the player is offline, look them up by name in the database
        db = UserDB("wmctcore_users.db")
        mod_log = db.get_offline_mod_log(player_name)
        if not mod_log:
            sender.send_message(f"{errorLog()}Player '{player_name}' not found.")
            db.close_connection()
            return False
        db.close_connection()

    try:
        duration_number = int(args[1])
        duration_unit = args[2].lower()
    except ValueError:
        sender.send_message(f"{errorLog()}Invalid duration format. Use an integer followed by a time unit.")
        return False

    # Supported time units
    time_units = {
        "second": timedelta(seconds=duration_number),
        "minute": timedelta(minutes=duration_number),
        "hour": timedelta(hours=duration_number),
        "day": timedelta(days=duration_number),
        "week": timedelta(weeks=duration_number),
        "month": timedelta(days=30 * duration_number),  # Approximation
        "year": timedelta(days=365 * duration_number)   # Approximation
    }

    if duration_unit not in time_units:
        sender.send_message(f"{errorLog()}Invalid time unit. Use: second, minute, hour, day, week, month, year.")
        return False

    ban_duration = time_units[duration_unit]
    ban_expiration = datetime.now() + ban_duration
    reason = " ".join(args[3:]) if len(args) > 3 else "Negative Behavior"

    # Convert datetime to timestamp for format_time_remaining
    formatted_expiration = format_time_remaining(int(ban_expiration.timestamp()))
    message = ban_message(self.server.level.name, formatted_expiration, reason)

    db = UserDB("wmctcore_users.db")
    if target:
        # If the player is online, add ban directly
        db.add_ban(target.xuid, int(ban_expiration.timestamp()), reason)
        target.kick(message)
        sender.send_message(f"{modLog()}Player {ColorFormat.YELLOW}{player_name} {ColorFormat.GOLD}was banned for {ColorFormat.YELLOW}\"{reason}\" {ColorFormat.GOLD}for {ColorFormat.YELLOW}{formatted_expiration}")
    else:
        # If the player is offline, use xuid to ban them
        db.add_ban(db.get_xuid_by_name(player_name), int(ban_expiration.timestamp()), reason)
        sender.send_message(f"{modLog()}Player {ColorFormat.YELLOW}{player_name} {ColorFormat.GOLD}was banned for {ColorFormat.YELLOW}\"{reason}\" {ColorFormat.GOLD}for {ColorFormat.YELLOW}{formatted_expiration} {ColorFormat.GRAY}{ColorFormat.ITALIC}(Offline)")

    db.close_connection()
    return True
