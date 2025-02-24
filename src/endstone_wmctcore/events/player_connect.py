from endstone.event import PlayerLoginEvent, PlayerJoinEvent, PlayerQuitEvent
from typing import TYPE_CHECKING

from datetime import datetime
from endstone_wmctcore.utils.modUtil import format_time_remaining, ban_message
from endstone_wmctcore.utils.dbUtil import UserDB

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin


def handle_login_event(self: "WMCTPlugin", ev: PlayerLoginEvent):
    # Remove Overwritten Permissions
    self.reload_custom_perms()

    # Ban System: ENHANCEMENT
    db = UserDB("wmctcore_users.db")
    mod_log = db.get_mod_log(ev.player.xuid)

    if mod_log:
        if mod_log.is_banned:
            # Check if the ban has expired
            now = datetime.now()
            banned_time = datetime.fromtimestamp(mod_log.banned_time)

            if now >= banned_time:  # Ban has expired
                # Unban the player
                db.remove_ban(ev.player.xuid)  # Add a method to remove the ban from the database
                message = f"Your ban has expired. Welcome back, {ev.player.name}!"
                ev.kick_message = message  # Optionally notify the player
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

    # Ban System: ENHANCEMENT
    mod_log = db.get_mod_log(ev.player.xuid)
    if mod_log:
        if mod_log.is_banned:
            ev.join_message = "" # Remove join message

    db.close_connection()
    return

def handle_leave_event(self: "WMCTPlugin", ev: PlayerQuitEvent):

    # Update Data On Leave
    db = UserDB("wmctcore_users.db")
    db.save_user(ev.player)
    db.update_user_leave_data(ev.player.xuid)

    # Ban System: ENHANCEMENT
    mod_log = db.get_mod_log(ev.player.xuid)
    if mod_log:
        if mod_log.is_banned:
            ev.quit_message = ""  # Remove join message

    db.close_connection()
    return
