from endstone import Player, boss
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.prefixUtil import infoLog, errorLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "bossbar",
    "Sets a client sided bossbar display!",
    ["/bossbar <player: player> (red|blue|green|yellow|pink|purple|rebecca_purple|white)<color: color> (solid|segmented_6|segmented_10|segmented_12|segmented_20)<style: style> <title: string> [is_dark: bool]",
     "/bossbar (all)<selector: All> (red|blue|green|yellow|pink|purple|rebecca_purple|white)<color: color> (solid|segmented_6|segmented_10|segmented_12|segmented_20)<style: style> <title: string> [is_dark: bool]"],
    ["wmctcore.command.bossbar"]
)

# BOSSBAR COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:

    color = args[1].upper()
    style = args[2].upper()
    bar = self.server.create_boss_bar(args[3], boss.BarColor[color], boss.BarStyle[style])

    if args[0] == "all":
        for player in self.server.online_players:
            bar.add_player(player)
    else:
        target = self.server.get_player(args[0])
        bar.add_player(target)

    sender.send_message(f"{infoLog()}A {color} bossbar with a {style} style was set to {args[0]}!")
    return True
