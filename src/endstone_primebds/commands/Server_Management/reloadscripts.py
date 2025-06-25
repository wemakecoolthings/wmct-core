from endstone import Player
from endstone.command import CommandSender
from endstone_primebds.utils.commandUtil import create_command
from endstone_primebds.utils.prefixUtil import infoLog, errorLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_primebds.primebds import PrimeBDS

# Register command
command, permission = create_command(
    "reloadscripts",
    "Reloads the server scripts!",
    ["/reloadscripts"],
    ["primebds.command.reloadscripts"]
)

# RELOADSCRIPTS COMMAND FUNCTIONALITY
def handler(self: "PrimeBDS", sender: CommandSender, args: list[str]) -> bool:
    self.server.reload_data()
    sender.send_message(f"{infoLog()}Server scripts were reloaded!")
    return True
