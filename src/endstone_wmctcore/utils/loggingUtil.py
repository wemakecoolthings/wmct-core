import time
from datetime import datetime
from typing import TYPE_CHECKING
import requests
import re

from endstone import ColorFormat

from endstone_wmctcore.utils.dbUtil import UserDB
from endstone_wmctcore.utils.formWrapperUtil import ActionFormData, ActionFormResponse
from endstone_wmctcore.utils.internalPermissionsUtil import has_log_perms
from endstone_wmctcore.utils.configUtil import load_config
from endstone_wmctcore.utils.prefixUtil import infoLog, griefLog
from endstone_wmctcore.utils.timeUtil import TimezoneUtils

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

def log(self: "WMCTPlugin", message, type):
    config = load_config()
    discordRelay(message, type)
    admin_tags = set(config["modules"]["game_logging"].get("custom_tags", []))

    db = UserDB("wmctcore_users.db")

    for player in self.server.online_players:
        user = db.get_online_user(player.xuid)
        if has_log_perms(user.internal_rank) or admin_tags.intersection(set(player.scoreboard_tags) or player.is_op):
            if db.enabled_logs(player.xuid):
                player.send_message(message)
                return True

    db.close_connection()

    return False

def discordRelay(message, type):
    message = re.sub(r'§.', '', message)

    config = load_config()
    discord_logging = config["modules"]["discord_logging"]

    if type == "cmd" and discord_logging["commands"]["enabled"]:
        webhook_url = discord_logging["commands"]["webhook"]
    elif type == "mod" and discord_logging["moderation"]["enabled"]:
        webhook_url = discord_logging["moderation"]["webhook"]
    elif type == "chat" and discord_logging["chat"]["enabled"]:
        webhook_url = discord_logging["chat"]["webhook"]
    elif type == "grief" and discord_logging["griefing"]["enabled"]:
        webhook_url = discord_logging["griefing"]["webhook"]
    else:
        # No matching category or disabled module
        return False

    # If the webhook URL is empty, do nothing
    if not webhook_url:
        return False

    # Format the payload to be sent to Discord
    payload = {
        "embeds": [
            {
                "title": discord_logging["embed"]["title"],
                "description": message,
                "color": discord_logging["embed"]["color"],
                "footer": {
                    "text": f"Logged at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                }
            }
        ]
    }

    # Send the HTTP POST request to the Discord webhook
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Discord message: {e}")
        return False

def sendGriefLog(logs: list[dict], sender):
    if not logs:  # Check if logs are empty
        sender.send_message(f"{griefLog()}No grief logs found.")
        return True

    logs.sort(key=lambda x: x['timestamp'], reverse=True)

    # Split logs into pages of 15 entries each
    logs_per_page = 15
    total_pages = (len(logs) + logs_per_page - 1) // logs_per_page  # Calculate total number of pages, fixed calculation
    current_page = 1
    show_page(current_page, logs, total_pages, sender, logs_per_page)

    return True

def show_page(current_page, logs, total_pages, sender, logs_per_page):
    form = ActionFormData()
    form.title(f"Grief Log Activity ({current_page}/{total_pages})")  # Display total pages correctly

    # Ensure the page number is within valid bounds
    start_idx = (current_page - 1) * logs_per_page  # Start index for the current page
    end_idx = min(start_idx + logs_per_page, len(logs))  # End index for the current page

    log_text = f"{ColorFormat.YELLOW}Found logs:\n\n"

    # Format logs for the current page
    for log in logs[start_idx:end_idx]:
        player_name = log['name']
        action = log['action']
        timestamp = log['timestamp']
        location = log['location']
        formatted_time = TimezoneUtils.convert_to_timezone(timestamp, 'EST')

        # Start building the log text
        log_text += f"{ColorFormat.RESET}User: {ColorFormat.AQUA}{player_name}\n{ColorFormat.RESET}Action: {ColorFormat.GREEN}{action}\n{ColorFormat.RESET}Location: {ColorFormat.YELLOW}{location}\n{ColorFormat.RESET}Time: {ColorFormat.RED}{formatted_time}\n"

        # Check if block_type exists and append it if present
        if 'block_type' in log:
            block_type = log['block_type']
            log_text += f"{ColorFormat.RESET}Block Type: {ColorFormat.BLUE}{block_type}\n"

        # Check if block_state exists and append it if present
        if 'block_state' in log:
            block_state = log['block_state']
            log_text += f"{ColorFormat.RESET}Block State: {ColorFormat.LIGHT_PURPLE}{block_state}\n"

        log_text += "\n"

    form.body(log_text)
    discordRelay(log_text, "grief")

    # Add navigation buttons
    form.button("Next Page")
    form.button("Previous Page")

    # Show the form to the sender
    form.show(sender).then(
        lambda player=sender, result=ActionFormResponse: handle_grieflog_response(player, result, current_page, logs, total_pages, sender, logs_per_page)
    )

def handle_grieflog_response(player, result, current_page, logs, total_pages, sender, logs_per_page):
    if result.canceled or result.selection is None:
        return  # User canceled or didn't select anything

    # Next Page
    if result.selection == 0:  # Next button
        if current_page < total_pages:
            current_page += 1
        else:
            current_page = 1  # Loop back to the first page if at the end

    # Previous Page
    elif result.selection == 1:  # Previous button
        if current_page > 1:
            current_page -= 1
        else:
            current_page = total_pages  # Loop back to the last page if at the beginning

    # Show the updated page
    show_page(current_page, logs, total_pages, sender, logs_per_page)


