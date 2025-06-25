from endstone import Player
from endstone.command import CommandSender
from endstone_primebds.utils.commandUtil import create_command
from endstone_primebds.utils.prefixUtil import errorLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_primebds.primebds import PrimeBDS

# Caching terrain height maps for optimization
terrain_cache = {}  # {(x, z): lowest_air_y}

# Register command
command, permission = create_command(
    "bottom",
    "Warps you to the nearest air pocket below you!",
    ["/bottom [min_y_level: int]"],
    ["primebds.command.bottom"]
)

# BOTTOM COMMAND FUNCTIONALITY
def handler(self: "PrimeBDS", sender: CommandSender, args: list[str]) -> bool:
    if not isinstance(sender, Player):
        sender.send_error_message(f"{errorLog()}This command can only be executed by a player.")
        return False

    player = self.server.get_player(sender.name)
    pos = player.location
    dimension = player.dimension.name

    # Set world height limits based on dimension
    if dimension == "Nether":
        world_bottom = 0
    elif dimension == "TheEnd":
        world_bottom = 0
    else:
        world_bottom = -63  # Overworld default bottom

    max_y = int(args[0]) if args else int(pos.y-2)  # Default to player's current Y level
    x, z = int(pos.x), int(pos.z)  # Get player's X and Z coordinates

    # Check if terrain height is cached
    if (x, z) in terrain_cache:
        lowest_air_y = terrain_cache[(x, z)]
    else:
        lowest_air_y = None

        # Scan downward from player's Y level
        for y in range(max_y, world_bottom - 1, -1):
            block = player.dimension.get_block_at(x, y, z)

            # Look for the first air block with solid ground below it
            if block.type == "minecraft:air":
                if player.dimension.get_block_at(x, y - 1, z).type != "minecraft:air":
                    lowest_air_y = y
                    terrain_cache[(x, z)] = lowest_air_y  # Cache the result
                    break

    # If no valid air pocket is found, return an error
    if lowest_air_y is None:
        sender.send_message(f"{errorLog()}No valid air pocket found at this X, Z position.")
        return False

    # Teleport player to the lowest detected air pocket
    player.perform_command(f"tp {x} {lowest_air_y} {z}")
    return True
