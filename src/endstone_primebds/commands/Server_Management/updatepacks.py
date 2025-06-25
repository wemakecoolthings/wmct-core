import os
import json
import requests
from endstone import ColorFormat, Player
from endstone.command import CommandSender

import endstone_primebds
from endstone_primebds.utils.commandUtil import create_command
from endstone_primebds.utils.prefixUtil import infoLog, errorLog, trailLog
from endstone_primebds.utils.formWrapperUtil import ActionFormData, ActionFormResponse

# Register command
command, permission = create_command(
    "updatepacks",
    "Updates the server packs!",
    ["/updatepacks (resource|behavior|all)<target_pack: target_pack>"],
    ["primebds.command.reloadpacks"]
)

# RELOADPACKS FUNCTIONALITY
def handler(self, sender: CommandSender, args: list[str]) -> bool:
    current_dir = os.path.dirname(endstone_primebds.__file__)
    while not os.path.exists(os.path.join(current_dir, 'worlds')):
        current_dir = os.path.dirname(current_dir)

    RP_PATH = os.path.join(current_dir, 'worlds', self.server.level.name, 'resource_packs')
    BP_PATH = os.path.join(current_dir, 'worlds', self.server.level.name, 'behavior_packs')

    # Handle Resource Packs
    if "resource" in args or "all" in args:
        if not os.path.exists(RP_PATH):
            sender.send_message(f"{errorLog()} No resource packs found to update")
            return False

        updated_packs = 0
        updated_pack_names = []  # List to store names of updated packs
        for pack in os.listdir(RP_PATH):
            pack_path = os.path.join(RP_PATH, pack)
            manifest_path = os.path.join(pack_path, "manifest.json")
            if not os.path.isfile(manifest_path):
                continue

            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)

                # Increment version
                header_version = manifest.get("header", {}).get("version", [1, 0, 0])
                header_version[-1] += 1  # Increment last number
                manifest["header"]["version"] = header_version

                # Write back updated manifest
                with open(manifest_path, "w", encoding="utf-8") as f:
                    json.dump(manifest, f, indent=4)

                updated_packs += 1
                updated_pack_names.append(pack)  # Add the updated pack name to the list
            except Exception as e:
                sender.send_message(f"{errorLog()} Failed to update {pack}: {e}")
                continue

        # Send message with updated pack names
        if updated_packs > 0:
            sender.send_message(
                f"{infoLog()}Updated {updated_packs} resource pack(s): {', '.join(updated_pack_names)}!\n{ColorFormat.GRAY}{ColorFormat.ITALIC}REQUIRES SERVER RESTART TO APPLY")
        else:
            sender.send_message(f"{errorLog()} No resource packs were updated.")

    # Handle Behavior Packs
    if "behavior" in args or "all" in args:
        if not os.path.exists(BP_PATH):
            sender.send_message(f"{errorLog()} No behavior packs found to update")
            return False
        else:
            select_pack(sender, BP_PATH)
        return True

def select_pack(sender: CommandSender, path) -> None:
    packs = [pack for pack in os.listdir(path) if os.path.isdir(os.path.join(path, pack))]

    if not packs:
        sender.send_message(f"{errorLog()} No behavior packs found.")
        return

    form = ActionFormData()
    form.title("Select Behavior Pack")
    form.body("Choose a behavior pack to update:")

    for pack in packs:
        form.button(pack)

    form.button("Cancel")

    form.show(sender).then(
        lambda player=sender, result=ActionFormResponse: select_dependency(player, result, packs, path)
    )

