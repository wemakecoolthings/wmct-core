from endstone import Player
from endstone.command import CommandSender
from endstone_primebds.utils.commandUtil import create_command
from endstone_primebds.utils.prefixUtil import infoLog, errorLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_primebds.primebds import PrimeBDS

# Register command
command, permission = create_command(
    "refresh",
    "Refreshes your permissions to fix display issues!",
    ["/refresh"],
    ["primebds.command.refresh"],
    "true"
)

# REFRESH COMMAND FUNCTIONALITY
def handler(self: "PrimeBDS", sender: CommandSender, args: list[str]) -> bool:
    if isinstance(sender, Player):
        self.reload_custom_perms(sender)
        sender.send_message(f"{infoLog()}Client commands & permissions were reloaded!")
    else:
        sender.send_error_message("This command can only be executed by a player")
    return True
