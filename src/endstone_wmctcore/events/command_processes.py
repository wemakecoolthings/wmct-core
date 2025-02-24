from endstone.event import event_handler, PlayerCommandEvent, ServerCommandEvent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from endstone_wmctcore.wmctcore import WMCTPlugin

@event_handler
def handle_command_preprocess(self: "WMCTPlugin", event: PlayerCommandEvent):
    command = event.command
    player = event.player  # Get the player who issued the command
    if command.startswith("/me") >= 1:
        if command.count("@e") >= 5:
            event.player.add_attachment(self, "minecraft.command.me", False)
            event.is_cancelled = True

            # Log the staff message
            # TBD

            # Kick the player
            player.kick("Crasher Detected")
