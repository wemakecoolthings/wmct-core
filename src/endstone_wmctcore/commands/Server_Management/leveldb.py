import os
import json
from pstats import SortKey

import endstone.scoreboard
from endstone import ColorFormat
from endstone._internal.endstone_python import DisplaySlot, ObjectiveSortOrder
from endstone.command import CommandSender

from endstone.scoreboard import Criteria
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.prefixUtil import infoLog, errorLog
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "levelscores",
    "Save and load scoreboard profiles between worlds - USES NAME STRING OBJECTIVES",
    ["/levelscores (save|load|list|delete)<action: file_action> [name: string]"],
    ["wmctcore.command.levelscores"]
)

# LEVELDB CMD FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    player = self.server.get_player(sender.name)

    action = args[0]

    if action == "save" and len(args) > 1:
        name = args[1]
        return save_scoreboard(self, player, name)
    elif action == "load" and len(args) > 1:
        name = args[1]
        return load_scoreboard(self, player, name)
    elif action == "list":
        profiles = list_scoreboard_profiles()
        player.send_message(
            f"{infoLog()}Available profiles: {', '.join(profiles)}" if profiles else f"{infoLog()}No profiles found.")
        return True
    elif action == "delete" and len(args) > 1:
        name = args[1]
        return delete_scoreboard(self, player, name)

    player.send_message(f"{errorLog()}Invalid action. Use 'save', 'load', or 'list'.")
    return False

def save_scoreboard(self: "WMCTPlugin", player, name: str) -> bool:
    save_path = os.path.join(get_profiles_directory(), f"{name}.json")
    objectives = self.server.scoreboard.objectives
    entries = self.server.scoreboard.entries
    data = {}

    for objective in objectives:
        obj_data = {
            "display_name": objective.display_name,
            "criteria": objective.criteria.name,
            "render_type": objective.render_type.value,
            "display_slot": str(objective.display_slot) if hasattr(objective.display_slot, '__str__') else str(DisplaySlot.PLAYER_LIST),  # Default to PLAYER_LIST
            "sort_order": str(objective.sort_order) if hasattr(objective.sort_order, '__str__') else str(ObjectiveSortOrder.ASCENDING), # Default to ASCENDING
            "entries": {}
        }

        if len(entries) > 0:
            for entry in entries:
                # Only process entries that are strings
                if isinstance(entry, str):
                    score_obj = objective.get_score(entry)
                    obj_data["entries"][entry] = {
                        "value": score_obj.value
                    }

        data[objective.name] = obj_data

    # Saving to file
    with open(save_path, 'w') as f:
        json.dump(data, f, indent=4)

    player.send_message(f"{infoLog()}Saved scoreboard profile '{name}'")
    return True

def load_scoreboard(self: "WMCTPlugin", player, name: str) -> bool:
    load_path = os.path.join(get_profiles_directory(), f"{name}.json")

    if not os.path.exists(load_path):
        player.send_message(f"{errorLog()}Scoreboard profile '{name}' not found!")
        return False

    with open(load_path, 'r') as f:
        data = json.load(f)

    # Track if any new objectives were created
    new_profile = False

    for obj_name, obj_data in data.items():
        objective = self.server.scoreboard.get_objective(obj_name)

        if not objective:
            criteria = Criteria.DUMMY
            objective = self.server.scoreboard.add_objective(obj_name, criteria, obj_data["display_name"])
            new_profile = True  # Mark as new profile

        # Set the entries for both new and existing objectives
        for entry_name, entry_data in obj_data["entries"].items():
            score_obj = objective.get_score(entry_name)
            score_obj.value = entry_data["value"]

    # Send the message after processing all objectives
    if new_profile:
        player.send_message(f"{infoLog()}Loaded scoreboard profile '{name}' {ColorFormat.GRAY}{ColorFormat.ITALIC}[NEW]")
    else:
        player.send_message(f"{infoLog()}Loaded scoreboard profile '{name}' {ColorFormat.GRAY}{ColorFormat.ITALIC}[OLD]")

    return True

def delete_scoreboard(self: "WMCTPlugin", player, name: str) -> bool:
    delete_path = os.path.join(get_profiles_directory(), f"{name}.json")

    if not os.path.exists(delete_path):
        player.send_message(f"{errorLog()}Scoreboard profile '{name}' not found!")
        return False

    os.remove(delete_path)
    player.send_message(f"{infoLog()}Deleted scoreboard profile '{name}'")
    return True

def list_scoreboard_profiles() -> list[str]:
    directory = get_profiles_directory()
    return [f[:-5] for f in os.listdir(directory) if f.endswith('.json')]

def get_profiles_directory() -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while not (os.path.exists(os.path.join(current_dir, 'plugins')) and os.path.exists(
            os.path.join(current_dir, 'worlds'))):
        current_dir = os.path.dirname(current_dir)


    profiles_dir = os.path.join(current_dir, 'scoreboard_profiles')
    os.makedirs(profiles_dir, exist_ok=True)

    return profiles_dir