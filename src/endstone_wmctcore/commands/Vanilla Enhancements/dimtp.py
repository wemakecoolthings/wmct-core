from endstone import Player
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.prefixUtil import infoLog, errorLog

from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

DIM_SCALE = {
    "OVERWORLD": 1,
    "NETHER": 8,
    "THE_END": 1
}

HEIGHT_LIMITS = {
    "OVERWORLD": 320,
    "NETHER": 127,
    "THE_END": 255
}

# Register command
command, permission = create_command(
    "dimtp",
    "Teleports a player across dimensions!",
    ["/dimtp <player: player> (overworld|nether|the_end)<dim: dim> [pos: pos] [translate: bool]"],
    ["wmctcore.command.dimtp"]
)

def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    if not isinstance(sender, Player):
        sender.send_error_message(f"{errorLog()} This command can only be used by players.")
        return False

    if len(args) < 2:
        sender.send_error_message(f"{errorLog()} Usage: /dimtp <player> <overworld|nether|the_end> [x y z] [translate]")
        return False

    player_name, target_dim = args[0], args[1].upper()
    player = self.server.get_player(player_name)

    if not player:
        sender.send_error_message(f"{errorLog()} Player '{player_name}' not found.")
        return False

    if target_dim not in DIM_SCALE:
        sender.send_error_message(
            f"{errorLog()} Invalid dimension: {target_dim}. Must be overworld, nether, or the_end.")
        return False

    try:
        new_x, new_y, new_z = player.location.x, player.location.y, player.location.z
        translate = False

        if len(args) >= 5:
            new_x, new_y, new_z = float(args[2]), float(args[3]), float(args[4])

        if len(args) == 6:
            translate = args[5].lower() == "true"
    except ValueError:
        sender.send_error_message(f"{errorLog()} Coordinates must be numbers, and translate must be true or false.")
        return False

    if translate:
        scale_from = DIM_SCALE.get(player.dimension.name.upper(), 1)
        scale_to = DIM_SCALE.get(target_dim, 1)
        scale_factor = scale_from / scale_to
        new_x *= scale_factor
        new_z *= scale_factor

    new_y = max(-64, min(new_y, HEIGHT_LIMITS[target_dim]))  # Ensure Y-level is valid

    player.perform_command(f"execute in {target_dim.lower()} run tp \"{player.name}\" {new_x} {new_y} {new_z}")
    return True