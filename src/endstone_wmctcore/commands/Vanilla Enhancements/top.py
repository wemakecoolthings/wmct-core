from endstone import Player
from endstone.util import Vector
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.prefixUtil import infoLog, errorLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Caching terrain height maps for optimization
terrain_cache = {}  # {(x, z): highest_y}

# Register command
command, permission = create_command(
    "top",
    "Warps you to the topmost block with air!",
    ["/top [min_y_level: int]"],
    ["wmctcore.command.top"]
)

# TOP COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    if not isinstance(sender, Player):
        sender.send_error_message(f"{errorLog()} This command can only be executed by a player.")
        return False

    player = self.server.get_player(sender.name)
    pos = player.location
    dimension = player.dimension.name

    # Set world height limits based on dimension
    if dimension == "Nether":
        world_height = 120
    elif dimension == "TheEnd":
        world_height = 255
    else:
        world_height = 320  # Overworld

    min_y = int(args[0]) if args else -63  # Default min_y to -63 if not provided
    x, z = int(pos.x), int(pos.z)  # Get player's X and Z coordinates

    # Check if terrain height is cached
    if (x, z) in terrain_cache:
        highest_y = terrain_cache[(x, z)]
    else:
        highest_y = None

        # Scan downward from build height
        for y in range(world_height, min_y - 1, -1):
            block = player.dimension.get_block_at(x, y, z)

            # Look for the first solid block
            if block.type != "minecraft:air":
                # Check for an air pocket above (ensures safe teleport)
                if (
                    player.dimension.get_block_at(x, y + 1, z).type == "minecraft:air"
                    and player.dimension.get_block_at(x, y + 2, z).type == "minecraft:air"
                ):
                    highest_y = y
                    terrain_cache[(x, z)] = highest_y  # Cache the result
                    break

    # If no valid solid block is found, return an error
    if highest_y is None:
        sender.send_message(f"{errorLog()} No valid open-air block found at this X, Z position.")
        return False

    # Teleport player to the **first open air space above** the highest solid block
    safe_y = highest_y + 1
    player.perform_command(f"tp {x} {safe_y} {z}")
    return True
