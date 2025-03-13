import time

from endstone.event import BlockPlaceEvent, BlockBreakEvent, PlayerInteractEvent, DataPacketSendEvent, DataPacketReceiveEvent
from typing import TYPE_CHECKING

from endstone_wmctcore.utils.configUtil import load_config
from endstone_wmctcore.utils.loggingUtil import sendGriefLog
from endstone_wmctcore.utils.dbUtil import GriefLog

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

def handle_block_break(self: "WMCTPlugin", ev: BlockBreakEvent):
    config = load_config()
    is_gl_enabled = config["modules"]["grieflog"]["enabled"]

    if is_gl_enabled:
        dbgl = GriefLog("wmctcore_gl.db")

        if dbgl.get_user_toggle(ev.player.xuid, ev.player.name)[3]:
            logs = dbgl.get_logs_by_coordinates(ev.block.x, ev.block.y, ev.block.z)
            sendGriefLog(logs, ev.player)
            ev.is_cancelled = True
        else:
            block_states = list(ev.block.data.block_states.values())
            formatted_block_states = ", ".join(block_states)
            dbgl.log_action(ev.player.xuid, ev.player.name, "Block Break", ev.block.location, int(time.time()), ev.block.data.type, formatted_block_states)

        dbgl.close_connection()

    return True

def handle_block_place(self: "WMCTPlugin", ev: BlockPlaceEvent):
    config = load_config()
    is_gl_enabled = config["modules"]["grieflog"]["enabled"]

    if is_gl_enabled:
        dbgl = GriefLog("wmctcore_gl.db")

        if dbgl.get_user_toggle(ev.player.xuid, ev.player.name)[3]:
            logs = dbgl.get_logs_by_coordinates(ev.block.x, ev.block.y, ev.block.z)
            sendGriefLog(logs, ev.player)
            ev.is_cancelled = True
        else:
            placed_block = ev.block_placed_state
            block_states = list(placed_block.data.block_states.values())
            formatted_block_states = ", ".join(block_states)
            dbgl.log_action(ev.player.xuid, ev.player.name, "Block Place", placed_block.location, int(time.time()), placed_block.type, formatted_block_states)

        dbgl.close_connection()
    return True

last_interaction_time = {}
def handle_player_interact(self: "WMCTPlugin", ev: PlayerInteractEvent):
    config = load_config()
    is_gl_enabled = config["modules"]["grieflog"]["enabled"]

    if is_gl_enabled:
        dbgl = GriefLog("wmctcore_gl.db")

        current_time = time.time()  # Get the current time in seconds
        last_time = last_interaction_time.get(ev.player.xuid, 0)

        if current_time - last_time < 0.5:
            return True

        last_interaction_time[ev.player.xuid] = current_time

        types_to_check = ["chest", "barrel", "furnace", "table", "crafter", "shulker", "smoker",
                          "dispenser", "dropper", "hopper", "command", "lectern", "stonecutter",
                          "grindstone", "anvil", "beacon"]  # List of types to check
        if dbgl.get_user_toggle(ev.player.xuid, ev.player.name)[3]:
            logs = dbgl.get_logs_by_coordinates(ev.block.x, ev.block.y, ev.block.z)
            sendGriefLog(logs, ev.player)
            ev.is_cancelled = True
        elif any(item in ev.block.data.type for item in types_to_check):
            block_states = list(ev.block.data.block_states.values())
            formatted_block_states = ", ".join(block_states)
            dbgl.log_action(ev.player.xuid, ev.player.name, "Opened Container", ev.block.location, int(time.time()), ev.block.data.type, formatted_block_states)

        dbgl.close_connection()
    return True