import threading
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from endstone import ColorFormat, Player

from endstone_wmctcore.utils.configUtil import load_config
from endstone_wmctcore.utils.loggingUtil import log, discordRelay

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Track AFK and death times
afk_tracker = {}
death_tracker = {}

def interval_function(self: "WMCTPlugin"):
    now = datetime.now()
    config = load_config()

    for player in self.server.online_players:
        if player.is_dead:
            if player not in death_tracker:
                death_tracker[player] = now
            else:
                time_dead = (now - death_tracker[player]).total_seconds()
                if time_dead >= config["modules"]["check_prolonged_death_screen"]["time_in_seconds"] and config["modules"]["check_prolonged_death_screen"]["enabled"]:
                    if config["modules"]["check_prolonged_death_screen"]["kick"]:
                        log(self, f"{player.name} was kicked for Prolonged Death Screen", "mod")
                        player.kick(f"{ColorFormat.RED}Detected: Prolonged Death Screen Exploit")
                        remove_from_saved_areas(self, player)
                    else:
                        discordRelay(f"{player.name} was detected to be AFK", "mod")
        else:
            if player in death_tracker:
                del death_tracker[player]  # Reset death timer on respawn

        if player not in afk_tracker:
            afk_tracker[player] = (player.location, now)
        else:
            saved_loc, last_move_time = afk_tracker[player]
            if player.location == saved_loc:
                time_afk = (now - last_move_time).total_seconds()
                if time_afk >= config["modules"]["check_afk"]["time_in_seconds"] and config["modules"]["check_afk"]["enabled"]:
                    if config["modules"]["check_afk"]["kick"]:
                        log(self, f"{player.name} was kicked for AFK", "mod")
                        player.kick(f"{ColorFormat.RED}Detected: AFK")
                        remove_from_saved_areas(self, player)
                    else:
                        discordRelay(f"{player.name} was detected to be AFK", "mod")
            else:
                # Reset AFK timer when player moves
                afk_tracker[player] = (player.location, now)

    # Run again every second
    threading.Timer(1, lambda: interval_function(self)).start()

def remove_from_saved_areas(self: "WMCTPlugin", player: Player):
    """
    Clears any saved areas or active sessions for a player if they are kicked.
    This prevents lingering data in memory after a kick.
    """
    if player in death_tracker:
        del death_tracker[player]
    if player in afk_tracker:
        del afk_tracker[player]
