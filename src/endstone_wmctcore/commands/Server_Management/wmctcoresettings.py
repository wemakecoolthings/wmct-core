import json
from endstone import Player, ColorFormat
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.formWrapperUtil import ActionFormData, ActionFormResponse, ModalFormData, ModalFormResponse
from endstone_wmctcore.utils.configUtil import load_config, save_config

from typing import TYPE_CHECKING

from endstone_wmctcore.utils.prefixUtil import errorLog, infoLog

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "wmctcoresettings",
    "Opens the wmctcore plugin settings menu!",
    ["/wmctcoresettings"],
    ["wmctcore.command.wmctcoresettings"]
)

# WMCTCORESETTINGS COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    if not isinstance(sender, Player):
        sender.send_error_message("This command can only be executed by a player")
        return True

    config = load_config()

    form = ActionFormData()
    form.title("WMCTCore Settings")
    form.body("Select a category to view settings:")

    form.button("Commands Settings")
    form.button("Modules Settings")
    form.button("Cancel")

    form.show(sender).then(
        lambda player=sender, result=ActionFormResponse: handle_settings_menu(player, result, config)
    )

    return True

# HANDLE MAIN SETTINGS MENU
def handle_settings_menu(player: Player, result: ActionFormResponse, config: dict):
    if result.canceled or result.selection is None:
        return

    if result.selection == 0:
        show_commands_settings(player)
    elif result.selection == 1:
        show_modules_settings(player, config)

def show_commands_settings(player: Player):
    config = load_config()
    commands = config.get("commands", {})
    form = ActionFormData().title("Commands Settings").body("Toggle command availability:")

    for command_name, settings in commands.items():
        status = settings.get("enabled", False)
        status_color = "§aEnabled" if status else "§cDisabled"
        form.button(f"{command_name} - {status_color}")

    form.button("Back")
    form.show(player).then(lambda p, res: handle_commands_response(p, res, config))

def handle_commands_response(player: Player, result: ActionFormResponse, config):
    if result.canceled or result.selection is None:
        return

    commands = list(config.get("commands", {}).keys())
    if result.selection < len(commands):
        command_name = commands[result.selection]
        toggle_command_setting(player, command_name, config)
    else:
        handler(None, player, [])

def toggle_command_setting(player: Player, command_name: str, config: dict):
    if command_name in config["commands"]:
        config["commands"][command_name]["enabled"] = not config["commands"][command_name]["enabled"]
        save_config(config)
    new_status = config["commands"][command_name]["enabled"]
    status_color = "§a" if new_status else "§c"
    player.send_message(f"{infoLog()}Command §b/{command_name}§r was set to {status_color}{new_status}§r! Use §e/reload §rto enable changes!")

def show_modules_settings(player: Player, config: dict):
    modules = config.get("modules", {})

    form = ActionFormData()
    form.title("Modules Settings")
    form.body("Select a module to edit its settings:")

    for module in modules.keys():
        form.button(module)  # Just the module name, no enabled/disabled status

    form.button("Back")

    form.show(player).then(
        lambda p=player, res=ActionFormResponse: handle_module_selection(p, res, config)
    )

def handle_module_selection(player: Player, result: ActionFormResponse, config: dict):
    if result.canceled or result.selection is None:
        return

    modules = list(config.get("modules", {}).keys())

    if result.selection < len(modules):
        module_name = modules[result.selection]
        show_module_sub_options(player, module_name, config)

    else:
        handler(None, player, [])  # Go back to main menu

def show_module_sub_options(player: Player, module_name: str, config: dict):
    module_data = config.get("modules", {}).get(module_name, {})

    form = ActionFormData()
    form.title(f"{module_name} Settings")
    form.body("Select a setting category:")

    for sub_option in module_data.keys():
        form.button(sub_option)

    form.button("Back")

    form.show(player).then(
        lambda p=player, res=ActionFormResponse: handle_sub_option_selection(p, module_name, res, config)
    )

def handle_sub_option_selection(player: Player, module_name: str, result: ActionFormResponse, config: dict):
    if result.canceled or result.selection is None:
        return

    module_data = config.get("modules", {}).get(module_name, {})
    sub_options = list(module_data.keys())

    if result.selection < len(sub_options):
        sub_option = sub_options[result.selection]
        show_individual_settings(player, module_name, sub_option, config)

    else:
        show_modules_settings(player, config)  # Go back to module list

def show_individual_settings(player: Player, module_name: str, sub_option: str, config: dict):
    settings = config.get("modules", {}).get(module_name, {}).get(sub_option, {})

    if not isinstance(settings, dict):
        player.send_message(f"{errorLog()}{sub_option} is not a settings category.")
        return

    form = ActionFormData()
    form.title(f"{module_name} - {sub_option}")
    form.body("Select a setting to edit:")

    for setting_key in settings.keys():
        form.button(setting_key)

    form.button("Back")

    form.show(player).then(
        lambda p=player, res=ActionFormResponse: handle_setting_edit(p, module_name, sub_option, res, config)
    )

def handle_setting_edit(player: Player, module_name: str, sub_option: str, result: ActionFormResponse, config: dict):
    if result.canceled or result.selection is None:
        return

    settings = config.get("modules", {}).get(module_name, {}).get(sub_option, {})
    setting_keys = list(settings.keys())

    if result.selection < len(setting_keys):
        setting_key = setting_keys[result.selection]
        prompt_value_input(player, module_name, sub_option, setting_key, config)

    else:
        show_module_sub_options(player, module_name, config)  # Go back to sub-options list

def prompt_value_input(player: Player, module_name: str, sub_option: str, setting_key: str, config: dict):
    current_value = config.get("modules", {}).get(module_name, {}).get(sub_option, {}).get(setting_key, "")

    form = ModalFormData().title(f"Edit {setting_key}")
    form.text_field(f"Current Value: {current_value}\nEnter new value:", "")

    def on_submit(player: Player, response: ModalFormResponse):
        if response.canceled:
            player.send_message(f"{errorLog()}§cSettings update canceled.")
            return

        new_value = response.formValues[0].strip()
        if new_value == "":
            player.send_message(f"{infoLog()}No changes made.")
            return

        update_json_setting(player, module_name, sub_option, setting_key, new_value, config)

    form.show(player).then(lambda p, r: on_submit(p, r))

def update_json_setting(player: Player, module_name: str, sub_option: str, setting_key: str, new_value: str, config: dict):
    try:
        # Convert type accordingly
        current_value = config.get("modules", {}).get(module_name, {}).get(sub_option, {}).get(setting_key, "")

        if isinstance(current_value, bool):
            new_value = new_value.lower() in ["true", "1", "yes"]
        elif isinstance(current_value, int):
            new_value = int(new_value)
        elif isinstance(current_value, float):
            new_value = float(new_value)
        elif isinstance(current_value, list) or isinstance(current_value, dict):
            new_value = json.loads(new_value)  # Ensure proper JSON conversion

        config["modules"][module_name][sub_option][setting_key] = new_value
        save_config(config)

        player.send_message(f"{infoLog()}Updated §a{setting_key} §rsuccessfully!")
    except Exception as e:
        player.send_message(f"{errorLog()}Error updating setting: §c{str(e)}")
