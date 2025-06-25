import time
from endstone.command import CommandSender
from endstone_primebds.utils.commandUtil import create_command
from endstone_primebds.utils.prefixUtil import infoLog, errorLog, trailLog
from endstone_primebds.utils.dbUtil import GriefLog, UserDB
from endstone_primebds.utils.timeUtil import TimezoneUtils
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_primebds.primebds import PrimeBDS

# Register command
command, permission = create_command(
    "activity",
    "Lists out session information!",
    ["/activity <player: player> [page: int]"],
    ["primebds.command.activity"]
)

SESSIONS_PER_PAGE = 5

def handler(self: "PrimeBDS", sender: CommandSender, args: list[str]) -> bool:
    if len(args) < 1:
        sender.sendMessage(f"{errorLog()} Usage: /activity <player> [page: int]")
        return True

    player_name = args[0]
    page = int(args[1]) if len(args) > 1 and args[1].isdigit() else 1
    if page < 1:
        page = 1

    dbgl = GriefLog("primebds_gl.db")
    db = UserDB("primebds_users.db")
    xuid = db.get_xuid_by_name(player_name)
    db.close_connection()

    if not xuid:
        sender.send_message(f"{errorLog()}No session history found for {player_name}")
        return True

    # Fetch all user sessions
    sessions = dbgl.get_user_sessions(xuid)
    if not sessions:
        sender.send_message(f"{errorLog()}No session history found for {player_name}")
        return True

    total_playtime_seconds = dbgl.get_total_playtime(xuid)
    sender.send_message(f"{infoLog()} §rSession History for {player_name} (Page {page}):")

    playtime_str = format_time(total_playtime_seconds)
    sender.send_message(f"{trailLog()} §eTotal Playtime: §f{playtime_str}")

    sessions.sort(key=lambda s: s['start_time'], reverse=True)

    active_session = None
    for session in sessions:
        if session['end_time'] is None:
            active_session = session
            sessions.remove(session)
            break

    # Display active session first (if applicable)
    if active_session:
        start_time = TimezoneUtils.convert_to_timezone(active_session['start_time'], 'EST')
        active_seconds = int(time.time() - active_session['start_time'])
        sender.send_message(f"{trailLog()} §a{start_time}§7 - §aActive Now §f(+{format_time(active_seconds)})")

    # Paginate session history
    total_pages = (len(sessions) + SESSIONS_PER_PAGE - 1) // SESSIONS_PER_PAGE
    start_idx = (page - 1) * SESSIONS_PER_PAGE
    end_idx = start_idx + SESSIONS_PER_PAGE
    paginated_sessions = sessions[start_idx:end_idx]

    for session in paginated_sessions:
        start_time = TimezoneUtils.convert_to_timezone(session['start_time'], 'EST')
        end_time = TimezoneUtils.convert_to_timezone(session['end_time'], 'EST')
        duration_text = f"§f({format_time(session['duration'])})"
        sender.send_message(f"{trailLog()} §a{start_time}§7 - §c{end_time} {duration_text}")

    if page < total_pages:
        sender.send_message(f"{trailLog()} §eUse '/activity {player_name} {page + 1}' for more.")

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