from endstone import ColorFormat
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.configUtil import load_config
from endstone_wmctcore.utils.dbUtil import UserDB
from endstone_wmctcore.utils.loggingUtil import log
from endstone_wmctcore.utils.modUtil import format_time_remaining, ban_message
from endstone_wmctcore.utils.prefixUtil import errorLog, modLog
from datetime import timedelta, datetime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "mute",
    "Permanently mutes a player from the server!",
    ["/mute <player: player> [reason: message]"],
    ["wmctcore.command.mute"]
)

def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    if len(args) < 1:
        sender.send_message(f"{errorLog()}Usage: /mute <player> [reason]")
        return False

    player_name = args[0].strip('"')
    target = self.server.get_player(player_name)

    db = UserDB("wmctcore_users.db")

    # Check if the player is muted already
    mod_log = db.get_offline_mod_log(player_name)
    if mod_log and mod_log.is_muted:
        formatted_expiration = format_time_remaining(mod_log.mute_time, True)
        sender.send_message(f"{modLog()}Player {ColorFormat.YELLOW}{player_name} {ColorFormat.GOLD}is already muted for {ColorFormat.YELLOW}{mod_log.mute_reason}{ColorFormat.GOLD}, the mute expires {ColorFormat.YELLOW}{formatted_expiration}")
        db.close_connection()
        return False

    mute_duration = timedelta(days=365 * 300)
    mute_expiration = datetime.now() + mute_duration
    reason = " ".join(args[3:]) if len(args) > 3 else "Negative Behavior"

    # Convert datetime to timestamp for format_time_remaining
    formatted_expiration = format_time_remaining(int(mute_expiration.timestamp()), True)
    message = f"{modLog()}You are muted for {ColorFormat.YELLOW}{reason} {ColorFormat.GOLD}which expires {ColorFormat.YELLOW}{formatted_expiration}"

    if target:
        # If the player is online, apply the mute directly
        db.add_mute(target.xuid, int(mute_expiration.timestamp()), reason)
        target.send_message(message)
        sender.send_message(
            f"{modLog()}Player {ColorFormat.YELLOW}{player_name} {ColorFormat.GOLD}was muted for {ColorFormat.YELLOW}\"{reason}\" {ColorFormat.GOLD}which expires {ColorFormat.YELLOW}{formatted_expiration}")
    else:
        # If the player is offline, use xuid to mute them
        db.add_mute(db.get_xuid_by_name(player_name), int(mute_expiration.timestamp()), reason)
        sender.send_message(
            f"{modLog()}Player {ColorFormat.YELLOW}{player_name} {ColorFormat.GOLD}was muted for {ColorFormat.YELLOW}\"{reason}\" {ColorFormat.GOLD}which expires {ColorFormat.YELLOW}{formatted_expiration} {ColorFormat.GRAY}{ColorFormat.ITALIC}(Offline)")

    config = load_config()
    mod_log_enabled = config["modules"]["game_logging"]["moderation"]["enabled"]
    print(mod_log_enabled)
    if mod_log_enabled:
        log(self, f"{modLog()}Player {ColorFormat.YELLOW}{player_name} {ColorFormat.GOLD}was muted by {ColorFormat.YELLOW}{sender.name} {ColorFormat.GOLD}for {ColorFormat.YELLOW}\"{reason}\" {ColorFormat.GOLD}until {ColorFormat.YELLOW}{formatted_expiration}")

    db.close_connection()
    return True
