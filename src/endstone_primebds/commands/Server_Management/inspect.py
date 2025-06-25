from endstone import Player, ColorFormat
from endstone.command import CommandSender
from endstone_primebds.utils.commandUtil import create_command
from endstone_primebds.utils.configUtil import load_config
from endstone_primebds.utils.dbUtil import GriefLog
from endstone_primebds.utils.prefixUtil import infoLog, errorLog, griefLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_primebds.primebds import PrimeBDS

# Register command
command, permission = create_command(
    "inspect",
    "Toggles inspect mode on and off for the player.",
    ["/inspect"],
    ["primebds.command.inspect"]
)

# INSPECT COMMAND FUNCTIONALITY
def handler(self: "PrimeBDS", sender: CommandSender, args: list[str]) -> bool:
    config = load_config()
    is_gl_enabled = config["modules"]["grieflog"]["enabled"]

    if not is_gl_enabled:
        sender.send_message(f"{errorLog()}Grief Logger is currently disabled by config")
        return True

    if isinstance(sender, Player):
        dbgl = GriefLog("primebds_gl.db")
        player = self.server.get_player(sender.name)

        toggle = dbgl.get_user_toggle(player.xuid, player.name)[3]
        toggle = not toggle

        dbgl.set_user_toggle(player.xuid, player.name)

        if toggle:
            sender.send_message(f"{griefLog()}Inspect mode {ColorFormat.GREEN}Enabled")
        else:
            sender.send_message(f"{griefLog()}Inspect mode {ColorFormat.RED}Disabled")

        dbgl.close_connection()

    else:
        sender.send_error_message("This command can only be executed by a player")

    return True

