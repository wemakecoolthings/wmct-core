import time

from endstone.event import BlockPlaceEvent, BlockBreakEvent, PlayerInteractEvent
from typing import TYPE_CHECKING
from endstone_wmctcore.utils.loggingUtil import discordRelay, sendGriefLog
from endstone_wmctcore.utils.dbUtil import GriefLog
from endstone_wmctcore.utils.modUtil import format_time_remaining
from endstone_wmctcore.utils.prefixUtil import griefLog

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

def handle_block_break(self: "WMCTPlugin", ev: BlockBreakEvent):
    dbgl = GriefLog("wmctcore_gl.db")

    if dbgl.get_user_toggle(ev.player.xuid, ev.player.name)[3]:
        logs = dbgl.get_logs_by_coordinates(ev.block.x, ev.block.y, ev.block.z)
        sendGriefLog(logs, ev.player)
        ev.is_cancelled = True
    else:
        dbgl.log_action(ev.player.xuid, ev.player.name, "Block Break", ev.block.location, int(time.time()))

    dbgl.close_connection()
    return True

def handle_block_place(self: "WMCTPlugin", ev: BlockPlaceEvent):
    dbgl = GriefLog("wmctcore_gl.db")

    if dbgl.get_user_toggle(ev.player.xuid, ev.player.name)[3]:
        logs = dbgl.get_logs_by_coordinates(ev.block.x, ev.block.y, ev.block.z)
        sendGriefLog(logs, ev.player)
        ev.is_cancelled = True
    else:
        dbgl.log_action(ev.player.xuid, ev.player.name, "Block Break", ev.block.location, int(time.time()))

    dbgl.close_connection()
    return True

last_interaction_time = {}
def handle_player_interact(self: "WMCTPlugin", ev: PlayerInteractEvent):
    dbgl = GriefLog("wmctcore_gl.db")

    current_time = time.time()  # Get the current time in seconds
    last_time = last_interaction_time.get(ev.player.xuid, 0)

    if current_time - last_time < 0.5:
        return True

    last_interaction_time[ev.player.xuid] = current_time

    if dbgl.get_user_toggle(ev.player.xuid, ev.player.name)[3]:
        logs = dbgl.get_logs_by_coordinates(ev.block.x, ev.block.y, ev.block.z)
        sendGriefLog(logs, ev.player)
        ev.is_cancelled = True

    dbgl.close_connection()
    return True