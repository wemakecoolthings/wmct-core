from endstone import Player, GameMode
from endstone_wmctcore.utils.commandUtil import create_command
from endstone.command import CommandSender
from typing import TYPE_CHECKING
from endstone_wmctcore.utils.formWrapperUtil import (
    ActionFormData,
    ActionFormResponse,
)

from endstone_wmctcore.utils.configUtil import load_config
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

# SPECTATE COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    config = load_config()
    check_gamemode = config["modules"]["spectator_check"].get("check_gamemode", True)
    check_tags = config["modules"]["spectator_check"].get("check_tags", False)
    dead_tags = config["modules"]["spectator_check"].get("allow_tags", [])
    ignore_tags = config["modules"]["spectator_check"].get("ignore_tags", [])

    if not isinstance(sender, Player):
        sender.send_error_message("This command can only be executed by a player.")
        return False

    # Validate sender eligibility based on config
    if check_gamemode and sender.game_mode != GameMode.SPECTATOR:
        sender.send_message(f"{infoLog()}You are not currently a spectator!")
        return True
    if check_tags and not any(tag in sender.scoreboard_tags for tag in dead_tags):
        sender.send_message(f"{infoLog()}You are not currently a spectator!")
        return True

    def is_valid_spectate_target(player: Player) -> bool:
        """Returns True if the player is a valid spectate target based on config settings."""
        if check_gamemode and player.game_mode == GameMode.SPECTATOR:
            return False
        if check_tags:
            if not any(tag in player.scoreboard_tags for tag in dead_tags):
                return False
            if any(tag in player.scoreboard_tags for tag in ignore_tags):
                return False
        return True

    if len(args) == 0:
        # Spectate menu logic
        players_to_spectate = [p for p in self.server.online_players if is_valid_spectate_target(p)]
        if players_to_spectate:
            form = ActionFormData()
            form.title("Spectate Menu")
            form.body("Select a player to spectate!")

            for player in players_to_spectate:
                form.button(player.name_tag)

            def submit(player: Player, result: ActionFormResponse):
                if not result.canceled:
                    try:
                        selected_index = int(result.selection)
                        if 0 <= selected_index < len(players_to_spectate):
                            warp_player(player, players_to_spectate[selected_index])
                        else:
                            player.send_message(f"{infoLog()}Invalid selection.")
                    except ValueError:
                        player.send_message(f"{infoLog()}Invalid selection index.")

            form.show(sender).then(lambda player=sender, result=ActionFormResponse: submit(player, result))
        else:
            sender.send_message(f"{infoLog()}No players available to spectate.")
        return True
    else:
        # Direct teleport logic
        target_name = args[0]
        target = self.server.get_player(target_name)

        if target is None or not is_valid_spectate_target(target):
            sender.send_message(f"{infoLog()}Player {target_name} is not available to spectate.")
            return False

        warp_player(sender, target)
        return True


def warp_player(sender: Player, target: Player):
    """Warp the sender to the target player."""
    sender.teleport(target.location)
    sender.send_message(f"{infoLog()}Now spectating {target.name_tag}")
