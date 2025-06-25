from endstone import Player, ColorFormat
from endstone.command import CommandSender
from endstone_primebds.utils.commandUtil import create_command
from endstone_primebds.utils.prefixUtil import infoLog, errorLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_primebds.primebds import PrimeBDS

# Register command
command, permission = create_command(
    "sendtoast",
    "Sends a custom toast message!",
    ["/sendtoast <player: player> <title: string> <text: message>", "/sendtoast (all)<selector: All> <title: string> <text: message>"],
    ["primebds.command.sendtoast"]
)

# REFRESH COMMAND FUNCTIONALITY
def handler(self: "PrimeBDS", sender: CommandSender, args: list[str]) -> bool:

    if args[0] == "all":
        for player in self.server.online_players:
            player.send_toast(args[1], args[2])
        sender.send_message(f"{infoLog()}A toast packet was sent to all players")
    else:
        player = self.server.get_player(args[0])
        if player:
            player.send_toast(args[1], args[2])
            sender.send_message(f"{infoLog()}A toast packet was sent to {ColorFormat.YELLOW}{player.name}")
        else:
            sender.send_message(f"{infoLog()}A toast packet could not be sent")

    return True
