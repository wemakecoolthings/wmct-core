from endstone import Player
from endstone.command import CommandSender
from endstone_primebds.utils.commandUtil import create_command

from typing import TYPE_CHECKING

from endstone_primebds.utils.prefixUtil import errorLog

if TYPE_CHECKING:
    from endstone_primebds.primebds import PrimeBDS

# Register command
command, permission = create_command(
    "gmsp",
    "Sets your game mode to spectator!",
    ["/gmsp [player: player]", "/gmsp (all)[selector: All]"],
    ["primebds.command.gmsp"]
)

# GMSP COMMAND FUNCTIONALITY
def handler(self: "PrimeBDS", sender: CommandSender, args: list[str]) -> bool:
    if len(args) == 0:
        if not isinstance(sender, Player):
            sender.send_message(f"{errorLog()}This command can only be executed by a player")
            return False
        target = self.server.get_player(sender.name)
        target.perform_command("gamemode spectator @s")

    elif len(args) == 1:
        target_name = args[0].lower()

        if target_name == "all":
            sender.perform_command("gamemode spectator @a")

        else:
            target = self.server.get_player(target_name)
            if target:
                sender.perform_command(f"gamemode spectator {target_name}")
            else:
                sender.send_message(f"Player {target_name} not found.")

    else:
        sender.send_message(f"{errorLog()}Invalid arguments. Usage: /gmsp [player] or /gmsp [all]")
        return False

    return True
