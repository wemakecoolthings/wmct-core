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

    # Ban System: ENHANCEMENT
    return

def handle_leave_event(self: "WMCTPlugin", ev: PlayerQuitEvent):

    # Ban System: ENHANCEMENT
    return
