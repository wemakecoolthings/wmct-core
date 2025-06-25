from datetime import datetime
from typing import TYPE_CHECKING

from endstone import ColorFormat
from endstone.event import PlayerMoveEvent, PlayerJumpEvent, ActorDamageEvent, ActorDeathEvent, ActorKnockbackEvent

if TYPE_CHECKING:
    from endstone_primebds.primebds import PrimeBDS

def handle_movement_event(self: "PrimeBDS", ev: PlayerMoveEvent):
    return

def handle_jump_event(self: "PrimeBDS", ev: PlayerJumpEvent):
    return

def handle_damage_event(self: "PrimeBDS", ev: ActorDamageEvent):
    return

def handle_kb_event(self: "PrimeBDS", ev: ActorDeathEvent):
    return

def handle_death_event(self: "PrimeBDS", ev: ActorKnockbackEvent):
    return