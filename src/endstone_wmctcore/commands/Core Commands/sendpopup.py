from endstone import Player, ColorFormat
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.prefixUtil import infoLog, errorLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "sendpopup",
    "Sends a custom popup message!",
    ["/sendpopup <player: player> <text: message>", "/sendpopup (all)<selector: All> <text: message>"],
    ["wmctcore.command.sendpopup"]
)

# REFRESH COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:

    if args[0] == "all":
        for player in self.server.online_players:
            player.send_tip(args[1])
        sender.send_message(f"{infoLog()}A popup packet was sent to all players")
    else:
        player = self.server.get_player(args[0])
        if player:
            player.send_popup(args[1])
            sender.send_message(f"{infoLog()}A popup packet was sent to {ColorFormat.YELLOW}{player.name}")
        else:
            sender.send_message(f"{infoLog()}A popup packet could not be sent")

    return True
