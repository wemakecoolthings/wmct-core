from endstone import Player, ColorFormat
from endstone.command import CommandSender
from endstone_wmctcore.utils.commandUtil import create_command
from endstone_wmctcore.utils.dbUtil import UserDB
from endstone_wmctcore.utils.internalPermissionsUtil import RANKS
from endstone_wmctcore.utils.prefixUtil import infoLog, errorLog, noticeLog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

# Register command
command, permission = create_command(
    "setrank",
    "Sets the internal permissions for a player!",
    ["/setrank <player: player> (default|helper|mod|admin|operator)<rank: rank>"],
    ["wmctcore.command.setrank"]
)

# SETRANK COMMAND FUNCTIONALITY
def handler(self: "WMCTPlugin", sender: CommandSender, args: list[str]) -> bool:
    db = UserDB("wmctcore_users.db")
    player_name = args[0]
    new_rank = args[1].lower()  # Convert input rank to lowercase for comparison

    # Fetch user data
    user = db.get_offline_user(player_name)
    if user:
        current_rank = user.internal_rank

        # Check if the rank needs to be updated
        if current_rank.lower() == new_rank.lower():
            sender.send_message(f"{errorLog()}Player {player_name} already has the rank {new_rank}. No changes made.")
            db.close_connection()
            return False

        # Update the user's rank in the database
        for rank in RANKS:
            if rank.lower() == new_rank:
                db.update_user_rank_data(player_name, rank)

                # Reload permissions if the player is online
                online_target = self.server.get_player(player_name)
                if online_target:
                    if new_rank == "operator":
                        self.server.dispatch_command(self.server.command_sender, f"op {player_name}")
                    else:
                        self.server.dispatch_command(self.server.command_sender, f"deop {player_name}")
                        if online_target.is_op:
                            sender.send_message(
                                f"{noticeLog()}Warning: internal OP level is currently set to 4 meaning their OP status cannot be reverted automatically")

                    self.reload_custom_perms(online_target)

                sender.send_message(
                    f"{infoLog()}Player {ColorFormat.YELLOW}{player_name}'s {ColorFormat.WHITE}rank was updated to {ColorFormat.YELLOW}{rank.upper()}")
                db.close_connection()
                return True
    else:
        sender.send_message(f"{errorLog()}Could not find user data for player {player_name}.")

    db.close_connection()
    return False
