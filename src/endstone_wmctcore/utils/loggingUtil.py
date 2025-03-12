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
        print(logs)
        sender.send_message(f"{griefLog()}No grief logs found.")
        return True

    logs.sort(key=lambda x: x['timestamp'], reverse=True)

    # Split logs into pages of 15 entries each
    logs_per_page = 15
    total_pages = (len(logs) + logs_per_page - 1) // logs_per_page  # Calculate total number of pages
    current_page = 1
    show_page(current_page, logs, total_pages, sender, logs_per_page)

    return True

def show_page(current_page, logs, total_pages, sender, logs_per_page):
    form = ActionFormData()
    form.title(f"Grief Log Activity ({current_page}/{total_pages-1})")

    # Ensure the page number is within valid bounds
    start_idx = current_page * logs_per_page
    end_idx = min(start_idx + logs_per_page, len(logs))

    location = logs[0]['location']  # Get location for uniform display
    log_text = f"{ColorFormat.YELLOW}Actions at coordinates {location}\n\n"

    # Format logs for the current page
    for log in logs[start_idx:end_idx]:
        player_name = log['name']
        action = log['action']
        timestamp = log['timestamp']
        formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(timestamp))  # Format the timestamp

        log_text += f"{ColorFormat.AQUA}{player_name}\n{ColorFormat.GREEN}{action}\n{ColorFormat.RED}{formatted_time}\n\n"

    form.body(log_text)

    # Add navigation buttons
    form.button("Next Page")
    form.button("Previous Page")

    # Show the form to the sender
    form.show(sender).then(
        lambda player=sender, result=ActionFormResponse: handle_grieflog_response(player, result, current_page, logs, total_pages, sender, logs_per_page)
    )

def handle_grieflog_response(player, result, current_page, logs, total_pages, sender, logs_per_page):
    if result.selection == 0:  # Next button
        if current_page < total_pages - 1:
            show_page(current_page + 1, logs, total_pages, sender, logs_per_page)
        else:
            show_page(1, logs, total_pages, sender, logs_per_page)
    elif result.selection == 1:  # Previous button
        if current_page > 1:
            show_page(current_page - 1, logs, total_pages, sender, logs_per_page)
        else:
            show_page(total_pages-1, logs, total_pages, sender, logs_per_page)

