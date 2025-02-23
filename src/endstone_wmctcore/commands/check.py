from endstone import Player, ColorFormat
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.prefixUtil import infoLog, trailLog, errorLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "check",
    "Checks a player's client info!",
    ["/check <player: player>", "/check (all)<selector: All>"],
    ["wmctcore.command.check"]
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

    elif player_name.lower() == "offline":

        return True

    else:
        target = sender.server.get_player(player_name)
        if target is None:
            sender.send_error_message(f"{errorLog()}Player {player_name} not found.")
            return True

        sender.send_message(f"{self.user_db.get_online_user('users', target.xuid, 'device_os')}")
        sender.send_message(f"{self.user_db.get_offline_user('users', target.name, 'device_os')}")

    return True

