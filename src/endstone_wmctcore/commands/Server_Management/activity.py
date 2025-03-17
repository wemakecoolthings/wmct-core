import time
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.prefixUtil import infoLog, errorLog, trailLog
from endstone_wmctcore.utils.dbUtil import GriefLog, UserDB
from endstone_wmctcore.utils.timeUtil import TimezoneUtils
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "activity",
    "Lists out session information!",
    ["/activity <player: player>"],
    ["wmctcore.command.activity"]
)

# ACTIVITY COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    if len(args) < 1:
        sender.sendMessage(f"{errorLog()} Usage: /activity <player>")
        return True

    player_name = args[0]

    dbgl = GriefLog("wmctcore_gl.db")

    db = UserDB("wmctcore_users.db")
    xuid = db.get_xuid_by_name(player_name)
    db.close_connection()

    if not xuid:
        sender.send_message(f"{errorLog()}No session history found for {player_name}")
        return True

    # Fetch the most recent sessions (limit to 5)
    sessions = dbgl.get_user_sessions(xuid)
    sessions.reverse()  # Ensure latest sessions are at the front
    sessions = sessions[:5]  # Only take the 5 most recent

    if not sessions:
        sender.send_message(f"{errorLog()}No session history found for {player_name}")
        return True

    # Calculate total playtime (including active sessions)
    total_playtime_seconds = dbgl.get_total_playtime(xuid)

    sender.send_message(f"{infoLog()} §rSession History for {player_name}:")

    days = total_playtime_seconds // 86400  # 1 day = 86400 seconds
    hours = (total_playtime_seconds % 86400) // 3600  # 1 hour = 3600 seconds
    minutes = (total_playtime_seconds % 3600) // 60  # 1 minute = 60 seconds
    seconds = total_playtime_seconds % 60  # Remaining seconds

    # Construct the playtime string
    playtime_str = ""
    if days > 0:
        playtime_str += f"{days}d "
    if hours > 0 or days > 0:
        playtime_str += f"{hours}h "
    if minutes > 0 or hours > 0 or days > 0:
        playtime_str += f"{minutes}m "
    playtime_str += f"{seconds}s"

    sender.send_message(f"{trailLog()} §eTotal Playtime: §f{playtime_str}")

    active_session = None
    for session in sessions:
        if session['end_time'] is None:
            active_session = session
            sessions.remove(session)  
            break

    # Display the active session first (if applicable)
    if active_session:
        start_time = TimezoneUtils.convert_to_timezone(active_session['start_time'], 'EST')
        active_seconds = int(time.time() - active_session['start_time'])
        sender.send_message(f"{trailLog()} §a{start_time}§7 - §aActive Now §f(+{format_time(active_seconds)})")

    # Display up to 5 past sessions
    for session in sessions:
        start_time = TimezoneUtils.convert_to_timezone(session['start_time'], 'EST')
        end_time = TimezoneUtils.convert_to_timezone(session['end_time'], 'EST')
        duration_text = f"§f({format_time(session['duration'])})"
        sender.send_message(f"{trailLog()} §a{start_time}§7 - §c{end_time} {duration_text}")

    dbgl.close_connection()
    return True

def format_time(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h"
    days = hours // 24
    return f"{days}d"
