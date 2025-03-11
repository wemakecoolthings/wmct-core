from endstone import Player
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.prefixUtil import infoLog, errorLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "reloadscripts",
    "Reloads the server scripts!",
    ["/reloadscripts"],
    ["wmctcore.command.reloadscripts"]
)

# RELOADSCRIPTS COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    self.server.reload_data()
    sender.send_message(f"{infoLog()}Server scripts were reloaded!")
    return True
