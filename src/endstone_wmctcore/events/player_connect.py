import time

from endstone.event import PlayerLoginEvent, PlayerJoinEvent, PlayerQuitEvent
from typing import TYPE_CHECKING

from datetime import datetime
from endstone_wmctcore.utils.modUtil import format_time_remaining, ban_message
from endstone_wmctcore.utils.dbUtil import UserDB, GriefLog

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

def handle_login_event(self: "WMCTPlugin", ev: PlayerLoginEvent):

    # Ban System: ENHANCEMENT
    db = UserDB("wmctcore_users.db")

    player_xuid = ev.player.xuid
    player_ip = str(ev.player.address)

    mod_log = db.get_mod_log(player_xuid)
    is_ip_banned = db.check_ip_ban(player_ip)

    # Handle IP Ban
    if is_ip_banned:
        banned_time = datetime.fromtimestamp(mod_log.banned_time)
        if now >= banned_time:  # IP Ban has expired
            db.remove_ban(player_ip)
        else:  # IP Ban is still active
            formatted_expiration = format_time_remaining(mod_log.banned_time)
            message = ban_message(self.server.level.name, formatted_expiration, "IP Ban - " + mod_log.ban_reason)
            ev.kick_message = message
            ev.is_cancelled = True  # Prevent login

    # Handle XUID Ban
    elif mod_log:
        if mod_log.is_banned:  # Only proceed if the player is banned
            banned_time = datetime.fromtimestamp(mod_log.banned_time)
            if now >= banned_time:  # Ban has expired
                db.remove_ban(player_xuid)
            else:  # Ban is still active
                formatted_expiration = format_time_remaining(mod_log.banned_time)
                message = ban_message(self.server.level.name, formatted_expiration, mod_log.ban_reason)
                ev.kick_message = message
                ev.is_cancelled = True  # Prevent login

    db.close_connection()
    return

def handle_join_event(self: "WMCTPlugin", ev: PlayerJoinEvent):

    # Update Saved Data
    db = UserDB("wmctcore_users.db")
    db.save_user(ev.player)
    db.update_user_data(ev.player.name, 'last_join', int(time.time()))
    self.reload_custom_perms(ev.player)

    # Ban System: ENHANCEMENT
    mod_log = db.get_mod_log(ev.player.xuid)
    if mod_log:
        if mod_log.is_banned:
            ev.join_message = "" # Remove join message
        else:
            # User Log
            dbgl = GriefLog("wmctcore_gl.db")
            dbgl.start_session(ev.player.xuid, ev.player.name, int(time.time()))
            dbgl.close_connection()

    db.close_connection()
    return

def handle_leave_event(self: "WMCTPlugin", ev: PlayerQuitEvent):

    # Update Data On Leave
    db = UserDB("wmctcore_users.db")
    db.update_user_data(ev.player.name, 'last_leave', int(time.time()))

    # Ban System: ENHANCEMENT
    mod_log = db.get_mod_log(ev.player.xuid)
    if mod_log:
        if mod_log.is_banned:
            ev.quit_message = ""  # Remove join message
        else:
            # User Log
            dbgl = GriefLog("wmctcore_gl.db")
            dbgl.end_session(ev.player.xuid, int(time.time()))
            dbgl.close_connection()

    db.close_connection()
    return
