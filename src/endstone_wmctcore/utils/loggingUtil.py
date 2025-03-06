from typing import TYPE_CHECKING
from endstone_wmctcore.utils.dbUtil import UserDB
from endstone_wmctcore.utils.internalPermissionsUtil import has_log_perms
from endstone_wmctcore.utils.configUtil import load_config

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

def log(self: "WMCTPlugin", message):
    config = load_config()
    admin_tags = set(config["modules"]["game_logging"].get("custom_tags", []))

    db = UserDB("wmctcore_users.db")

    for player in self.server.online_players:
        user = db.get_online_user(player.xuid)
        if has_log_perms(user.internal_rank) or admin_tags.intersection(set(player.scoreboard_tags)):
            if db.enabled_logs(player.xuid):
                player.send_message(message)
                return True

    db.close_connection()

    return False
