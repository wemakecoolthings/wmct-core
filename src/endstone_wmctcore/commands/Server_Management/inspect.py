from endstone import Player, ColorFormat
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.dbUtil import GriefLog
from endstone_wmctcore.utils.prefixUtil import infoLog, errorLog, griefLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "inspect",
    "Toggles inspect mode on and off for the player.",
    ["/inspect"],
    ["wmctcore.command.inspect"]
)

# INSPECT COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    if isinstance(sender, Player):
        dbgl = GriefLog("wmctcore_gl.db")
        player = self.server.get_player(sender.name)

        # Get the current toggle value (True or False)
        toggle = dbgl.get_user_toggle(player.xuid, player.name)[3]
        toggle = not toggle

        # Update the toggle in the database
        dbgl.set_user_toggle(player.xuid, player.name)

        # Send a message based on the new toggle state
        if toggle:
            sender.send_message(f"{griefLog()}Inspect mode {ColorFormat.GREEN}Enabled")
        else:
            sender.send_message(f"{griefLog()}Inspect mode {ColorFormat.RED}Disabled")

        dbgl.close_connection()

    else:
        sender.send_error_message("This command can only be executed by a player")

    return True