def select_dependency(player: Player, result: ActionFormResponse, packs, path):
    if result.canceled or int(result.selection) >= len(packs):
        return

    # Get the chosen pack from the list of packs
    chosen_pack = packs[result.selection] if result.selection is not None else None
    if not chosen_pack:
        return

    manifest_path = os.path.join(path, chosen_pack, "manifest.json")

    if not os.path.exists(manifest_path):
        player.send_message(f"{errorLog()}No manifest file found for {chosen_pack}.")
        return

    try:
        # Open the manifest file and load its contents
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        # Extract dependencies from the manifest
        dependencies = manifest.get("dependencies", [])

        if not dependencies:
            player.send_message(f"{errorLog()}No dependencies found for {chosen_pack}.")
            return

        # Create the form to display dependencies
        form = ActionFormData()
        form.title(f"Select Dependency for {chosen_pack}")
        form.body("Choose a dependency to update:")

        # Add buttons for each dependency found in the manifest
        for dep in dependencies:
            form.button(dep.get("module_name") + " - " + dep.get("version"))

        # Add Cancel Button
        form.button("Cancel")

        # Show the form to the player and proceed based on their selection
        form.show(player).then(
            lambda p=player, result=ActionFormResponse: select_version(p, result, dependencies, manifest_path, chosen_pack, path)
        )

    except Exception as e:
        player.send_message(f"{errorLog()} Failed to load dependencies for {chosen_pack}: {e}")

def select_version(player: Player, result: ActionFormResponse, dep, manifest_path, chosen_pack, path):
    if result.canceled or int(result.selection) >= len(dep):
        return

    # Get the selected dependency
    chosen_dep = dep[result.selection] if result.selection is not None else None
    if not chosen_dep:
        player.send_message(f"{infoLog()}Action canceled or invalid selection.")
        return

    module_name = chosen_dep.get("module_name")
    npm_url = f"https://registry.npmjs.org/{module_name}"

    try:
        response = requests.get(npm_url)
        response.raise_for_status()

        data = response.json()
        all_versions = list(data.get("versions", {}).keys())[::-1]  # Reverse to show newest first

    except requests.RequestException as e:
        player.send_message(f"Error fetching versions for {module_name}: {e}")
        return

    def show_version_menu(page=0):

        page_lim = 10

        form = ActionFormData()
        total_pages = (len(all_versions) // page_lim) + 1
        form.title(f"{module_name} Ver (Page {page + 1}/{total_pages})")
        form.body("Choose a version:")

        start_index = page * page_lim
        end_index = min(start_index + page_lim, len(all_versions))
        page_versions = all_versions[start_index:end_index]

        for version in page_versions:
            form.button(version)

        if start_index > 0:
            form.button("<- Previous Page")
        if end_index < len(all_versions):
            form.button("Next Page ->")

        def on_version_selected(player: Player, response: ActionFormResponse):
            if response.canceled:
                return

            index = response.selection
            total_buttons = len(page_versions)

            if start_index > 0 and index == total_buttons:  # Previous Page
                show_version_menu(page - 1)
            elif end_index < len(all_versions) and index == total_buttons + (start_index > 0):  # Next Page
                show_version_menu(page + 1)
            else:  # A version was selected
                chosen_version = page_versions[int(index)]

                lower_version = chosen_version.lower()
                if "beta" in lower_version or "preview" in lower_version:
                    split_version = chosen_version.split(".")
                    for i in range(len(split_version)):
                        if "beta" in split_version[i].lower() or "preview" in split_version[i].lower():
                            major_version = ".".join(split_version[:i + 1])  # Keep everything up to "beta" or "preview"
                            break
                    else:
                        major_version = chosen_version  # Fallback
                else:
                    major_version = chosen_version  # Keep full version

                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        manifest = json.load(f)

                    # Loop through the list of dependencies to find the correct one to update
                    for dependency in manifest["dependencies"]:
                        if dependency["module_name"] == module_name:  # Assuming 'module_name' is provided as input
                            dependency["version"] = major_version  # Update the version
                            break  # Stop once the correct dependency is updated

                    # Save the updated manifest back to the file
                    with open(manifest_path, "w", encoding="utf-8") as f:
                        json.dump(manifest, f, indent=4)

                    select_pack(player, path)

                except Exception as e:
                    print(f"Error reading or writing manifest file: {e}")

                player.send_message(f"{infoLog()}Selected {module_name} - {chosen_version} {ColorFormat.GRAY}({ColorFormat.WHITE}Saved as {ColorFormat.YELLOW}{major_version}{ColorFormat.GRAY})\n{trailLog()}Updated {chosen_pack} {ColorFormat.GRAY}- {ColorFormat.ITALIC}REQUIRES SERVER RESTART TO APPLY")

        form.show(player).then(
            lambda p=player, result=ActionFormResponse: on_version_selected(p, result)
        )

    show_version_menu()
