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

import threading

def log(self: "WMCTPlugin", message, type):
    # Load configuration and initialize single DB connection
    config = load_config()
    db = UserDB("wmctcore_users.db")  # Open DB connection once at the start

    discord_thread = threading.Thread(target=discordRelay, args=(message, type))
    discord_thread.start()

    # Load config tags once
    config_tags = set(config["modules"]["game_logging"].get("custom_tags", []))

    # Create a set of online players that need messages sent
    players_to_notify = []
    for player in self.server.online_players:
        user = db.get_online_user(player.xuid)
        if has_log_perms(user.internal_rank) or config_tags.intersection(set(player.scoreboard_tags) or player.is_op):
            if db.enabled_logs(player.xuid):
                players_to_notify.append(player)

    # Send messages to players asynchronously
    if players_to_notify:
        threading.Thread(target=send_messages, args=(players_to_notify, message, db)).start()

    db.close_connection()  # Close the DB connection after everything is done
    return False

def send_messages(players, message, db):
    """Send the log message to all valid players asynchronously."""
    for player in players:
        player.send_message(message)

def discordRelay(message, type):
    """Send message to Discord asynchronously without blocking."""
    message = re.sub(r'§.', '', message)  # Clean up formatting

    config = load_config()
    discord_logging = config["modules"]["discord_logging"]

    webhook_url = get_webhook_url(type, discord_logging)
    if not webhook_url:
        return False  # No valid webhook found or enabled

    # Prepare the payload for Discord
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

    # Send Discord message asynchronously
    threading.Thread(target=send_discord_message, args=(webhook_url, payload)).start()
    return True

def get_webhook_url(type, discord_logging):
    """Helper function to get the appropriate webhook URL based on the message type."""
    if type == "cmd" and discord_logging["commands"]["enabled"]:
        return discord_logging["commands"]["webhook"]
    elif type == "mod" and discord_logging["moderation"]["enabled"]:
        return discord_logging["moderation"]["webhook"]
    elif type == "chat" and discord_logging["chat"]["enabled"]:
        return discord_logging["chat"]["webhook"]
    elif type == "grief" and discord_logging["griefing"]["enabled"]:
        return discord_logging["griefing"]["webhook"]
    return None

MAX_RETRIES = 15  # Max retries in case of rate limits
INITIAL_BACKOFF = 1  # Start with 1 second
def send_discord_message(webhook_url, payload):
    """Send HTTP request to Discord webhook with exponential backoff."""
    retries = 0
    backoff = INITIAL_BACKOFF  # Initial backoff time

    while retries < MAX_RETRIES:
        try:
            # Send the request to the Discord webhook
            response = requests.post(webhook_url, json=payload)

            # Raise an exception if response indicates a failure (4xx or 5xx)
            response.raise_for_status()

            # If request was successful, exit the loop
            return True
        except requests.exceptions.RequestException as e:
            # Check if rate limit (HTTP 429) occurred
            if response.status_code == 429:
                retries += 1
                wait_time = backoff * (2 ** retries)  # Exponential backoff
                print(f"[WMCTCORE - Discord Log] Rate limit exceeded. Retrying in {wait_time}s...")
                time.sleep(wait_time)  # Wait before retrying
            else:
                # For other exceptions (like network errors), just print and exit
                print(f"Failed to send Discord message: {e}")
                return False

    # If max retries were reached, log failure
    print("Max retries reached. Failed to send message.")
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


