from endstone import Player, ColorFormat
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.prefixUtil import infoLog, errorLog

from typing import TYPE_CHECKING
import threading

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

        specification = args[0] if len(args) > 0 else "on"  # Default specification if none provided

        # Check if the 'off' argument is passed to disable monitoring
        if specification.lower() == 'off':
            # Clear any active intervals for this player
            if sender.name in active_intervals:
                active_intervals[sender.name].set()
                del active_intervals[sender.name]  # Remove from the active intervals dictionary
                sender.send_message(f"{infoLog()}Monitoring has been turned off")
            else:
                sender.send_message(f"{infoLog()}No active monitoring found")
            return True

        # If the player wants to enable or re-enable monitoring, clear existing intervals
        if sender.name in active_intervals:
            active_intervals[sender.name].set()

        # Parse the specification and time arguments
        time = int(args[1]) if len(args) > 1 else 1  # Default time interval if not provided
        display = args[2] if len(args) > 2 else "tip"

        # Create a threading event to control loop
        stop_event = threading.Event()

        # Create a monitor function that calls itself recursively
        def monitor_interval():
            if stop_event.is_set():  # If stop_event is set, stop the loop
                return

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
            nearest_chunk = get_nearest_chunk(player, self.server.level)
            is_laggy = check_entities_in_chunk(self, nearest_chunk.x, nearest_chunk.z)

            if player.ping < 100:
                ping_color = ColorFormat.GREEN
            elif 100 <= player.ping <= 200:
                ping_color = ColorFormat.YELLOW
            else:
                ping_color = ColorFormat.RED

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
            your_chunk_str = f"{ColorFormat.GREEN}x={nearest_chunk.x}, z={nearest_chunk.z}"
            your_dim = f"{dim_color}{player.dimension.name}"

            if display == "tip":
                player.send_tip(f"{ColorFormat.AQUA}Server Monitor{ColorFormat.RESET}\n"
                                f"{ColorFormat.RESET}Level: {self.server.level.name} {ColorFormat.ITALIC}{ColorFormat.GRAY}(ver. {version_str}{ColorFormat.GRAY})\n"
                                f"{ColorFormat.RESET}TPS: {tps_str} {ColorFormat.RESET}\n"
                                f"{ColorFormat.RESET}MSPT: {mspt_str}\n"
                                f"{ColorFormat.RESET}Loaded Chunks: {chunk_str}\n"
                                f"{ColorFormat.RESET}Loaded Entities: {entity_str}\n"
                                f"{ColorFormat.RESET}--------------\n"
                                f"{ColorFormat.RESET}Your Ping: {ping_str}\n"
                                f"{ColorFormat.RESET}Current Chunk: {your_chunk_str}, {chunk_lag_str}\n"
                                f"{ColorFormat.RESET}Current DIM: {your_dim}")
            elif display == "toast":
                player.send_toast(
                    f"{ColorFormat.AQUA}Server Monitor",
                    f"{ColorFormat.RESET}TPS: {tps_str} {ColorFormat.GRAY}| {ColorFormat.RESET}Chunks: {chunk_str} {ColorFormat.GRAY}| {ColorFormat.RESET}Entities: {entity_str}"
                )

            # Call monitor_interval recursively after the time delay
            threading.Timer(time, monitor_interval).start()

        # Start the interval loop
        monitor_interval()

        # Save the stop_event to control the loop
        active_intervals[sender.name] = stop_event

        sender.send_message(f"{infoLog()}Started monitoring on an interval of {time} seconds")
        return True
    else:
        sender.send_error_message("This command can only be executed by a player")
    return True

def check_entities_in_chunk(self: "WMCTPlugin", target_chunk_x: int, target_chunk_z: int) -> bool:
    """Checks the number of entities in a specific chunk and returns True if the count exceeds 400."""
    # Initialize the count of entities in the target chunk
    entity_count = 0

    # Iterate over all entities to check if they are in the target chunk
    for entity in self.server.level.actors:
        # Get the chunk coordinates of the entity
        entity_chunk_x = entity.location.x // 16
        entity_chunk_z = entity.location.z // 16

        # Check if the entity is in the target chunk
        if entity_chunk_x == target_chunk_x and entity_chunk_z == target_chunk_z:
            entity_count += 1

    # Return True if the entity count exceeds 400
    return entity_count > 400

def get_nearest_chunk(player: Player, level):
    # Get the player's current chunk position
    player_chunk_x = player.location.x // 16
    player_chunk_z = player.location.z // 16

    # Get all loaded chunks for the level
    loaded_chunks = level.get_dimension(player.dimension.name).loaded_chunks

    # Initialize the closest chunk and minimum distance
    closest_chunk = None
    min_distance_sq = float('inf')  # Initialize with a large number

    # Iterate through each loaded chunk to find the nearest one
    for chunk in loaded_chunks:
        chunk_x, chunk_z = chunk.x, chunk.z  # Accessing .x and .z properties of the chunk

        # Calculate the squared distance between the player and the chunk
        distance_sq = (chunk_x - player_chunk_x) ** 2 + (chunk_z - player_chunk_z) ** 2

        # Update the closest chunk if a closer one is found
        if distance_sq < min_distance_sq:
            min_distance_sq = distance_sq
            closest_chunk = chunk

    return closest_chunk

def clear_all_intervals():
    """Clear all active intervals."""
    global active_intervals
    for player_name, stop_event in active_intervals.items():
        stop_event.set()  # Stop each interval by setting the event
    active_intervals.clear()  # Clear the dictionary of active intervals
