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
    "ipban",
    "Bans a player's IP from the server, either temporarily or permanently!",
    [
        "/ipban <player: player> <duration_number: int> (second|minute|hour|day|week|month|year)<duration_length: ip_ban_length> [reason: message]",
        "/ipban <player: player> (forever)<forever: forever> [reason: message]"
    ],
    ["wmctcore.command.ipban"]
)

# IPBAN COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    if len(args) < 2:
        sender.send_message(
            f"{errorLog()}Usage: /ipban <player> <duration> (unit) [reason] or /ipban <player> forever [reason]")
        return False

    player_name = args[0].strip('"')
    target = self.server.get_player(player_name)

    db = UserDB("wmctcore_users.db")

    # Check if the player is already IP-banned (online or offline)
    if target:
        # If the player is online, check the ban status in the database
        if db.get_mod_log(target.xuid).is_banned:
            sender.send_message(f"{modLog()}Player {ColorFormat.YELLOW}{player_name} {ColorFormat.RED}is already IP-banned.")
            db.close_connection()
            return False
    else:
        # If the player is offline, check their mod log for an existing IP ban
        mod_log = db.get_offline_mod_log(player_name)
        if mod_log and mod_log.is_ip_banned:
            sender.send_message(f"{modLog()}Player {ColorFormat.YELLOW}{player_name} {ColorFormat.RED}is already IP-banned.")
            db.close_connection()
            return False

        if not mod_log:
            sender.send_message(f"{errorLog()}Player '{player_name}' not found.")
            db.close_connection()
            return False

    reason = "Negative Behavior"
    permanent = args[1].lower() == "forever"

    if permanent:
        ban_expiration = datetime.now() + timedelta(days=365 * 300)  # Explicit 300-year ban
        reason = " ".join(args[2:]) if len(args) > 2 else reason
    else:
        if len(args) < 3:
            sender.send_message(f"{errorLog()}Invalid duration format. Use an integer followed by a time unit.")
            return False

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
            "year": timedelta(days=361 * duration_number)  # Approximation
        }

        if duration_unit not in time_units:
            sender.send_message(f"{errorLog()}Invalid time unit. Use: second, minute, hour, day, week, month, year.")
            return False

        ban_duration = time_units[duration_unit]
        ban_expiration = datetime.now() + ban_duration
        reason = " ".join(args[3:]) if len(args) > 3 else reason

    # Convert datetime to timestamp for format_time_remaining
    formatted_expiration = "Permanent" if permanent else format_time_remaining(int(ban_expiration.timestamp()))
    message = ban_message(self.server.level.name, formatted_expiration, "IP Ban - " + reason)

    target_user = target if target else db.get_offline_mod_log(player_name)

    if not target_user:
        sender.send_message(f"{modLog()}Could not retrieve IP for '{player_name}'.")
        db.close_connection()
        return False

    db.add_ban(target_user.xuid, int(ban_expiration.timestamp()), reason, True)

    if target:
        target.kick(message)
        if permanent:
            sender.send_message(
                f"{modLog()}Player {ColorFormat.YELLOW}{player_name} {ColorFormat.GOLD}was permanently IP banned for {ColorFormat.YELLOW}'{reason}' {ColorFormat.GOLD}. {ColorFormat.GRAY}{ColorFormat.ITALIC}(Permanent IP Banned)."
            )
        else:
            sender.send_message(
                f"{modLog()}Player {ColorFormat.YELLOW}{player_name} {ColorFormat.GOLD}was IP banned for {ColorFormat.YELLOW}'{reason}' {ColorFormat.GOLD}for {formatted_expiration} {ColorFormat.GRAY}{ColorFormat.ITALIC}(IP Banned)."
            )
    else:
        if permanent:
            sender.send_message(
                f"{modLog()}Player {ColorFormat.YELLOW}{player_name} {ColorFormat.GOLD}was permanently IP banned for {ColorFormat.YELLOW}'{reason}' {ColorFormat.GOLD}. {ColorFormat.GRAY}{ColorFormat.ITALIC}(Offline, Permanent IP Banned)."
            )
        else:
            sender.send_message(
                f"{modLog()}Player {ColorFormat.YELLOW}{player_name} {ColorFormat.GOLD}was IP banned for {ColorFormat.YELLOW}'{reason}' {ColorFormat.GOLD}for {formatted_expiration} {ColorFormat.GRAY}{ColorFormat.ITALIC}(Offline, IP Banned)."
            )

    db.close_connection()
    return True
