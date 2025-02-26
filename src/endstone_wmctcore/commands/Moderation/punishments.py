from endstone import ColorFormat, Player
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command

from typing import TYPE_CHECKING, Optional

from endstone_wmctcore.utils.dbUtil import UserDB
from endstone_wmctcore.utils.formWrapperUtil import ActionFormResponse, ActionFormData
from endstone_wmctcore.utils.prefixUtil import modLog, errorLog

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "punishments",
    "Manage punishment history of a specified player!",
    ["/punishments <player: player> [page: int]",
     "/punishments (remove|clear) <punishment_removal: remove_punishment_log>"],
    ["wmctcore.command.punishments"]
)


def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    """Command to fetch or remove a player's punishment history."""

    if not args:
        sender.send_message(
            ColorFormat.red("Usage: /punishments <player> [page] OR /punishments (remove|clear)"))
        return False

    action = args[0].lower()

    db = UserDB("wmctcore_users.db")

    if action == "remove":
        remove_punishment(self, sender, args)
        return True

    elif action == "clear":
        remove_punishment(self, sender, args)
        return True

    # Retrieve punishment history
    target_name = args[0]
    page = int(args[1]) if len(args) > 1 and args[1].isdigit() else 1

    if page < 1:
        sender.send_message(f"{errorLog()}Page number must be 1 or higher")
        return False

    history_message = db.print_punishment_history(target_name, page)

    if not history_message:
        sender.send_message(f"{modLog()}No punishment history found for {ColorFormat.YELLOW}{target_name}")
        return True

    sender.send_message(history_message)
    return True

def remove_punishment(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    """Handles the removal or clearing process of a player's punishments, using a menu to choose a player."""

    if len(args) > 1:
        sender.send_message(f"{errorLog()}Usage: /punishments remove or /punishments clear")
        return False

    # Check if the action is 'remove' or 'clear'
    action = args[0].lower()

    # Retrieve list of all players in the database
    db = UserDB("wmctcore_users.db")
    players = db.get_all_players()

    if not players:
        sender.send_message(f"{errorLog()}No players found in the database.")
        return False

    # Create an action form with the list of players
    form = ActionFormData()
    form.title("Punishment Log Manager")
    form.body("Select a player:")

    for player in players:
        form.button(f"{player}")

    # Handle the player's submission
    def submit(player: Player, result: ActionFormResponse):
        if result.canceled:
            return

        selected_player = players[int(result.selection)]

        if selected_player:
            if action == "remove":
                # Show punishments for the selected player and allow them to select one to remove
                return remove_punishment_by_id(self, sender, selected_player)
            elif action == "clear":
                # Clear all punishments for the selected player
                return clear_all_punishments(self, sender, selected_player)
            else:
                player.send_message(f"{errorLog()}Invalid action. Please use 'remove' or 'clear'.")
        else:
            player.send_message(f"{errorLog()}Invalid selection.")

    # Show the form and wait for a response
    form.show(sender).then(
        lambda result, player=sender: submit(result, player)
    )

    return True

def clear_all_punishments(self: "WMCTPlugin", sender: CommandSender, target_name: str) -> bool:
    """Clears all punishment logs for the selected player."""
    db = UserDB("wmctcore_users.db")

    # Clear all punishment logs for the selected player
    success = db.delete_all_punishment_logs_by_name(target_name)

    if success:
        sender.send_message(f"{modLog()}Successfully cleared all punishments for {ColorFormat.YELLOW}{target_name}")
    else:
        sender.send_message(f"{modLog()}Failed to clear punishments for {ColorFormat.YELLOW}{target_name}")

    return True

def remove_punishment_by_id(self: "WMCTPlugin", sender: CommandSender, target_name: str) -> bool:
    """Removes a specific punishment by ID using a menu."""

    # Retrieve punishment history
    db = UserDB("wmctcore_users.db")
    history = db.print_punishment_history(target_name)
    punish_log = db.get_punishment_logs(target_name)

    if not history:
        sender.send_message(f"{errorLog()}No punishments found for {ColorFormat.YELLOW}{target_name}.")
        return False

    # Create action form with punishments listed as buttons
    form = ActionFormData()
    form.title("Punishment Removal")

    # Add each punishment to the form with its index
    for idx, punishment in enumerate(history, start=1):
        form.button(f"§7{punishment}")

    # Handle the player's selection
    def submit(player: Player, result: ActionFormResponse):
        if result.canceled:
            return

        # Remove punishment by ID
        punishment_id = punish_log[int(result.selection)].id
        success = db.remove_punishment_log_by_id(target_name, punishment_id)

        if success:
            player.send_message(
                f"{modLog()}Successfully removed punishment ID {punishment_id} for {ColorFormat.YELLOW}{target_name}")
        else:
            player.send_message(
                f"{errorLog()}Failed to remove punishment ID {punishment_id} for {ColorFormat.YELLOW}{target_name}")

    # Show the form and wait for the player's response
    form.show(sender).then(
        lambda result, player=sender: submit(result, player)
    )

    return True