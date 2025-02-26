import re
from datetime import datetime
import pytz
import time
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
    ["/punishments <player: player> [page: int]", "/punishments (remove|clear)<punishment_removal: remove_punishment_log>"],
    ["wmctcore.command.punishments"]
)

def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    """Command to fetch or remove a player's punishment history."""

    if not args:
        sender.send_message(ColorFormat.red("Usage: /punishments <player> [page] OR /punishments remove <player>"))
        return False

    action = args[0].lower()

    if action == "remove":
        return False # To be added later
    elif action == "clear":
        return False # To be added later

    target_name = args[0]
    page = int(args[1]) if len(args) > 1 and args[1].isdigit() else 1

    if page < 1:
        sender.send_message(f"{errorLog()}Page number must be 1 or higher")
        return False

    # Retrieve punishment history
    db = UserDB("wmctcore_users.db")
    history = db.get_punishment_history(target_name)

    if not history:
        sender.send_message(f"{modLog()}No punishment history found for {ColorFormat.YELLOW}{target_name}")
        return True

    # Paginate (5 per page)
    per_page = 5
    total_pages = (len(history) + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    paginated_history = history[start:end]

    # Build response
    msg = [f"{modLog()}Punishment History for {ColorFormat.YELLOW}{target_name} {ColorFormat.GRAY}(Page {page}/{total_pages}){ColorFormat.GOLD}:§r"]
    for entry in paginated_history:
        msg.append(f"§7- {entry}")

    # Show navigation hint
    if page < total_pages:
        msg.append(f"§8Use §e/punishments {target_name} {page + 1} §8for more.")

    sender.send_message(f"\n".join(msg))
    return True