import time

from endstone.event import PlayerLoginEvent, PlayerJoinEvent, PlayerQuitEvent, PlayerKickEvent
from typing import TYPE_CHECKING

from datetime import datetime

from endstone_primebds.utils.configUtil import load_config
from endstone_primebds.utils.modUtil import format_time_remaining, ban_message
from endstone_primebds.utils.dbUtil import UserDB, GriefLog
from endstone.util import Vector

if TYPE_CHECKING:
    from endstone_primebds.primebds import PrimeBDS

def handle_login_event(self: "PrimeBDS", ev: PlayerLoginEvent):

    # Ban System: ENHANCEMENT
    db = UserDB("userInfo.db")
    now = datetime.now()

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

def handle_join_event(self: "PrimeBDS", ev: PlayerJoinEvent):

    # Update Saved Data
    db = UserDB("userInfo.db")
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
            dbgl = GriefLog("grieflog.db")
            dbgl.start_session(ev.player.xuid, ev.player.name, int(time.time()))
            rounded_x = round(ev.player.location.x)
            rounded_y = round(ev.player.location.y)
            rounded_z = round(ev.player.location.z)
            rounded_coords = Vector(rounded_x, rounded_y, rounded_z)
            dbgl.log_action(ev.player.xuid, ev.player.name, "Login", rounded_coords, int(time.time()))
            dbgl.close_connection()

    db.close_connection()
    return

def handle_leave_event(self: "PrimeBDS", ev: PlayerQuitEvent):

    # Update Data On Leave
    db = UserDB("userInfo.db")
    db.update_user_data(ev.player.name, 'last_leave', int(time.time()))

    # Ban System: ENHANCEMENT
    mod_log = db.get_mod_log(ev.player.xuid)
    if mod_log:
        if mod_log.is_banned:
            ev.quit_message = ""  # Remove join message
        else:
            # User Log
            dbgl = GriefLog("grieflog.db")
            dbgl.end_session(ev.player.xuid, int(time.time()))
            rounded_x = round(ev.player.location.x)
            rounded_y = round(ev.player.location.y)
            rounded_z = round(ev.player.location.z)
            rounded_coords = Vector(rounded_x, rounded_y, rounded_z)
            dbgl.log_action(ev.player.xuid, ev.player.name, "Logout", rounded_coords, int(time.time()))
            dbgl.close_connection()

    db.close_connection()
    return

def handle_kick_event(self: "PrimeBDS", ev: PlayerKickEvent):
    print(ev.player.name, ev.reason)
    dbgl = GriefLog("grieflog.db")
    dbgl.end_session(ev.player.xuid, int(time.time()))
    dbgl.close_connection()