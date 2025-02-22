from endstone import ColorFormat, Player
from endstone.command import CommandSender, Command, CommandExecutor
from endstone_wmctcore.utils.prefixUtil import Prefix

# Define the command details
command = {
    "ping": {
        "description": "Checks the server ping!",
        "usages": ["/ping [target: player]"],
        "permissions": ["wmctcore.command.ping"]
    }
}

permission = {
    "wmctcore.command.ping": {
        "description": "Allows use of ping command",
        "default": "true"
    }
}

class Ping(CommandExecutor):
    def __init__(self, server):
        super().__init__()
        self.server = server

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        if len(args) == 0:
            if not isinstance(sender, Player):
                sender.send_error_message("This command can only be executed by a player")
                return False
            target = sender
        else:
            player_name = args[0].strip('"')
            if player_name == "@s":
                target = sender
            else:
                target = self.server.get_player(player_name)
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
            f"{Prefix.infoLog()}The ping of {target.name} is {ping_color}{ping}{ColorFormat.RESET}ms"
        )
        return True
