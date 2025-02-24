from endstone.event import PlayerLoginEvent, PlayerJoinEvent, PlayerQuitEvent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

def handle_login_event(self: "WMCTPlugin", ev: PlayerLoginEvent):

    # Remove Overwritten Permissions
    self.reload_custom_perms()

    # Ban System: ENHANCEMENT

    return

def handle_join_event(self: "WMCTPlugin", ev: PlayerJoinEvent):

    # Update Saved Data
    self.user_db.save_user(ev.player)

    # Ban System: ENHANCEMENT

    return

def handle_leave_event(self: "WMCTPlugin", ev: PlayerQuitEvent):

    # Update Data On Leave
    self.user_db.save_user(ev.player)
    self.user_db.update_user_leave_data(ev.player.xuid)

    # Ban System: ENHANCEMENT
    return
