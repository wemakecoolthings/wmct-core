from endstone import Player, ColorFormat
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.prefixUtil import infoLog, errorLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "attribute",
    "Modifies internal player NBT data!",
    ["/attribute <player: player> (flyspeed)<attribute: type_1> <value: float>",
            "/attribute <player: player> (fly)<attribute: type> <value: bool>"],
    ["wmctcore.command.attribute"]
)

# DEV NOTE: REMOVED WALKSPEED ARGUMENT AS IT IS CURRENTLY BUGGED

# ATTRIBUTE COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    # Check if the player exists
    player_name = args[0]
    player = self.server.get_player(player_name)

    if not player:
        # Send error message to the sender
        sender.send_message(f"{errorLog()}Player {player_name} not found!")
        return False

    # Handling flyspeed attribute
    if args[1].lower() == "flyspeed":
        try:
            new_fly_speed = float(args[2])
            original_fly_speed = player.fly_speed
            player.fly_speed = new_fly_speed
            player.send_message(f"{infoLog()}Flyspeeed changed: {ColorFormat.RED}{original_fly_speed} {ColorFormat.GRAY}-> {ColorFormat.GREEN}{new_fly_speed}")
            sender.send_message(f"{infoLog()}Player {player_name}'s flyspeed changed: {ColorFormat.RED}{original_fly_speed} {ColorFormat.GRAY}-> {ColorFormat.GREEN}{new_fly_speed}")
        except ValueError:
            sender.send_message(f"{errorLog()} Invalid fly speed value: {args[2]}")
            return False

    elif args[1].lower() == "walkspeed":
        try:
            new_walk_speed = float(args[2])
            original_walk_speed = player.walk_speed
            player.walk_speed = new_walk_speed
            player.send_message(f"{infoLog()}Walkspeeed changed: {ColorFormat.RED}{original_walk_speed} {ColorFormat.GRAY}-> {ColorFormat.GREEN}{new_walk_speed}")
            sender.send_message(f"{infoLog()}Player {player_name}'s walkspeed changed: {ColorFormat.RED}{original_walk_speed} {ColorFormat.GRAY}-> {ColorFormat.GREEN}{new_walk_speed}")
        except ValueError:
            sender.send_message(f"{errorLog()} Invalid fly speed value: {args[2]}")
            return False

    # Handling fly attribute
    elif args[1].lower() == "fly":
        try:
            new_fly_state = bool(args[2].lower() == "true")
            original_fly_state = player.is_flying
            player.allow_flight = new_fly_state
            player.send_message(f"{infoLog()}Fly state changed: {ColorFormat.RED}{original_fly_state} {ColorFormat.GRAY}-> {ColorFormat.GREEN}{new_fly_state}")
            sender.send_message(f"{infoLog()}Player {player_name}'s fly state changed: {ColorFormat.RED}{original_fly_state} {ColorFormat.GRAY}-> {ColorFormat.GREEN}{new_fly_state}")
        except ValueError:
            sender.send_message(f"{errorLog()}Invalid fly state value: {args[2]}")
            return False

    # Return True if the operation was successful
    return True
