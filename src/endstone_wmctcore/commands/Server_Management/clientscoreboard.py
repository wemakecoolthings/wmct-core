from endstone._internal.endstone_python import DisplaySlot
from endstone.command import CommandSender
from endstone.scoreboard import Criteria
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.prefixUtil import infoLog
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "clientscoreboard",
    "Client-sided scoreboard system!",
    ["/clientscoreboard <player: player> (set|remove)<action: csb_action> <objective: string> <display_name: string> (sidebar|list|belowname)<slot: slot> <value: int>"],
    ["wmctcore.command.clientscoreboard"]
)

# CLIENTSCOREBOARD CMD FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    if len(args) < 4:  # Ensure there are enough arguments
        return False

    player_name, action, objective_name, display_name, slot, *value = args
    player = self.server.get_player(player_name)
    if not player:
        return False

    value = int(value[0]) if value else 100

    if action == "set":
        if slot == "sidebar":
            slot = DisplaySlot.SIDE_BAR
        elif slot == "list":
            slot = DisplaySlot.PLAYER_LIST
        elif slot == "belowname":
            slot = DisplaySlot.BELOW_NAME
        add_score(player, objective_name, display_name, slot, value)
        action_text = "added"
    elif action == "remove":
        remove_score(player, objective_name)
        action_text = "removed"
    else:
        return False

    sender.send_message(f"{infoLog()}Client scoreboard was {action_text} for {player_name} with the "
                         f"objective '{objective_name}', display name '{display_name}', and a value of {value if value else 'N/A'}.")

def add_score(player, objective: str, display_name: str, slot: int, value: int) -> bool:
    criteria = Criteria.DUMMY
    if player.scoreboard.get_objective(objective):
        objective = player.scoreboard.get_objective(objective)
    else:
        objective = player.scoreboard.add_objective(objective, criteria, display_name)

    objective.get_score(player).value = value
    objective.set_display(slot)
    return True

def remove_score(player, objective: str) -> bool:
    player.scoreboard.get_objective(objective).reset_scores()
    return True