from endstone import Player, ColorFormat, Server
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.prefixUtil import infoLog, errorLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "monitor",
    "Monitor server performance in real time!",
    ["/monitor (on|off)[toggle: toggle] [time_in_seconds: int] (tip|toast)[display: packet_type]"],
    ["wmctcore.command.monitor"]
)

# Dictionary to store active intervals for each player
active_intervals = {}

# MONITOR COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    if isinstance(sender, Player):

        specification = args[0] if len(args) > 0 else "on" 

        # Check if the 'off' argument is passed to disable monitoring
        if specification.lower() == 'off':
            # Clear any active intervals for this player
            if sender.name in active_intervals:
                # Cancel the active task
                task_id = active_intervals[sender.name]
                self.server.scheduler.cancel_task(task_id)
                del active_intervals[sender.name]  # Remove from the active intervals dictionary
                sender.send_message(f"{infoLog()}Monitoring has been turned off")
            else:
                sender.send_message(f"{infoLog()}No active monitoring found")
            return True

        # If the player wants to enable or re-enable monitoring, clear existing intervals
        if sender.name in active_intervals:
            task_id = active_intervals[sender.name]
            self.server.scheduler.cancel_task(task_id) 
            del active_intervals[sender.name]

        # Parse the specification and time arguments
        time = int(args[1]) if len(args) > 1 else 1  # Default time interval if not provided
        display = args[2] if len(args) > 2 else "tip"

        # Create a monitor function that calls itself recursively using the scheduler
        def monitor_interval():
            try:
                player = self.server.get_player(sender.name)

                # INFO PREP
                dim_color = ColorFormat.GREEN
                tps = self.server.average_tps
                mspt = self.server.average_mspt  # Get the average MSTP
                mspt_cur = self.server.current_mspt
                tick_usage = self.server.average_tick_usage
                tps_display = int(tps)  # Integer part
                tps_fraction = int((tps - tps_display) * 10)  # First decimal place
                entity_count = len(self.server.level.actors)
                server_version = self.server.minecraft_version
                overworld_chunks = len(self.server.level.get_dimension("Overworld").loaded_chunks)
                nether_chunks = len(self.server.level.get_dimension("Nether").loaded_chunks)
                the_end_chunks = len(self.server.level.get_dimension("TheEnd").loaded_chunks)
                nearest_chunk, player_chunk_x, player_chunk_z = get_nearest_chunk(player, self.server.level)
                is_laggy = check_entities_in_chunk(self, nearest_chunk.x, nearest_chunk.z)

                ping_color = get_ping_color(player.ping)

                if tps > 18:
                    tps_color = ColorFormat.GREEN
                elif 14 <= tps <= 18:
                    tps_color = ColorFormat.YELLOW
                else:
                    tps_color = ColorFormat.RED

                if mspt < 50:
                    mspt_color = ColorFormat.GREEN
                else:
                    mspt_color = ColorFormat.RED

                if mspt_cur < 50:
                    mspt_cur_color = ColorFormat.GREEN
                else:
                    mspt_cur_color = ColorFormat.RED

                if entity_count < 600:
                    entity_color = ColorFormat.GREEN
                elif 600 <= entity_count <= 800:
                    entity_color = ColorFormat.YELLOW
                else:
                    entity_color = ColorFormat.RED

                if player.dimension.name == "Overworld":
                    dim_color = ColorFormat.GREEN
                elif player.dimension.name == "Nether":
                    dim_color = ColorFormat.Red
                elif player.dimension.name == "TheEnd":
                    dim_color = ColorFormat.MATERIAL_IRON

                if not is_laggy:
                    chunk_lag_str = f"§aO"
                else:
                    chunk_lag_str = f"§cX"

                # FINAL STRINGS
                tps_str = f"{tps_color}{tps_display}.{tps_fraction:1d} {ColorFormat.ITALIC}{ColorFormat.GRAY}({tick_usage:.1f})"
                ping_str = f"{ping_color}{player.ping // 1}ms"
                mspt_str = f"{mspt_color}{mspt:.1f}ms {ColorFormat.ITALIC}{ColorFormat.GRAY}(avg) {ColorFormat.RESET}{ColorFormat.GRAY}| {mspt_cur_color}{mspt_cur:.1f}ms {ColorFormat.ITALIC}{ColorFormat.GRAY}(cur)"
                entity_str = f"{entity_color}{entity_count}"
                version_str = f"{ColorFormat.GREEN}{server_version}"
                chunk_str = f"{ColorFormat.GREEN}{overworld_chunks} {ColorFormat.GRAY}| {ColorFormat.RED}{nether_chunks} {ColorFormat.GRAY}| {ColorFormat.MATERIAL_IRON}{the_end_chunks}"
                your_chunk_str = f"{ColorFormat.GREEN}x={player_chunk_x}, z={player_chunk_z}"
                your_dim = f"{dim_color}{player.dimension.name}"

                if display == "tip":
                    player.send_tip(f"{ColorFormat.AQUA}Server Monitor{ColorFormat.RESET}\n"
                                    f"{ColorFormat.RESET}---------------------------\n"
                                    f"{ColorFormat.RESET}Level: {self.server.level.name} {ColorFormat.ITALIC}{ColorFormat.GRAY}(ver. {version_str}{ColorFormat.GRAY})\n"
                                    f"{ColorFormat.RESET}TPS: {tps_str} {ColorFormat.RESET}\n"
                                    f"{ColorFormat.RESET}MSPT: {mspt_str}\n"
                                    f"{ColorFormat.RESET}Loaded Chunks: {chunk_str}\n"
                                    f"{ColorFormat.RESET}Loaded Entities: {entity_str}\n"
                                    f"{ColorFormat.RESET}---------------------------\n"
                                    f"{ColorFormat.RESET}Your Ping: {ping_str}\n"
                                    f"{ColorFormat.RESET}Current Chunk: {your_chunk_str}, {chunk_lag_str}\n"
                                    f"{ColorFormat.RESET}Current DIM: {your_dim}")
                elif display == "toast":
                    player.send_toast(
                        f"{ColorFormat.AQUA}Server Monitor",
                        f"{ColorFormat.RESET}TPS: {tps_str} {ColorFormat.GRAY}| {ColorFormat.RESET}Chunks: {chunk_str} {ColorFormat.GRAY}| {ColorFormat.RESET}Entities: {entity_str}"
                    )

                # Re-run the monitor_interval using the scheduler after the time delay
                task_id = self.server.scheduler.run_task(
                    self, monitor_interval, delay=time*20  # time*20 for 1 tick = 1 second
                )

                # Store the task id for future cancellation
                active_intervals[sender.name] = task_id.task_id
            except RuntimeError as e:
                clear_invalid_intervals(self)

        # Start the interval loop using the scheduler
        monitor_interval()

        sender.send_message(f"{infoLog()}Started monitoring on an interval of {time} seconds")
        return True
    else:
        sender.send_error_message("This command can only be executed by a player")
    return True

