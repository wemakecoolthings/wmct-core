from endstone import Player, GameMode
from endstone_wmctcore.utils.commandUtil import create_command
from endstone.command import CommandSender
from typing import TYPE_CHECKING
from endstone_wmctcore.utils.formWrapperUtil import (
    ActionFormData,
    ActionFormResponse,
)

from endstone_wmctcore.utils.prefixUtil import infoLog

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "spectate",
    "Warps you to a non-spectating player!",
    ["/spectate [player: player]"],
    ["wmctcore.command.spectate"],
    "true"
)

# PING COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    if sender.game_mode != GameMode.SPECTATOR:
        sender.send_message(f"{infoLog()}You are not currently a spectator!")
        return True

    if len(args) == 0:
        # No arguments passed
        if not isinstance(sender, Player):
            sender.send_error_message("This command can only be executed by a player.")
            return False

        # Get all players who are not in spectator mode
        players_to_spectate = [
            player for player in self.server.online_players if player.game_mode != GameMode.SPECTATOR
        ]

        # Create an ActionFormData menu
        if players_to_spectate:
            # Assuming 'sender' is a Player object
            form = ActionFormData()
            form.title("Spectate Menu")
            form.body("Select a player to spectate!")

            # Add buttons for each player to spectate
            for player in players_to_spectate:
                form.button(player.name)

            # Define the submit callback
            def submit(player: Player, result: ActionFormResponse):
                if not result.canceled:
                    # Convert the selection to an integer
                    try:
                        selected_player_index = int(result.selection)  # Convert the selection to an integer
                        if 0 <= selected_player_index < len(players_to_spectate):
                            selected_player = players_to_spectate[selected_player_index]
                            warp_player(player, selected_player)
                        else:
                            player.send_message(f"{infoLog()}No player selected or invalid selection.")
                    except ValueError:
                        player.send_message(f"{infoLog()}Invalid selection index.")

            # Show the form and handle the result asynchronously
            form.show(sender).then(
                lambda player=sender, result=ActionFormResponse: submit(player, result)
            )

        else:
            sender.send_message(f"{infoLog()}No players available to spectate.")

        return True

    else:
        # Argument passed - warp the player directly
        target_name = args[0]
        target = self.server.get_player(target_name)

        if target is None or target.game_mode == GameMode.SPECTATOR:
            sender.send_message(f"{infoLog()}Player {target_name} is not available to spectate.")
            return False

        # Warp the player to the target
        warp_player(sender, target)
        return True

def warp_player(sender: Player, target: Player):
    """Warp the sender to the target player."""
    sender.teleport(target.location)
    sender.send_message(f"{infoLog()}Now spectating {target.name}")

