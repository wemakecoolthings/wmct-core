import json
import os
import time

from endstone.event import PlayerLoginEvent, PlayerJoinEvent, PlayerQuitEvent, PlayerKickEvent
from typing import TYPE_CHECKING

from datetime import datetime

from endstone_primebds.utils.configUtil import load_config
from endstone_primebds.utils.modUtil import format_time_remaining, ban_message
from endstone_primebds.utils.dbUtil import UserDB, GriefLog
from endstone.util import Vector

if TYPE_CHECKING:
    from endstone_primebds.primebds import PrimeBDS

def handle_login_event(self: "PrimeBDS", ev: PlayerLoginEvent):

    # Ban System: ENHANCEMENT
    db = UserDB("users.db")
    now = datetime.now()

    player_xuid = ev.player.xuid
    player_ip = str(ev.player.address)

    mod_log = db.get_mod_log(player_xuid)
    is_ip_banned = db.check_ip_ban(player_ip)

    # Handle IP Ban
    if is_ip_banned:
        banned_time = datetime.fromtimestamp(mod_log.banned_time)
        if now >= banned_time:  # IP Ban has expired
            db.remove_ban(player_ip)
        else:  # IP Ban is still active
            formatted_expiration = format_time_remaining(mod_log.banned_time)
            message = ban_message(self.server.level.name, formatted_expiration, "IP Ban - " + mod_log.ban_reason)
            ev.kick_message = message
            ev.is_cancelled = True  # Prevent login

    # Handle XUID Ban
    elif mod_log:
        if mod_log.is_banned:  # Only proceed if the player is banned
            banned_time = datetime.fromtimestamp(mod_log.banned_time)
            if now >= banned_time:  # Ban has expired
                db.remove_ban(player_xuid)
            else:  # Ban is still active
                formatted_expiration = format_time_remaining(mod_log.banned_time)
                message = ban_message(self.server.level.name, formatted_expiration, mod_log.ban_reason)
                ev.kick_message = message
                ev.is_cancelled = True  # Prevent login

    db.close_connection()
    return

def handle_join_event(self: "PrimeBDS", ev: PlayerJoinEvent):
    # Update Saved Data
    db = UserDB("users.db")
    db.save_user(ev.player)
    db.update_user_data(ev.player.name, 'last_join', int(time.time()))
    self.reload_custom_perms(ev.player)

    # Ban System: ENHANCEMENT
    mod_log = db.get_mod_log(ev.player.xuid)
    if mod_log:
        if mod_log.is_banned:
            ev.join_message = ""  # Remove join message
        else:
            # User Log
            dbgl = GriefLog("grieflog.db")
            dbgl.start_session(ev.player.xuid, ev.player.name, int(time.time()))
            rounded_coords = Vector(
                round(ev.player.location.x),
                round(ev.player.location.y),
                round(ev.player.location.z)
            )
            dbgl.log_action(ev.player.xuid, ev.player.name, "Login", rounded_coords, int(time.time()))
            dbgl.close_connection()

    db.close_connection()

    check_unset_scoreboards(self)

    return

def handle_leave_event(self: "PrimeBDS", ev: PlayerQuitEvent):

    # Update Data On Leave
    db = UserDB("users.db")
    db.update_user_data(ev.player.name, 'last_leave', int(time.time()))

    # Ban System: ENHANCEMENT
    mod_log = db.get_mod_log(ev.player.xuid)
    if mod_log:
        if mod_log.is_banned:
            ev.quit_message = ""  # Remove join message
        else:
            # User Log
            dbgl = GriefLog("grieflog.db")
            dbgl.end_session(ev.player.xuid, int(time.time()))
            rounded_x = round(ev.player.location.x)
            rounded_y = round(ev.player.location.y)
            rounded_z = round(ev.player.location.z)
            rounded_coords = Vector(rounded_x, rounded_y, rounded_z)
            dbgl.log_action(ev.player.xuid, ev.player.name, "Logout", rounded_coords, int(time.time()))
            dbgl.close_connection()

    db.close_connection()
    return

def handle_kick_event(self: "PrimeBDS", ev: PlayerKickEvent):
    print(ev.player.name, ev.reason)
    dbgl = GriefLog("grieflog.db")
    dbgl.end_session(ev.player.xuid, int(time.time()))
    dbgl.close_connection()

def check_unset_scoreboards(self):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while not (
        os.path.exists(os.path.join(current_dir, 'plugins')) and
        os.path.exists(os.path.join(current_dir, 'worlds'))
    ):
        current_dir = os.path.dirname(current_dir)

    scoreboard_data_folder = os.path.join(current_dir, 'plugins/primebds_data', 'scoreboard_data')
    if not os.path.exists(scoreboard_data_folder):
        return  # Folder doesn't exist, nothing to check

    # Check if all scoreboard files are fully loaded
    all_fully_loaded = True
    for filename in os.listdir(scoreboard_data_folder):
        if filename.endswith(".json"):
            full_path = os.path.join(scoreboard_data_folder, filename)
            with open(full_path, 'r') as f:
                data = json.load(f)
            # If any objective in this file is not fully loaded, we continue processing
            for obj_data in data.values():
                if not obj_data.get("is_fully_loaded", False):
                    all_fully_loaded = False
                    break
            if not all_fully_loaded:
                break

    if all_fully_loaded:
        return

    # Map online players by xuid for quick lookup
    online_players_by_xuid = {player.xuid: player for player in self.server.online_players}

    for filename in os.listdir(scoreboard_data_folder):
        if not filename.endswith('.json'):
            continue

        full_path = os.path.join(scoreboard_data_folder, filename)
        try:
            with open(full_path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Could not read scoreboard file {filename}: {e}")
            continue

        file_modified = False

        for obj_name, obj_data in data.items():
            if not isinstance(obj_data, dict):
                continue

            entries = obj_data.get("entries", {})
            if not isinstance(entries, dict):
                continue

            all_loaded = True
            objective = self.server.scoreboard.get_objective(obj_name)
            if not objective:
                # If objective not present, add it with DUMMY criteria
                from endstone._internal.endstone_python import Criteria
                criteria = Criteria.DUMMY
                display_name = obj_data.get("display_name", obj_name)
                objective = self.server.scoreboard.add_objective(obj_name, criteria, display_name)

            # Iterate all entries
            for entry_key, entry_data in entries.items():
                loaded = entry_data.get("loaded", False)
                if loaded:
                    continue

                if entry_key.isdigit() and len(entry_key) >= 12:
                    player = online_players_by_xuid.get(entry_key)
                    if player:
                        score_obj = objective.get_score(player)
                        score_obj.value = entry_data.get("value", 0)
                        entry_data["loaded"] = True
                        file_modified = True
                    else:
                        all_loaded = False
                else:
                    # Non XUID entries should already be loaded immediately
                    # Mark loaded True to avoid repeated checks
                    entry_data["loaded"] = True
                    file_modified = True

            # Update is_fully_loaded based on whether all entries are loaded
            if all_loaded and obj_data.get("is_fully_loaded") != True:
                obj_data["is_fully_loaded"] = True
                file_modified = True
            elif not all_loaded and obj_data.get("is_fully_loaded") != False:
                obj_data["is_fully_loaded"] = False
                file_modified = True

        if file_modified:
            try:
                with open(full_path, 'w') as f:
                    json.dump(data, f, indent=4)
                print(f"[PrimeBDS] Updated scoreboard file '{filename}' after loading missing entries.")
            except Exception as e:
                print(f"[PrimeBDS] Could not save updated scoreboard file {filename}: {e}")