def get_ping_color(ping: int) -> str:
    """Returns the color formatting based on ping value."""
    return (
        ColorFormat.GREEN if ping <= 80 else
        ColorFormat.YELLOW if ping <= 160 else
        ColorFormat.RED
    )

def check_entities_in_chunk(self: "WMCTPlugin", target_chunk_x: int, target_chunk_z: int) -> bool:
    """Checks the number of entities in a specific chunk and returns True if the count exceeds 400."""
    entity_count = 0

    for entity in self.server.level.actors:
        entity_chunk_x = entity.location.x // 16
        entity_chunk_z = entity.location.z // 16

        if entity_chunk_x == target_chunk_x and entity_chunk_z == target_chunk_z:
            entity_count += 1

    return entity_count > 400

def get_nearest_chunk(player: Player, level):
    player_chunk_x = int(player.location.x) // 16 if player.location and player.location.x is not None else 0
    player_chunk_z = int(player.location.z) // 16 if player.location and player.location.z is not None else 0

    loaded_chunks = level.get_dimension(player.dimension.name).loaded_chunks if level else []

    if not loaded_chunks:
        return 0, player_chunk_x, player_chunk_z  

    # Initialize closest chunk tracking
    closest_chunk = None
    min_distance_sq = float('inf')

    # Iterate through each loaded chunk
    for chunk in loaded_chunks:
        chunk_x, chunk_z = getattr(chunk, "x", 0), getattr(chunk, "z", 0) 

        # Compute squared Euclidean distance
        dx = chunk_x - player_chunk_x
        dz = chunk_z - player_chunk_z
        distance_sq = dx * dx + dz * dz

        # Check if this is the closest chunk so far
        if distance_sq < min_distance_sq:
            min_distance_sq = distance_sq
            closest_chunk = chunk

    # Default to chunk (0,0) if no valid chunk is found
    closest_chunk = closest_chunk or type("Chunk", (), {"x": 0, "z": 0})()

    return closest_chunk, player_chunk_x, player_chunk_z

def clear_all_intervals(self: "WMCTPlugin"):
    """Clear all active intervals."""
    global active_intervals
    for player_name, task_id in active_intervals.items():
        self.server.scheduler.cancel_task(task_id) 
    active_intervals.clear()

def clear_invalid_intervals(self: "WMCTPlugin"):
    """Clear all active intervals for players who are no longer online."""
    global active_intervals
    for player_name, task_id in list(active_intervals.items()):
        if not any(player.name == player_name for player in self.server.online_players):
            self.server.scheduler.cancel_task(task_id)
            del active_intervals[player_name]
