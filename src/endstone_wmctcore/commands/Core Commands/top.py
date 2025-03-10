from endstone import Player
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.prefixUtil import errorLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

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
        sender.send_error_message(f"{errorLog()}This command can only be executed by a player.")
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
    x, z = int(pos.x), int(pos.z)

    # Use the new API function to get the highest block
    highest_y = player.dimension.get_highest_block_at(x, z).y

    # Ensure the highest block is within the valid Y range
    if highest_y < min_y:
        sender.send_message(f"{errorLog()}No valid open-air block found at this X, Z position.")
        return False

    # Ensure there is air above the highest block (safe teleport)
    if (
        player.dimension.get_block_at(x, highest_y + 1, z).type == "minecraft:air"
        and player.dimension.get_block_at(x, highest_y + 2, z).type == "minecraft:air"
    ):
        player.perform_command(f"tp {x} {highest_y + 1} {z}")
        return True
    else:
        sender.send_message(f"{errorLog()}No valid open-air block found at this X, Z position.")
        return False
