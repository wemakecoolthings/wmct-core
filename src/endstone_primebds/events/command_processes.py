from endstone import ColorFormat
from endstone.event import PlayerCommandEvent, ServerCommandEvent
from typing import TYPE_CHECKING

from endstone_primebds.utils.configUtil import load_config
from endstone_primebds.utils.dbUtil import UserDB
from endstone_primebds.utils.internalPermissionsUtil import check_internal_rank
from endstone_primebds.utils.loggingUtil import log, discordRelay
from endstone_primebds.utils.prefixUtil import modLog, errorLog, infoLog, noticeLog
from endstone_primebds.commands import moderation_commands

if TYPE_CHECKING:
    from endstone_primebds.primebds import PrimeBDS

def handle_command_preprocess(self: "PrimeBDS", event: PlayerCommandEvent):
    command = event.command
    player = event.player
    args = command.split()

    config = load_config()
    if config["modules"]["game_logging"]["commands"]["enabled"]:
        log(self, f"{noticeLog()}{ColorFormat.YELLOW}{player.name} {ColorFormat.GOLD}ran: {ColorFormat.AQUA}{command}", "cmd")
    if config["modules"]["discord_logging"]["commands"]["enabled"]:
        discordRelay(f"**{player.name}** ran: {command}", "cmd")

    # /me Crasher Fix
    if (args and args[0].lstrip("/").lower() == "me"
            and args[0].lstrip("/").lower() == "tell"
            and args[0].lstrip("/").lower() == "w"
            and args[0].lstrip("/").lower() == "msg"
            and command.count("@e") >= 5):
        event.player.add_attachment(self, "minecraft.command.me", False)
        event.player.add_attachment(self, "minecraft.command.tell", False)
        event.player.add_attachment(self, "minecraft.command.w", False)
        event.player.add_attachment(self, "minecraft.command.msg", False)
        event.is_cancelled = True

        # Log the staff message
        if config["modules"]["me_crasher_patch"]["enabled"]:
            if config["modules"]["me_crasher_patch"]["ban"]:
                self.server.dispatch_command(self.server.command_sender, f"tempban {player.name} 7 day Crasher Exploit")
            else:
                log(self, f"{modLog()}Player {ColorFormat.YELLOW}{player.name} {ColorFormat.GOLD}was kicked due to {ColorFormat.YELLOW}Crasher Exploit", "mod")
                player.kick("Crasher Detected")

    # Internal Permissions Handler
    db = UserDB("userInfo.db")
    if ((db.get_online_user(player.xuid).internal_rank == "Operator" and not player.has_permission("minecraft.kick")) or
            (db.get_online_user(player.xuid).internal_rank == "Default" and player.is_op) or not player.has_permission("primebds.command.refresh")):
        self.reload_custom_perms(player)

    if args and len(args) > 0 and args[0].lstrip("/").lower() in moderation_commands \
            or (len(args) > 0 and args[0].lstrip("/").lower() == "kick"): # Edge case for kick

        if args[0].lstrip("/").lower() == "punishments":
            return True

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
            target_user = db.get_online_user(target.xuid)
            sender = db.get_online_user(player.xuid)

            if target_user and sender:
                is_valid = check_internal_rank(target_user.internal_rank, sender.internal_rank)
                if is_valid and not player.is_op:
                    event.is_cancelled = True
                    event.player.send_message(f"{modLog()}Player {ColorFormat.YELLOW}{target.name} {ColorFormat.GOLD}has higher permissions")

        elif not target:
            target_user = db.get_offline_user(args[1])
            sender = db.get_online_user(player.xuid)

            if target_user and sender:
                is_valid = check_internal_rank(target_user.internal_rank, sender.internal_rank)
                if is_valid and not player.is_op:
                    event.is_cancelled = True
                    event.player.send_message(
                        f"{modLog()}Player {ColorFormat.YELLOW}{target.name} {ColorFormat.GOLD}has higher permissions")

    elif args and args[0].lstrip("/").lower() == "ban" or args[0].lstrip("/").lower() == "unban" or args[0].lstrip("/").lower() == "pardon":
        player.send_message(f"{errorLog()}Hardcoded Endstone Moderation Commands are disabled by primebds")
        event.is_cancelled = True
        return False

    db.close_connection()

def handle_server_command_preprocess(self: "PrimeBDS", event: ServerCommandEvent):
    command = event.command
    player = event.sender
    args = command.split()

    if args and args[0].lstrip("/").lower() == "ban" or args[0].lstrip("/").lower() == "unban" or args[0].lstrip(
            "/").lower() == "pardon":
        player.send_message(f"{errorLog()}Hardcoded Endstone Moderation Commands are disabled by primebds\n{infoLog()}Please use \"permban\" or \"removeban\"")
        event.is_cancelled = True
        return False