import threading
from datetime import datetime
from typing import TYPE_CHECKING

from endstone import ColorFormat
from endstone.event import PlayerChatEvent
from endstone_wmctcore.utils.loggingUtil import discordRelay
from endstone_wmctcore.utils.dbUtil import UserDB
from endstone_wmctcore.utils.modUtil import format_time_remaining
from endstone_wmctcore.utils.prefixUtil import modLog

# In-memory cache for mute status
mute_cache = {}

# Periodic cache cleanup interval (in minutes)
CACHE_CLEANUP_INTERVAL = 10

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

def handle_chat_event(self: "WMCTPlugin", ev: PlayerChatEvent):
    discordRelay(f"**{ev.player.name}**: {ev.message}", "chat")

    # Check cache and load from DB if not found
    mute_data = mute_cache.get(ev.player.xuid)
    if not mute_data:
        threading.Thread(target=load_mute_from_db, args=(ev.player.xuid,)).start()
        return True

    # Handle mute status
    if mute_data["is_permanent"]:
        ev.player.send_message(f"{modLog()}You are permanently muted for {ColorFormat.YELLOW}{mute_data['reason']}")
        ev.is_cancelled = True
        return False

    # Check mute expiration
    if datetime.fromtimestamp(mute_data['time']) < datetime.now():
        threading.Thread(target=remove_expired_mute, args=(ev.player.name,)).start()
        del mute_cache[ev.player.xuid]
        return True

    # Display mute message with remaining time
    ev.player.send_message(f"{modLog()}You are muted for \"{ColorFormat.YELLOW}{mute_data['reason']}\" "
                           f"{ColorFormat.GOLD}which expires in {ColorFormat.YELLOW}{format_time_remaining(mute_data['time'])}")
    ev.is_cancelled = True
    return False

def load_mute_from_db(xuid):
    """Fetch mute data from the database and cache it."""
    db = UserDB("wmctcore_users.db")
    mod_log = db.get_mod_log(xuid)
    db.close_connection()

    if not mod_log:
        return

    mute_cache[xuid] = {
        "reason": mod_log.mute_reason,
        "time": mod_log.mute_time,
        "is_permanent": mod_log.mute_time > (datetime.now().timestamp() + (365 * 100 * 24 * 60 * 60))
    }

def remove_expired_mute(player_name):
    """Remove expired mute from database and cache."""
    db = UserDB("wmctcore_users.db")
    db.remove_mute(player_name)
    db.close_connection()

def cleanup_cache():
    """Clear expired mutes from cache periodically."""
    now = datetime.now().timestamp()
    expired = [xuid for xuid, data in mute_cache.items() if data['time'] < now]
    for xuid in expired:
        del mute_cache[xuid]

def start_cache_cleanup():
    """Start a background thread to clean up expired mutes periodically."""
    import time
    while True:
        time.sleep(CACHE_CLEANUP_INTERVAL * 60)
        cleanup_cache()

# Start cache cleanup thread
threading.Thread(target=start_cache_cleanup, daemon=True).start()
