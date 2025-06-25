import time

from endstone import Player, ColorFormat
from endstone.command import CommandSender
from endstone_primebds.utils.commandUtil import create_command
from endstone_primebds.utils.formWrapperUtil import ActionFormResponse, ActionFormData
from endstone_primebds.utils.prefixUtil import errorLog
from endstone_primebds.utils.dbUtil import GriefLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_primebds.primebds import PrimeBDS

# Register command
command, permission = create_command(
    "activitylist",
    "Lists players by activity filter (highest, lowest, or recent)!",
    ["/activitylist (highest|lowest|recent)[filter: activity_filter]"],
    ["primebds.command.activitylist"]
)

# ACTIVITY LIST COMMAND FUNCTIONALITY
def handler(self: "PrimeBDS", sender: CommandSender, args: list[str]) -> bool:
    if len(args) < 1:
        filter_type = "highest"  # Default to 'highest' if no filter is provided
    else:
        filter_type = args[0].lower()  # Filter type (highest, lowest, recent)

    dbgl = GriefLog("primebds_gl.db")

    # Fetch all users and their total playtimes
    playtimes = dbgl.get_all_playtimes()

    if not playtimes:
        sender.send_message(f"{errorLog()}No player playtime data found")
        return True

    # Sort the playtimes based on the filter type
    if filter_type == "highest":
        sorted_playtimes = sorted(playtimes, key=lambda x: x['total_playtime'], reverse=True)
    elif filter_type == "lowest":
        sorted_playtimes = sorted(playtimes, key=lambda x: x['total_playtime'])
    elif filter_type == "recent":
        # For the 'recent' filter, sort by the most recent session's start_time
        sorted_playtimes = []
        for player in playtimes:
            xuid = player['xuid']
            sessions = dbgl.get_user_sessions(xuid)
            if sessions:
                # Get the most recent session (sorted by start_time)
                recent_session = max(sessions, key=lambda s: s['start_time'])
                sorted_playtimes.append({
                    'name': player['name'],
                    'xuid': xuid,
                    'recent_session_start': recent_session['start_time'],
                    'total_playtime': player['total_playtime']
                })
        # Sort by most recent session's start_time
        sorted_playtimes = sorted(sorted_playtimes, key=lambda x: x['recent_session_start'], reverse=True)
    else:
        sender.send_message(f"{errorLog()} Invalid filter type. Use 'highest', 'lowest', or 'recent'.")
        return True

    form = ActionFormData()
    form.title("Player Activity List")
    form.body(f"Top players sorted by {filter_type} activity:")

    for entry in sorted_playtimes:
        player_name = entry['name']
        total_playtime_seconds = entry['total_playtime']

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

        form.button(f"{ColorFormat.AQUA}{player_name}\n{ColorFormat.RED}{playtime_str}")

    form.button("Cancel")

    form.show(sender).then(
        lambda player=sender, result=ActionFormResponse: handle_activitylist_response(player, result)
    )

    dbgl.close_connection()

    return True

def handle_activitylist_response(player: Player, result: ActionFormResponse):
    if result.canceled or result.selection is None:
        return 
