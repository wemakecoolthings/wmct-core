from endstone import Player, ColorFormat
from endstone.command import CommandSender
from endstone_primebds.utils.commandUtil import create_command
from endstone_primebds.utils.prefixUtil import infoLog, errorLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_primebds.primebds import PrimeBDS

# Register command
command, permission = create_command(
    "nickname",
    "Sets a display nickname!",
    ["/nickname [nick: string]", "/nickname (remove)[remove_nick:remove_nick]"],
    ["primebds.command.nickname"],
    "op",
    ["nick"]
)

# NICK COMMAND FUNCTIONALITY
def handler(self: "PrimeBDS", sender: CommandSender, args: list[str]) -> bool:
    if not isinstance(sender, Player):
        sender.send_error_message(f"{errorLog()} This command can only be executed by a player.")
        return False

    player = self.server.get_player(sender.name)

    if not args:
        sender.send_message(f"{infoLog()}Your current nickname is: {ColorFormat.YELLOW}{player.name_tag}")
        return True

    if args[0].lower() == "remove":
        player.name_tag = player.name  # Reset nickname
        sender.send_message(f"{infoLog()}Your nickname has been reset to your original name: {ColorFormat.YELLOW}{player.name}")
    else:
        new_nick = args[0]
        if new_nick:
            player.name_tag = new_nick  # Set new nickname
            sender.send_message(f"{infoLog()}Your nickname was set to: {ColorFormat.YELLOW}{new_nick}")
        else:
            sender.send_error_message(f"{errorLog()} Nickname cannot be empty.")

    return True
