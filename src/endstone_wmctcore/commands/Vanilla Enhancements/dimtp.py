from endstone import Player
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.prefixUtil import infoLog, errorLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

DIM_SCALE = {
    "OVERWORLD": 1,
    "NETHER": 8,     # Nether to Overworld scaling (1:8 ratio)
    "THE_END": 1     # The End doesn't scale with other dimensions
}

# Register command
command, permission = create_command(
    "dimtp",
    "Teleports a player across dimensions!",
    ["/dimtp (overworld|nether|the_end)<DIM: dim> [pos: pos]"],
    ["wmctcore.command.dimtp"]
)

# DIMTP COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    if not isinstance(sender, Player):
        sender.send_error_message(f"{errorLog()} This command can only be used by players.")
        return False

    if not args:
        sender.send_error_message(f"{errorLog()} Usage: /dimtp (overworld|nether|the_end) [x y z]")
        return False

    player = self.server.get_player(sender.name)
    current_dim = player.dimension.name.upper()
    target_dim = args[0].upper()

    if target_dim not in DIM_SCALE:
        sender.send_error_message(
            f"{errorLog()} Invalid dimension: {target_dim}. Must be overworld, nether, or the_end")
        return False

    # Set height limits per dimension
    height_limits = {
        "OVERWORLD": 320,
        "NETHER": 127,
        "THE_END": 255
    }

    # Get player's current position
    current_x, current_y, current_z = int(player.location.x), int(player.location.y), int(player.location.z)

    # Determine new coordinates
    if len(args) >= 4:
        # Player provided specific coordinates
        try:
            new_x, new_y, new_z = int(args[1]), int(args[2]), int(args[3])
        except ValueError:
            sender.send_error_message(f"{errorLog()} Invalid coordinates. Use numbers: /dimtp {target_dim} [x y z]")
            return False
    else:
        # Auto-translate coordinates based on dimension scaling
        scale_from = DIM_SCALE.get(current_dim, 1)
        scale_to = DIM_SCALE.get(target_dim, 1)
        scale_factor = scale_from / scale_to  # Convert position correctly

        new_x = int(current_x * scale_factor)
        new_y = min(int(current_y), height_limits[target_dim])  # Ensure within height limits
        new_z = int(current_z * scale_factor)

    # Ensure Y-level is valid
    new_y = max(-64, min(new_y, height_limits[target_dim]))

    # Execute teleport command
    player.perform_command(f"execute in {target_dim.lower()} run tp {player.name} {new_x} {new_y} {new_z}")
    return True