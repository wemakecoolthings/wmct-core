import os
import json
import shutil
import threading
import time

from endstone_primebds.utils.configUtil import load_config, save_config
from endstone.command import CommandSender
from endstone_primebds.utils.commandUtil import create_command
from endstone_primebds.utils.prefixUtil import errorLog, infoLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_primebds.primebds import PrimeBDS

# Register command
command, permission = create_command(
    "alist",
    "Manages server access!",
    ["/alist", "/alist (list|check|profiles)<allowlist_sub: allowlist_list>",
     "/alist (add|remove)<allowlist_sub: allowlist_sub_action> <player: player> [ignore_max_player_limit: bool]",
     "/alist (create|use|delete)<allowlist: allowlist_action> <name: string>"],
    ["primebds.command.alist"],
    "op",
    ["wlist"]
)

# ALLOWLIST COMMAND FUNCTIONALITY
def handler(self: "PrimeBDS", sender: CommandSender, args: list[str]) -> bool:
    if len(args) == 0:
        sender.send_message(f"{errorLog()}Usage: /alist <add|remove|list> [name]")
        return True

    subcommand = args[0].lower()

    if subcommand == "add":
        if len(args) < 2:
            sender.send_message(f"{errorLog()}Usage: /alist add <player> [ignore_max_player]")
            return True

        player_name = args[1]
        ignore_max_player = None

        if len(args) >= 3:
            if args[2].lower() in ["true", "false"]:
                ignore_max_player = args[2].lower() == "true"
            else:
                sender.send_message(f"{errorLog()}§rignore_max_player must be 'true' or 'false'")
                return True

        self.server.dispatch_command(self.server.command_sender, f"whitelist add \"{player_name}\"")
        sender.send_message(f"{infoLog()}§rAdded §b{player_name}§r to allowlist.")

        if ignore_max_player is not None:
            def modify_allowlist_after_delay():
                time.sleep(1.5)  # Small delay to let Minecraft write the entry
                allowlist_path = get_allowlist_path()
                try:
                    with open(allowlist_path, 'r') as f:
                        data = json.load(f)

                    modified = False
                    for entry in data:
                        if entry.get("name") == player_name:
                            entry["ignoresPlayerLimit"] = ignore_max_player
                            entry["xuid"] = self.server.get_player(player_name).xuid
                            modified = True
                            break

                    if modified:
                        with open(allowlist_path, 'w') as f:
                            json.dump(data, f, indent=4)
                        print(f"[PrimeBDS] Updated 'ignoresPlayerLimit' for {player_name} to {ignore_max_player}")
                    else:
                        print(f"[PrimeBDS] Could not find {player_name} in allowlist.json")

                except Exception as e:
                    print(f"[PrimeBDS] Failed to modify allowlist: {e}")

            threading.Thread(target=modify_allowlist_after_delay, daemon=True).start()

        self.server.dispatch_command(self.server.command_sender, f"whitelist reload")

    elif subcommand == "remove":
        if len(args) < 2:
            sender.send_message(f"{errorLog()}Usage: /alist remove <player>")
            return True
        player_name = args[1]
        self.server.dispatch_command(self.server.command_sender, f"whitelist remove \"{player_name}\"")
        sender.send_message(f"{infoLog()}§rRemoved §b{player_name}§r from allowlist.")
        self.server.dispatch_command(self.server.command_sender, f"whitelist reload")
        return True

    elif subcommand == "list":
        allowlist_path = get_allowlist_path()
        if not os.path.exists(allowlist_path):
            sender.send_message(f"{errorLog()}§rAllowlist file not found.")
            return True
        try:
            with open(allowlist_path, 'r') as f:
                data = json.load(f)
            if not data:
                sender.send_message(f"{infoLog()}§rAllowlist is empty.")
                return True
            lines = []
            for entry in data:
                name = entry.get("name", "[unknown]")
                ignores = entry.get("ignoresPlayerLimit", False)
                formatted = f"§7{name}"
                if ignores:
                    formatted = f"§6{name} §8(ignores player limit)"
                lines.append(formatted)
            sender.send_message(f"{infoLog()}§rAllowlist players:\n" + "\n".join(f"§7- {line}" for line in lines))
        except Exception as e:
            sender.send_message(f"{errorLog()}§rFailed to read allowlist: {e}")
        return True


    elif subcommand == "check":

        try:

            config = load_config()
            profile_name = config.get("modules", {}).get("allowlist", {}).get("profile", "default")
            profile_dir = get_allowlist_profiles_folder()
            profile_file = os.path.join(profile_dir, f"{profile_name}.json")

            if not os.path.exists(profile_file):
                sender.send_message(f"{errorLog()}§rProfile §c'{profile_name}'§r not found in allowlist_profiles.")
                return True

            # Get actual active allowlist
            current_dir = os.path.dirname(os.path.abspath(__file__))

            while not (
                    os.path.exists(os.path.join(current_dir, 'plugins')) and
                    os.path.exists(os.path.join(current_dir, 'worlds'))
            ):
                current_dir = os.path.dirname(current_dir)

            allowlist_path = os.path.join(current_dir, 'allowlist.json')

            if not os.path.exists(allowlist_path):
                sender.send_message(f"{errorLog()}Active allowlist.json file not found.")
                return True

            with open(allowlist_path, 'r') as f:
                active_data = json.load(f)

            active_count = len(active_data)
            sender.send_message(
                f"{infoLog()}§rUsing allowlist profile: §b{profile_name}§r with §a{active_count}§r active players.")

        except Exception as e:
            sender.send_message(f"{errorLog()}Failed to check allowlist profile: {e}")

        return True

    elif subcommand == "create":
        if len(args) < 2:
            sender.send_message(f"{errorLog()}Usage: /alist create <name>")
            return True

        profile_name = args[1].strip()
        path = get_allowlist_profile_path(profile_name)

        if os.path.exists(path):
            sender.send_message(f"{errorLog()}Allowlist profile '{profile_name}' already exists.")
            return True

        try:
            with open(path, "w") as f:
                json.dump([], f, indent=4)
            sender.send_message(f"{infoLog()}Created allowlist profile '{profile_name}'.")
        except Exception as e:
            sender.send_message(f"{errorLog()}Failed to create profile: {e}")
        return True

    elif subcommand == "delete":
        if len(args) < 2:
            sender.send_message(f"{errorLog()}Usage: /alist delete <name>")
            return True

        profile_name = args[1].strip()
        path = get_allowlist_profile_path(profile_name)

        if not os.path.exists(path):
            sender.send_message(f"{errorLog()}Allowlist profile '{profile_name}' does not exist.")
            return True

        try:
            os.remove(path)
            sender.send_message(f"{infoLog()}Deleted allowlist profile '{profile_name}'.")
        except Exception as e:
            sender.send_message(f"{errorLog()}Failed to delete profile: {e}")
        return True

    elif subcommand == "use":
        if len(args) < 2:
            sender.send_message(f"{errorLog()}Usage: /alist use <profile>")
            return True

        target_profile = args[1].strip()
        profiles_dir = get_allowlist_profiles_folder()
        target_path = os.path.join(profiles_dir, f"{target_profile}.json")
        if not os.path.exists(target_path):
            sender.send_message(f"{errorLog()}Profile '{target_profile}' does not exist.")
            return True

        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            while not (
                    os.path.exists(os.path.join(current_dir, 'plugins')) and
                    os.path.exists(os.path.join(current_dir, 'worlds'))
            ):
                current_dir = os.path.dirname(current_dir)

            current_allowlist = os.path.join(current_dir, "allowlist.json")
            config = load_config()
            current_profile = config.get("modules", {}).get("allowlist", {}).get("profile", "default")
            current_profile_path = os.path.join(profiles_dir, f"{current_profile}.json")
            if os.path.exists(current_allowlist):
                with open(current_allowlist, "r") as f:
                    current_data = f.read()
                if not os.path.exists(current_profile_path) or open(current_profile_path, "r").read() != current_data:
                    with open(current_profile_path, "w") as f:
                        f.write(current_data)
                    print(f"[PrimeBDS] Backed up allowlist.json to profile '{current_profile}'")

            # Now apply the new profile
            def delayed_apply():
                time.sleep(1.0)  # short delay to avoid race conditions
                print(f"[PrimeBDS] Activated allowlist profile '{target_profile}'")
                sender.send_message(f"{infoLog()}Activated allowlist profile '{target_profile}'")
                shutil.copyfile(target_path, current_allowlist)
                config["modules"]["allowlist"]["profile"] = target_profile
                save_config(config)
                self.server.dispatch_command(self.server.command_sender, f"whitelist reload")

            threading.Thread(target=delayed_apply, daemon=True).start()
            sender.send_message(f"{infoLog()}Allowlist profile will switch to '{target_profile}' shortly.")

        except Exception as e:
            sender.send_message(f"{errorLog()}Failed to use profile: {e}")
        return True

    elif subcommand == "profiles":
        profiles_dir = get_allowlist_profiles_folder()
        if not os.path.exists(profiles_dir):
            sender.send_message(f"{errorLog()}No profiles directory found.")
            return True

        try:
            profiles = [f[:-5] for f in os.listdir(profiles_dir) if f.endswith(".json")]
            if not profiles:
                sender.send_message(f"{infoLog()}No saved allowlist profiles.")
                return True

            config = load_primebds_config()
            current_profile = config.get("modules", {}).get("allowlist", {}).get("profile", "default")

            lines = []
            for profile in profiles:
                if profile == current_profile:
                    lines.append(f"§a{profile} §7(current)")
                else:
                    lines.append(f"§7{profile}")
            sender.send_message(f"{infoLog()}Available profiles:\n" + "\n".join(f"§8- {line}" for line in lines))

        except Exception as e:
            sender.send_message(f"{errorLog()}Failed to list profiles: {e}")
        return True

    else:
        sender.send_message(f"{errorLog()}Unknown subcommand '{subcommand}'")
        return True
    return True

