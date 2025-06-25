from endstone.command import CommandSender
from endstone_primebds.utils.commandUtil import create_command
from endstone_primebds.utils.prefixUtil import infoLog, errorLog, trailLog
from endstone_primebds.utils.dbUtil import GriefLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_primebds.primebds import PrimeBDS

# Register command
command, permission = create_command(
    "playtime",
    "Displays your total playtime or the server leaderboard.",
    ["/playtime [leaderboard: bool]"],
    ["primebds.command.playtime"],
    "true"
)

# PLAYTIME COMMAND FUNCTIONALITY
def handler(self: "PrimeBDS", sender: CommandSender, args: list[str]) -> bool:
    player_name = sender.name
    player = self.server.get_player(player_name)

    if len(args) == 0:
        dbgl = GriefLog("primebds_gl.db")

        # Fetch total playtime for the player
        total_playtime_seconds = dbgl.get_total_playtime(player.xuid)
        total_playtime_minutes = total_playtime_seconds // 60
        total_playtime_hours = total_playtime_minutes // 60
        total_playtime_days = total_playtime_hours // 24
        total_playtime_hours %= 24
        total_playtime_minutes %= 60
        total_playtime_seconds %= 60

        # Fetch leaderboard information
        leaderboard = dbgl.get_all_playtimes()

        # Find the player's rank
        player_rank = None
        for index, entry in enumerate(leaderboard):
            if entry['name'] == player_name:
                player_rank = index + 1
                break

        # Determine the rank suffix
        if player_rank:
            rank_suffix = get_rank_suffix(player_rank)
        else:
            rank_suffix = "N/A"

        # Send the total playtime and rank
        sender.send_message(
            f"{infoLog()}§rYour Playtime: §f{total_playtime_days}d {total_playtime_hours}h {total_playtime_minutes}m {total_playtime_seconds}s §7§o({player_rank}{rank_suffix})§r")

        dbgl.close_connection()
    elif len(args) == 1 and args[0].lower() == 'true':
        # Display leaderboard
        dbgl = GriefLog("primebds_gl.db")
        leaderboard = dbgl.get_all_playtimes()
        leaderboard = sorted(leaderboard, key=lambda x: x['total_playtime'], reverse=True)

        sender.send_message(f"{infoLog()}§rTop 10 Playtimes on the Server:")

        # Show the top 10 players' playtimes
        for index, entry in enumerate(leaderboard[:10]):
            player_name = entry['name']
            total_playtime_seconds = entry['total_playtime']
            total_playtime_minutes = total_playtime_seconds // 60
            total_playtime_hours = total_playtime_minutes // 60
            total_playtime_days = total_playtime_hours // 24
            total_playtime_hours %= 24
            total_playtime_minutes %= 60
            total_playtime_seconds %= 60

            # Calculate the rank and its suffix
            rank = index + 1
            rank_suffix = get_rank_suffix(rank)

            sender.send_message(
                f"{trailLog()}§e{rank}{rank_suffix}. §a{player_name} - §f{total_playtime_days}d {total_playtime_hours}h {total_playtime_minutes}m {total_playtime_seconds}s")

        dbgl.close_connection()
    else:
        # If incorrect arguments are passed
        sender.send_message(f"{errorLog()}Usage: /playtime [leaderboard]")

    return True

def get_rank_suffix(rank: int) -> str:
    if 10 <= rank % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(rank % 10, 'th')
    return suffix