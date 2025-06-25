from endstone import Player, boss, ColorFormat
from endstone.command import CommandSender
from endstone_primebds.utils.commandUtil import create_command
from endstone_primebds.utils.prefixUtil import infoLog, errorLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_primebds.primebds import PrimeBDS

# Cache for boss bars {player: boss_bar}
boss_bar_cache = {}

# Register command
command, permission = create_command(
    "bossbar",
    "Sets or removes a client-sided bossbar display!",
    [
        "/bossbar <player: player> (red|blue|green|yellow|pink|purple|rebecca_purple|white)<color: set_color> <progress: float> (solid|segmented_6|segmented_10|segmented_12|segmented_20)<style: set_style> <title: string> [is_dark: bool]",
        "/bossbar (all)<selector: All> (red|blue|green|yellow|pink|purple|rebecca_purple|white)<color: set_all_color> <progress: float> (solid|segmented_6|segmented_10|segmented_12|segmented_20)<style: set_all_style> <title: string> [is_dark: bool]",
        "/bossbar <player: player> (remove)<remove_boss_bar: remove_boss_bar>",
        "/bossbar (all)<selector: All> (remove)<remove_boss_bar: remove_all_boss_bar>"
    ],
    ["primebds.command.bossbar"]
)

# BOSSBAR COMMAND FUNCTIONALITY
def handler(self: "PrimeBDS", sender: CommandSender, args: list[str]) -> bool:
    global boss_bar_cache

    if args[1] == "remove":
        # Check if there are any boss bars stored
        if not boss_bar_cache:
            sender.send_message(f"{errorLog()}No active boss bars to remove!")
            return False

        # Handle boss bar removal
        if args[0] == "all":
            removed_count = 0
            for player in list(boss_bar_cache.keys()):
                bar = boss_bar_cache[player]
                bar.remove_player(player)

                # Only remove from cache if the bar has no players left
                if not bar.players:
                    del boss_bar_cache[player]

                removed_count += 1

            sender.send_message(f"{infoLog()}Removed boss bars from {removed_count} player(s)!")
            return True

        else:
            target = self.server.get_player(args[0])
            if target and target in boss_bar_cache:
                bar = boss_bar_cache[target]
                bar.remove_player(target)

                # Only delete from cache if it's empty
                if not bar.players:
                    del boss_bar_cache[target]

                sender.send_message(f"{infoLog()}Removed boss bar for {args[0]}!")
                return True
            else:
                sender.send_message(f"{errorLog()}No boss bar found for {args[0]}!")
                return False

    # Parse command arguments
    try:
        color = getattr(boss.BarColor, args[1].upper(), boss.BarColor.RED)
        progress = max(0, min(100, int(args[2])))  # Ensure progress is between 0-100
        style = getattr(boss.BarStyle, args[3].upper(), boss.BarStyle.SOLID)
        title = args[4]
        is_dark = bool(args[5]) if len(args) > 5 else False
    except (ValueError, IndexError):
        sender.send_message(f"{errorLog()}Invalid command usage!")
        return False

    # Create boss bar
    flags = [boss.BarFlag.DARKEN_SKY] if is_dark else []
    bar = self.server.create_boss_bar(title, color, style, flags)
    bar.progress = progress / 100  # Convert to decimal format (0.0 to 1.0)

    def remove_existing_bossbar(player: Player):
        """ Removes the player from their existing boss bar if they have one. """
        if player in boss_bar_cache:
            existing_bar = boss_bar_cache[player]
            existing_bar.remove_player(player)
            if not existing_bar.players: 
                del boss_bar_cache[player]

    if args[0] == "all":
        for player in self.server.online_players:
            remove_existing_bossbar(player)  
            bar.add_player(player)
            boss_bar_cache[player] = bar 
    else:
        target = self.server.get_player(args[0])
        if target:
            remove_existing_bossbar(target)  
            bar.add_player(target)
            boss_bar_cache[target] = bar  
        else:
            sender.send_message(f"{errorLog()}Player {args[0]} not found!")
            return False

    if sender != "Server":
        sender.send_message(f"{infoLog()}{ColorFormat.AQUA}Bossbar Set For {args[0]}:\n"
                            f"{ColorFormat.DARK_GRAY}---------------\n"
                            f"{ColorFormat.YELLOW}Color: {ColorFormat.RESET}{args[1]}\n"
                            f"{ColorFormat.YELLOW}Progress: {ColorFormat.RESET}{progress}%\n"
                            f"{ColorFormat.YELLOW}Style: {ColorFormat.RESET}{args[3]}\n"
                            f"{ColorFormat.YELLOW}Darkened Sky: {ColorFormat.RESET}{is_dark}\n"
                            f"{ColorFormat.DARK_GRAY}---------------")
    return True
