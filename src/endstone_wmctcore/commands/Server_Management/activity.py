import time

from endstone import Player
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.prefixUtil import infoLog, errorLog, trailLog
from endstone_wmctcore.utils.dbUtil import GriefLog
from endstone_wmctcore.utils.timeUtil import TimezoneUtils

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "activity",
    "Lists out session information!",
    ["/activity <player: player> [page: int]"],
    ["wmctcore.command.activity"]
)

SESSIONS_PER_PAGE = 5

# ACTIVITY COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    if len(args) < 1:
        sender.sendMessage(f"{errorLog()} Usage: /activity <player> [page]")
        return True

    player_name = args[0]
    player = self.server.get_player(player_name)
    page = int(args[1]) if len(args) > 1 else 1

    if page < 1:
        sender.send_message(f"{errorLog()}Page must be 1 or higher")
        return True

    dbgl = GriefLog("wmctcore_gl.db")

    # Fetch all sessions and reverse them (latest first)
    sessions = dbgl.get_user_sessions(player.xuid)
    sessions.reverse()

    # Handle no sessions found
    if not sessions:
        sender.send_message(f"{errorLog()}No session history found for {player_name}")
        return True

    # Calculate total combined playtime (including active sessions)
    total_playtime_seconds = dbgl.get_total_playtime(player.xuid)
    total_playtime_minutes = total_playtime_seconds // 60
    total_playtime_hours = total_playtime_minutes // 60
    total_playtime_minutes %= 60

    # Display total playtime at the top
    sender.send_message(f"{infoLog()}§rSession History for {player_name} (Page {page}/{(len(sessions) + SESSIONS_PER_PAGE - 1) // SESSIONS_PER_PAGE}):")
    sender.send_message(f"{trailLog()}§eTotal Playtime: §f{total_playtime_hours}h {total_playtime_minutes}m")

    # Pagination setup
    total_sessions = len(sessions)
    total_pages = (total_sessions + SESSIONS_PER_PAGE - 1) // SESSIONS_PER_PAGE

    if page > total_pages:
        sender.sendMessage(f"{errorLog()} Page {page} does not exist. Maximum page: {total_pages}.")
        return True

    # Slice the sessions for the current page
    start_index = (page - 1) * SESSIONS_PER_PAGE
    end_index = start_index + SESSIONS_PER_PAGE
    page_sessions = sessions[start_index:end_index]

    # Display the sessions
    for session in page_sessions:
        start_time = TimezoneUtils.convert_to_timezone(session['start_time'], 'EST')

        # Handle active sessions
        if session['end_time'] is None:
            end_time = "§aActive Now"
            active_minutes = int((time.time() - session['start_time']) // 60)
            duration_text = f"§a(+{active_minutes} min)"
        else:
            end_time = TimezoneUtils.convert_to_timezone(session['end_time'], 'EST')
            duration_minutes = session['duration'] // 60
            duration_text = f"§f({duration_minutes} min)"

        sender.send_message(f"{trailLog()}§a{start_time}§7 - §c{end_time} {duration_text}")

    dbgl.close_connection()
    return True
