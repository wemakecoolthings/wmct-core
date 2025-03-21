from datetime import datetime
from typing import TYPE_CHECKING

from endstone import ColorFormat
from endstone.event import PlayerChatEvent
from endstone_wmctcore.utils.loggingUtil import discordRelay
from endstone_wmctcore.utils.dbUtil import UserDB
from endstone_wmctcore.utils.modUtil import format_time_remaining
from endstone_wmctcore.utils.prefixUtil import modLog

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

def handle_chat_event(self: "WMCTPlugin", ev: PlayerChatEvent):
    discordRelay(f"**{ev.player.name}**: {ev.message}", "chat")

    mute_data = load_mute_from_db(ev.player.xuid)
    if not mute_data or not mute_data["is_muted"]:
        return True  # Player is not muted, allow chat

    # Handle mute expiration
    if not mute_data["is_permanent"] and mute_data["mute_time"] < datetime.now().timestamp():
        remove_expired_mute(ev.player.name)
        return True

    # Display mute message with remaining time
    if mute_data["is_permanent"]:
        ev.player.send_message(f"{modLog()}You are permanently muted for {ColorFormat.YELLOW}{mute_data['reason']}")
    else:
        ev.player.send_message(f"{modLog()}You are muted for \"{ColorFormat.YELLOW}{mute_data['reason']}{ColorFormat.GOLD}\" "
                               f"{ColorFormat.GOLD}which expires in {ColorFormat.YELLOW}{format_time_remaining(mute_data['mute_time'])}")

    ev.is_cancelled = True
    return False

def load_mute_from_db(xuid):
    """Fetch mute data directly from the database."""
    db = UserDB("wmctcore_users.db")
    mod_log = db.get_mod_log(xuid)
    db.close_connection()

    if not mod_log or not mod_log.is_muted:
        return None

    return {
        "is_muted": mod_log.is_muted,
        "reason": mod_log.mute_reason,
        "mute_time": mod_log.mute_time,
        "is_permanent": mod_log.mute_time > (datetime.now().timestamp() + (10 * 365 * 24 * 60 * 60))  # 10 years
    }

def remove_expired_mute(player_name):
    """Remove expired mute from the database."""
    db = UserDB("wmctcore_users.db")
    db.remove_mute(player_name)
    db.close_connection()
