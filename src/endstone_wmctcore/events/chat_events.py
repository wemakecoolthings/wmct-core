from endstone import ColorFormat
from endstone.event import PlayerChatEvent
from typing import TYPE_CHECKING

from datetime import timedelta, datetime
from endstone_wmctcore.utils.dbUtil import UserDB
from endstone_wmctcore.utils.modUtil import format_time_remaining
from endstone_wmctcore.utils.prefixUtil import modLog

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

def handle_chat_event(self: "WMCTPlugin", ev: PlayerChatEvent):
    db = UserDB("wmctcore_users.db")
    mod_log = db.get_mod_log(ev.player.xuid)
    if mod_log:
        if mod_log.is_muted:
            # Check if the mute is permanent (more than 100 years)
            mute_expiration = datetime.fromtimestamp(mod_log.mute_time)
            now = datetime.now()
            if mute_expiration > now + timedelta(days=365*100):  # Permanent mute (more than 100 years)
                ev.player.send_message(f"{modLog()}You are permanently muted for {ColorFormat.YELLOW}{mod_log.mute_reason}")
            else:
                formatted_expiration = format_time_remaining(mod_log.mute_time)
                ev.player.send_message(f"{modLog()}You are muted for {mod_log.mute_reason} for {formatted_expiration}")
            ev.is_cancelled = True
            return False

    return True