import os
import json
import endstone_wmctcore
from endstone import ColorFormat
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.prefixUtil import infoLog, errorLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "reloadpacks",
    "Reloads the server resource packs! [REQUIRES SERVER RESTART]",
    ["/reloadpacks"],
    ["wmctcore.command.reloadpacks"]
)

# RELOAD PACKS COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    RP_PATH = os.path.join(os.path.dirname(endstone_wmctcore.__file__), f'../../../../../worlds/{self.server.level.name}/resource_packs')

    if not os.path.exists(RP_PATH):
        sender.send_message(f"{errorLog()}No resource packs found to update")
        return False

    updated_packs = 0

    for pack in os.listdir(RP_PATH):
        pack_path = os.path.join(RP_PATH, pack)
        manifest_path = os.path.join(pack_path, "manifest.json")

        if not os.path.isfile(manifest_path):
            continue

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)

            # Increment last number in header version
            header_version = manifest.get("header", {}).get("version", [1, 0, 0])
            header_version[-1] += 1  # Increment the last number

            manifest["header"]["version"] = header_version

            # Write updated manifest back
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=4)

            updated_packs += 1
        except Exception as e:
            sender.send_message(f"{errorLog()}Failed to update {pack}: {e}")
            continue

    sender.send_message(f"{infoLog()}Updated {updated_packs} resource pack(s)! {ColorFormat.GRAY}{ColorFormat.ITALIC}[{ColorFormat.RED}REQUIRES SERVER RESTART{ColorFormat.GRAY}]")
    return True
