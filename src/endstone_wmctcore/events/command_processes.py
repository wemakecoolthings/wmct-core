from endstone import ColorFormat
from endstone.event import PlayerCommandEvent, ServerCommandEvent
from typing import TYPE_CHECKING

from endstone_wmctcore.utils.dbUtil import UserDB
from endstone_wmctcore.utils.internalPermissionsUtil import check_internal_rank
from endstone_wmctcore.utils.prefixUtil import modLog, errorLog, infoLog
from endstone_wmctcore.commands import moderation_commands

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

def handle_command_preprocess(self: "WMCTPlugin", event: PlayerCommandEvent):
    command = event.command
    player = event.player
    args = command.split()

    # /me Crasher Fix
    if args and args[0].lstrip("/").lower() == "me" and command.count("@e") >= 5:
        event.player.add_attachment(self, "minecraft.command.me", False)
        event.is_cancelled = True

        # Log the staff message (TBD)

        # Kick the player
        player.kick("Crasher Detected")


    # Internal Permissions Handler
    if args and len(args) > 0 and args[0].lstrip("/").lower() in moderation_commands \
            or (len(args) > 0 and args[0].lstrip("/").lower() == "kick"): # Edge case for kick

        if len(args) < 2:
            player.send_message(f"{errorLog()}Invalid usage: Not enough arguments")
            event.is_cancelled = True
            return False

        if any("@" in arg for arg in args):
            player.send_message(f"{errorLog()}Invalid argument: @ symbols are not allowed for managed commands")
            event.is_cancelled = True
            return False

        target = self.server.get_player(args[1])
        if target and self.server.get_player(target.name).is_op:
            if target.xuid != player.xuid: # Allow you to punish OR remove a punishment from yourself
                event.is_cancelled = True
                event.player.send_message(
                    f"{modLog()}Player {ColorFormat.YELLOW}{target.name} {ColorFormat.GOLD}has higher permissions")
                return True

        elif target:
            db = UserDB("wmctcore_users.db")
            target_user = db.get_online_user(target.xuid)
            sender = db.get_online_user(player.xuid)

            if target_user and sender:
                is_valid = check_internal_rank(target_user.internal_rank, sender.internal_rank)
                if is_valid and not player.is_op:
                    event.is_cancelled = True
                    event.player.send_message(f"{modLog()}Player {ColorFormat.YELLOW}{target.name} {ColorFormat.GOLD}has higher permissions")

            db.close_connection()

        elif not target:
            db = UserDB("wmctcore_users.db")
            target_user = db.get_offline_user(args[1])
            sender = db.get_online_user(player.xuid)

            if target_user and sender:
                is_valid = check_internal_rank(target_user.internal_rank, sender.internal_rank)
                if is_valid and not player.is_op:
                    event.is_cancelled = True
                    event.player.send_message(
                        f"{modLog()}Player {ColorFormat.YELLOW}{target.name} {ColorFormat.GOLD}has higher permissions")

            db.close_connection()

    elif args and args[0].lstrip("/").lower() == "ban" or args[0].lstrip("/").lower() == "unban" or args[0].lstrip("/").lower() == "pardon":
        player.send_message(f"{errorLog()}Hardcoded Endstone Moderation Commands are disabled by wmctcore")
        event.is_cancelled = True
        return False

def handle_server_command_preprocess(self: "WMCTPlugin", event: ServerCommandEvent):
    command = event.command
    player = event.sender
    args = command.split()

    if args and args[0].lstrip("/").lower() == "ban" or args[0].lstrip("/").lower() == "unban" or args[0].lstrip(
            "/").lower() == "pardon":
        player.send_message(f"{errorLog()}Hardcoded Endstone Moderation Commands are disabled by wmctcore\n{infoLog()}Please use \"permban\" or \"removeban\"")
        event.is_cancelled = True
        return False