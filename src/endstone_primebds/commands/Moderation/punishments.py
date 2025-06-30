from endstone_primebds.utils.timeUtil import TimezoneUtils

from endstone import ColorFormat, Player
from endstone.command import CommandSender
from endstone_primebds.utils.commandUtil import create_command
from typing import TYPE_CHECKING
from endstone_primebds.utils.dbUtil import UserDB
from endstone_primebds.utils.formWrapperUtil import ActionFormResponse, ActionFormData
from endstone_primebds.utils.prefixUtil import modLog, errorLog

if TYPE_CHECKING:
    from endstone_primebds.primebds import PrimeBDS

# Register command
command, permission = create_command(
    "punishments",
    "Manage punishment history of a specified player!",
    ["/punishments <player: player> [page: int]",
     "/punishments <player: player> (remove|clear) <punishment_removal: remove_punishment_log>"],
    ["primebds.command.punishments"]
)

# PUNISHMENTS CMD FUNCTIONALITY
def handler(self: "PrimeBDS", sender: CommandSender, args: list[str]) -> bool:
    """Command to fetch or remove a player's punishment history."""

    if not args:
        sender.send_message(
            ColorFormat.red("Usage: /punishments <player> [page] OR /punishments <player> (remove|clear)"))
        return False

    db = UserDB("users.db")

    target_name = args[0]

    if len(args) > 1:
        action = args[1].lower()

        if action == "remove":
            return remove_punishment_by_id(self, sender, target_name)

        elif action == "clear":
            return clear_all_punishments(self, sender, target_name)

    # Retrieve punishment history
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


def clear_all_punishments(self: "PrimeBDS", sender: CommandSender, target_name: str) -> bool:
    """Clears all punishment logs for the selected player."""
    db = UserDB("users.db")

    success = db.delete_all_punishment_logs_by_name(target_name)

    if success:
        sender.send_message(f"{modLog()}Successfully cleared all punishments for {ColorFormat.YELLOW}{target_name}")
    else:
        sender.send_message(f"{modLog()}Failed to clear punishments for {ColorFormat.YELLOW}{target_name}")

    return True

def remove_punishment_by_id(self: "PrimeBDS", sender: CommandSender, target_name: str) -> bool:
    """Removes a specific punishment by ID using a menu."""

    # Retrieve punishment history
    db = UserDB("users.db")
    history = db.print_punishment_history(target_name)
    punish_log = db.get_punishment_logs(target_name)

    if not history:
        sender.send_message(f"{modLog()}No more punishments found for {ColorFormat.YELLOW}{target_name}.")
        return False

    # Create action form with punishments listed as buttons
    form = ActionFormData()
    form.title("Punishment Removal")
    form.button("Cancel")

    for punishment in punish_log:
        punishment_text = (
            f"{punishment.action_type}: {punishment.reason}\n"
            f"{ColorFormat.DARK_GRAY}("
            f"{ColorFormat.YELLOW}{TimezoneUtils.convert_to_timezone(punishment.timestamp, 'EST')}"
            f"{ColorFormat.DARK_GRAY})"
        )
        form.button(f"§c{punishment_text}")

    # Handle the player's selection
    def submit(player: Player, result: ActionFormResponse):
        if result.canceled or result.selection == 0:
            return

        # Remove punishment by ID
        punishment_id = punish_log[int(result.selection)-1].id
        success = db.remove_punishment_log_by_id(target_name, punishment_id)

        if success:
            player.send_message(
                f"{modLog()}Successfully removed punishment ID {punishment_id} for {ColorFormat.YELLOW}{target_name}")
        else:
            player.send_message(
                f"{errorLog()}Failed to remove punishment ID {punishment_id} for {ColorFormat.YELLOW}{target_name}")

        remove_punishment_by_id(self, sender, target_name)

    # Show the form and wait for the player's response
    form.show(sender).then(
        lambda result, player=sender: submit(result, player)
    )

    return True