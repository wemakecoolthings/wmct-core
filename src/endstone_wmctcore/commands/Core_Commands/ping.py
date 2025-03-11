from endstone import Player, ColorFormat
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.prefixUtil import infoLog, trailLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "ping",
    "Checks the server ping!",
    ["/ping [player: player]", "/ping (all)[selector: All]"],
    ["wmctcore.command.ping"],
    "true"
)

# PING COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    if len(args) == 0:
        if not isinstance(sender, Player):
            sender.send_error_message("This command can only be executed by a player")
            return False
        target = sender
        ping = target.ping
        sender.send_message(
            f"{infoLog()}Your ping is {get_ping_color(ping)}{ping}{ColorFormat.RESET}ms"
        )
        return True

    player_name = args[0].strip('"')

    if player_name.lower() == "all":
        # Fetch and display all players' pings
        players = self.server.online_players
        if not players:
            sender.send_message(f"{infoLog()}No players are online.")
            return True

        ping_list = [
            f"{trailLog()}{player.name}: {get_ping_color(player.ping)}{player.ping}{ColorFormat.RESET}ms"
            for player in players
        ]
        sender.send_message(f"{infoLog()}Online Players' Pings:\n" + "\n".join(ping_list))
        return True

    # Handle single player lookup
    target = sender.server.get_player(player_name)
    if target is None:
        sender.send_error_message(f"Player {player_name} not found.")
        return True

    ping = target.ping
    sender.send_message(
        f"{infoLog()}The ping of {target.name} is {get_ping_color(ping)}{ping}{ColorFormat.RESET}ms"
    )
    return True


def get_ping_color(ping: int) -> str:
    """Returns the color formatting based on ping value."""
    return (
        ColorFormat.GREEN if ping <= 80 else
        ColorFormat.YELLOW if ping <= 160 else
        ColorFormat.RED
    )