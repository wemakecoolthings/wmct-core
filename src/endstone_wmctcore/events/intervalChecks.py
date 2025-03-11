import threading
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from endstone import ColorFormat, Player

from endstone_wmctcore.utils.configUtil import load_config
from endstone_wmctcore.utils.loggingUtil import log, discordRelay
from endstone_wmctcore.utils.prefixUtil import modLog

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

afk_tracker = {}
death_tracker = {}
confirmed_afk = set()
confirmed_death = set()
interval_thread: Optional[threading.Timer] = None

def interval_function(self: "WMCTPlugin"):
    global interval_thread
    now = datetime.now()
    config = load_config()

    for player in self.server.online_players:
        if player.is_dead:
            if player not in death_tracker:
                death_tracker[player] = now
            else:
                time_dead = (now - death_tracker[player]).total_seconds()
                if time_dead >= config["modules"]["check_prolonged_death_screen"]["time_in_seconds"] and \
                        config["modules"]["check_prolonged_death_screen"]["enabled"]:
                    self.server.dispatch_command(self.server.command_sender, "gamerule doimmediaterespawn true")
                    if player not in confirmed_death:
                        if config["modules"]["check_prolonged_death_screen"]["kick"]:
                            log(self, f"{modLog()}Player {ColorFormat.YELLOW}{player.name} {ColorFormat.GOLD}was kicked for Prolonged Death Screen", "mod")
                            player.kick(f"{ColorFormat.RED}Detected: Prolonged Death Screen Exploit")
                            remove_from_saved_areas(self, player)
                        else:
                            log(self, f"{modLog()}Player {ColorFormat.YELLOW}{player.name} {ColorFormat.GOLD}was detected to be stuck on Death Screen", "mod")
                        confirmed_death.add(player)
        else:
            if player in death_tracker:
                del death_tracker[player]
            if player in confirmed_death:
                confirmed_death.remove(player)

        if player not in afk_tracker:
            afk_tracker[player] = (player.location, now)
        else:
            saved_loc, last_move_time = afk_tracker[player]
            if player.location == saved_loc:
                time_afk = (now - last_move_time).total_seconds()
                if time_afk >= config["modules"]["check_afk"]["time_in_seconds"] and \
                        config["modules"]["check_afk"]["enabled"]:
                    if player not in confirmed_afk:
                        if config["modules"]["check_afk"]["kick"]:
                            log(self, f"{modLog()}Player {ColorFormat.YELLOW}{player.name} {ColorFormat.GOLD}was kicked for AFK", "mod")
                            player.kick(f"{ColorFormat.RED}Detected: AFK")
                            remove_from_saved_areas(self, player)
                        else:
                            log(self, f"{modLog()}Player {ColorFormat.YELLOW}{player.name} {ColorFormat.GOLD}was detected to be AFK", "mod")
                        confirmed_afk.add(player)
            else:
                if player in confirmed_afk:
                    confirmed_afk.remove(player)
                afk_tracker[player] = (player.location, now)

    interval_thread = threading.Timer(1, lambda: interval_function(self))
    interval_thread.start()

def stop_interval():
    global interval_thread
    if interval_thread:
        interval_thread.cancel()
        interval_thread = None

def remove_from_saved_areas(self: "WMCTPlugin", player: Player):
    if player in death_tracker:
        del death_tracker[player]
    if player in afk_tracker:
        del afk_tracker[player]
    if player in confirmed_afk:
        confirmed_afk.remove(player)
    if player in confirmed_death:
        confirmed_death.remove(player)
