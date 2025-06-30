import os

from endstone import Player
from endstone.command import CommandSender

from endstone_primebds.utils.commandUtil import create_command
from endstone_primebds.utils.formWrapperUtil import ActionFormData, ActionFormResponse
from endstone_primebds.utils.configUtil import load_config, save_config

from typing import TYPE_CHECKING

from endstone_primebds.utils.prefixUtil import infoLog
from functools import partial

if TYPE_CHECKING:
    from endstone_primebds.primebds import PrimeBDS

# Register command
command, permission = create_command(
    "primebds",
    "A global command for primebds to modify settings.!",
    ["/primebds (settings)<primebds_action: primebds_action>"],
    ["primebds.command.primebds"]
)

# PRIMEBDS SETTINGS COMMAND FUNCTIONALITY
def handler(self: "PrimeBDS", sender: CommandSender, args: list[str]) -> bool:
    if not isinstance(sender, Player):
        sender.send_error_message("This command can only be executed by a player")
        return True

    if args[0] == "settings":
        form = ActionFormData()
        form.title("primebds Settings")
        form.body("Select a category to view settings:")
        form.button("Commands Settings")
        form.button("Cancel")

        form.show(sender).then(handle_settings_menu)

    return True

def find_whl_file(name):
    # Search for .whl files in the current directory and subdirectories
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".whl") and name in file:
                return os.path.join(root, file)
    return None

# HANDLE MAIN SETTINGS MENU
def handle_settings_menu(player: Player, result: ActionFormResponse):
    if result.canceled or result.selection is None:
        return

    if result.selection == 0:
        config = load_config()
        show_commands_settings(player, config)

def show_commands_settings(player: Player, config: dict):
    commands = config.get("commands", {})
    form = ActionFormData().title("Commands Settings").body("Toggle command availability:")

    for command_name, settings in commands.items():
        status = settings.get("enabled", False)
        status_color = "§aEnabled" if status else "§cDisabled"
        form.button(f"{command_name} - {status_color}")

    form.show(player).then(partial(handle_commands_response, config=config))

def handle_commands_response(player: Player, result: ActionFormResponse, config: dict):
    if result.canceled or result.selection is None:
        return

    commands = list(config.get("commands", {}).keys())
    if result.selection < len(commands):
        command_name = commands[result.selection]
        toggle_command_setting(player, command_name, config)
        show_commands_settings(player, config)
    else:
        handle_settings_menu(player, ActionFormResponse(selection=0, canceled=False))

def toggle_command_setting(player: Player, command_name: str, config: dict):
    if command_name in config["commands"]:
        config["commands"][command_name]["enabled"] = not config["commands"][command_name]["enabled"]
        save_config(config)
    new_status = config["commands"][command_name]["enabled"]
    status_color = "§a" if new_status else "§c"
    player.send_message(
        f"{infoLog()}Command §b/{command_name}§r was set to {status_color}{new_status}§r! Use §e/reload or restart the server §rto enable changes!"
    )
