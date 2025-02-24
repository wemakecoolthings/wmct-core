from endstone import Player, ColorFormat
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.prefixUtil import infoLog, trailLog, errorLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "permban",
    "Permanently bans a player from the server!",
    ["/permban <player: player> [reason: message]"],
    ["wmctcore.command.permban"],
    "op"
)

# PING COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:

    player_name = args[0].strip('"')

    if player_name.lower() == "all":
        players = self.server.online_players
        if not players:
            sender.send_message(f"{infoLog()}No players are online.")
            return True
        else:

            return True

    else:
        target = sender.server.get_player(player_name)
        if target is None:

            # Check Offline DB

            return True

        sender.send_message(f"test")

    return True

