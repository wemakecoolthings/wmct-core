from endstone import Player
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command

from typing import TYPE_CHECKING

from endstone_wmctcore.utils.prefixUtil import errorLog

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "gms",
    "Sets your game mode to survival!",
    ["/gms [player: player]", "/gms (all)[selector: All]"],
    ["wmctcore.command.gms"]
)

# GMS COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    if len(args) == 0:
        if not isinstance(sender, Player):
            sender.send_message(f"{errorLog()}This command can only be executed by a player")
            return False
        target = self.server.get_player(sender.name)
        target.perform_command("gamemode s @s")

    elif len(args) == 1:
        target_name = args[0].lower()

        if target_name == "all":
            sender.perform_command("gamemode s @a")

        else:
            target = self.server.get_player(target_name)
            if target:
                sender.perform_command(f"gamemode s {target_name}")
            else:
                sender.send_message(f"Player {target_name} not found.")

    else:
        sender.send_error_message(f"{errorLog()}Invalid arguments. Usage: /gms [player] or /gms [all]")
        return False

    return True
