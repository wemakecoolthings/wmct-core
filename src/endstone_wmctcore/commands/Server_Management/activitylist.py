import time

from endstone import Player, ColorFormat
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.formWrapperUtil import ActionFormResponse, ActionFormData
from endstone_wmctcore.utils.prefixUtil import infoLog, errorLog, trailLog
from endstone_wmctcore.utils.dbUtil import GriefLog
from endstone_wmctcore.utils.timeUtil import TimezoneUtils

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "activitylist",
    "Lists players by activity filter (highest, lowest, or recent).",
    ["/activitylist (highest|lowest|recent)[filter: activity_filter]"],
    ["wmctcore.command.activitylist"]
)

# ACTIVITY LIST COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    if len(args) < 1:
        filter_type = "highest"  # Default to 'highest' if no filter is provided
    else:
        filter_type = args[0].lower()  # Filter type (highest, lowest, recent)

    dbgl = GriefLog("wmctcore_gl.db")

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

    # Create action form for the sorted list
    form = ActionFormData()
    form.title("Player Activity List")
    form.body(f"Top players sorted by {filter_type} activity:")

    # Add buttons with player names and their total playtime to the form
    for entry in sorted_playtimes:
        player_name = entry['name']
        total_playtime_seconds = entry['total_playtime']
        total_playtime_hours = total_playtime_seconds // 3600
        total_playtime_minutes = (total_playtime_seconds % 3600) // 60
        total_playtime_text = f"{total_playtime_hours}h {total_playtime_minutes}m"
        form.button(f"{ColorFormat.AQUA}{player_name}\n{ColorFormat.RED}{total_playtime_text}")

    # Add Cancel Button
    form.button("Cancel")

    form.show(sender).then(
        lambda player=sender, result=ActionFormResponse: handle_activitylist_response(player, result)
    )

    return True

# Handle the response after player selects from the action form
def handle_activitylist_response(player: Player, result: ActionFormResponse):
    if result.canceled or result.selection is None:
        return  # User canceled or didn't select anything
