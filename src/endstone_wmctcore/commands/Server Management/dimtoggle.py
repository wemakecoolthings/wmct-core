from endstone import Player
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.prefixUtil import infoLog, errorLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "dimtoggle",
    "Toggles dimension access to the nether or the end!",
    ["/dimtoggle (nether|the_end) [toggled: bool]"],
    ["wmctcore.command.dimtoggle"]
)

# DIMTP COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:

    return True
