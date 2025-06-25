from datetime import datetime
from typing import TYPE_CHECKING, Optional

from endstone import ColorFormat, Player

from endstone_primebds.utils.configUtil import load_config
from endstone_primebds.utils.loggingUtil import log, discordRelay
from endstone_primebds.utils.prefixUtil import modLog

if TYPE_CHECKING:
    from endstone_primebds.primebds import PrimeBDS

afk_tracker = {}
death_tracker = {}
confirmed_afk = set()
confirmed_death = set()

# This will hold the task ID for canceling if needed
interval_task_id: Optional[int] = None

def interval_function(self: "PrimeBDS"):
    # Reschedule the task to run again in 1 second
    global interval_task_id
    task = self.server.scheduler.run_task(self, lambda: run_checks(self), delay=20, period=20)
    interval_task_id = task.task_id

def run_checks(self: "PrimeBDS"):
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
                    if player not in confirmed_death:
                        self.server.dispatch_command(self.server.command_sender, "gamerule doimmediaterespawn true")
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

def stop_interval(self: "PrimeBDS"):
    global interval_task_id
    if interval_task_id:
        self.server.scheduler.cancel_task(interval_task_id)
        interval_task_id = None

def remove_from_saved_areas(self: "PrimeBDS", player: Player):
    if player in death_tracker:
        del death_tracker[player]
    if player in afk_tracker:
        del afk_tracker[player]
    if player in confirmed_afk:
        confirmed_afk.remove(player)
    if player in confirmed_death:
        confirmed_death.remove(player)
