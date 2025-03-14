from endstone import Player
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command

from typing import TYPE_CHECKING

from endstone_wmctcore.utils.prefixUtil import errorLog

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "gma",
    "Sets your game mode to adventure!",
    ["/gma [player: player]", "/gma (all)[selector: All]"],
    ["wmctcore.command.gma"]
)

# GMA COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    if len(args) == 0:
        if not isinstance(sender, Player):
            sender.send_message(f"{errorLog()}This command can only be executed by a player")
            return False
        target = self.server.get_player(sender.name)
        target.perform_command("gamemode a @s") 

    elif len(args) == 1:
        target_name = args[0].lower()

        if target_name == "all":
            sender.perform_command("gamemode a @a")

        else:
            target = self.server.get_player(target_name)
            if target:
                sender.perform_command(f"gamemode a {target_name}")
            else:
                sender.send_message(f"{errorLog()}Player {target_name} not found.")

    else:
        sender.send_message(f"{errorLog()}Invalid arguments. Usage: /gma [player] or /gma [all]")
        return False

    return True