def get_primebds_root() -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while not (
        os.path.exists(os.path.join(current_dir, 'plugins')) and
        os.path.exists(os.path.join(current_dir, 'worlds'))
    ):
        current_dir = os.path.dirname(current_dir)
    return current_dir

def get_primebds_config_path() -> str:
    root = get_primebds_root()
    return os.path.join(root, 'plugins', 'primebds_data', 'config.json')

def load_primebds_config() -> dict:
    path = get_primebds_config_path()
    if not os.path.exists(path):
        return {}
    with open(path, 'r') as f:
        return json.load(f)

def save_primebds_config(data: dict):
    path = get_primebds_config_path()
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def get_allowlist_profile_path(profile_name: str) -> str:
    return os.path.join(get_allowlist_profiles_folder(), f"{profile_name}.json")

def get_allowlist_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while not (
        os.path.exists(os.path.join(current_dir, 'plugins')) and
        os.path.exists(os.path.join(current_dir, 'worlds'))
    ):
        current_dir = os.path.dirname(current_dir)
    return os.path.join(current_dir, 'allowlist.json')

def get_primebds_data_folder() -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while not (
        os.path.exists(os.path.join(current_dir, 'plugins')) and
        os.path.exists(os.path.join(current_dir, 'worlds'))
    ):
        current_dir = os.path.dirname(current_dir)
    data_folder = os.path.join(current_dir, 'plugins', 'primebds_data')
    os.makedirs(data_folder, exist_ok=True)
    return data_folder

def get_allowlist_profiles_folder() -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while not (
        os.path.exists(os.path.join(current_dir, 'plugins')) and
        os.path.exists(os.path.join(current_dir, 'worlds'))
    ):
        current_dir = os.path.dirname(current_dir)

    data_folder = os.path.join(current_dir, 'plugins', 'primebds_data')
    os.makedirs(data_folder, exist_ok=True)

    profiles_folder = os.path.join(data_folder, "allowlist_profiles")
    os.makedirs(profiles_folder, exist_ok=True)

    # Check for existing 'default.json'
    default_profile = os.path.join(profiles_folder, "default.json")
    original_allowlist = os.path.join(current_dir, "allowlist.json")

    if not os.path.exists(default_profile) and os.path.exists(original_allowlist):
        try:
            shutil.copyfile(original_allowlist, default_profile)
            print("[PrimeBDS] Initialized allowlist_profiles/default.json from existing allowlist.json")
        except Exception as e:
            print(f"[PrimeBDS] Failed to create default allowlist profile: {e}")

    return profiles_folder