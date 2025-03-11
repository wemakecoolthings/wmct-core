from datetime import datetime
from typing import TYPE_CHECKING
import requests
import re
from endstone_wmctcore.utils.dbUtil import UserDB
from endstone_wmctcore.utils.internalPermissionsUtil import has_log_perms
from endstone_wmctcore.utils.configUtil import load_config

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
                "title": "Logger",
                "description": message,
                "color": 8388736,
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
