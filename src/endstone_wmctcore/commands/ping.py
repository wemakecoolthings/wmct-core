from endstone import Player, ColorFormat
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import usage, create_command
from endstone_wmctcore.utils.prefixUtil import infoLog

# Register command
command, permission = create_command(
    "ping",
    "Checks the server ping!",
    ["[player: player]", "(ALL)[selector: All]"],
    ["wmctcore.command.ping"]
)

# PING COMMAND FUNCTIONALITY
def handler(sender: CommandSender, args: list[str]) -> bool:
    if len(args) == 0:
        if not isinstance(sender, Player):
            sender.send_error_message("This command can only be executed by a player")
            return False
        target = sender
    else:
        player_name = args[0].strip('"')
        target = sender.server.get_player(player_name)
        if target is None:
            sender.send_error_message(f"Player {player_name} not found.")
            return True

    ping = target.ping
    ping_color = (
        ColorFormat.GREEN if ping <= 80 else
        ColorFormat.YELLOW if ping <= 160 else
        ColorFormat.RED
    )

    sender.send_message(
        f"{infoLog()}The ping of {target.name} is {ping_color}{ping}{ColorFormat.RESET}ms"
    )
    return True
