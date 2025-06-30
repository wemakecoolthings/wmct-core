from typing import TYPE_CHECKING
from time import time

from endstone import GameMode
from endstone._internal.endstone_python import Vector
from endstone.event import ActorDamageEvent, ActorKnockbackEvent

from endstone_primebds.utils.configUtil import load_config

if TYPE_CHECKING:
    from endstone_primebds.primebds import PrimeBDS

def handle_damage_event(self: "PrimeBDS", ev: ActorDamageEvent):
    config = load_config()

    entity = ev.actor  # Entity taking damage
    entity_key = f"{entity.type}:{entity.id}"
    current_time = time()
    last_hit_time = self.entity_damage_cooldowns.get(entity_key, 0)

    tags = []
    if hasattr(ev, 'damage_source') and ev.damage_source:
        actor = getattr(ev.damage_source, 'actor', None)
        if actor and hasattr(actor, 'scoreboard_tags'):
            tags = actor.scoreboard_tags or []

    # Get tag-aware values
    modifier = get_custom_tag(config, tags, "base_damage")
    kb_cooldown = get_custom_tag(config, tags, "hit_cooldown_in_seconds")

    # Apply bonus damage
    if modifier != 1:
        ev.damage += modifier

    # Apply cooldown logic
    if current_time - last_hit_time >= kb_cooldown:
        self.entity_damage_cooldowns[entity_key] = current_time
    else:
        ev.is_cancelled = True

    return

def handle_kb_event(self: "PrimeBDS", ev: ActorKnockbackEvent):
    config = load_config()
    source = self.server.get_player(ev.source.name)

    tags = source.scoreboard_tags or []

    kb_h_modifier = get_custom_tag(config, tags, "horizontal_knockback_modifier")
    kb_v_modifier = get_custom_tag(config, tags, "vertical_knockback_modifier")
    kb_sprint_h_modifier = get_custom_tag(config, tags, "horizontal_sprint_knockback_modifier")
    kb_sprint_v_modifier = get_custom_tag(config, tags, "vertical_sprint_knockback_modifier")

    # If base modifiers are 0, treat them as "do not modify"
    if kb_h_modifier == 0 and kb_v_modifier == 0 and kb_sprint_h_modifier == 0 and kb_sprint_v_modifier == 0:
        return

    kb_h_modifier = kb_h_modifier or 1.0
    kb_v_modifier = kb_v_modifier or 1.0
    kb_sprint_h_modifier = kb_sprint_h_modifier or 1.0
    kb_sprint_v_modifier = kb_sprint_v_modifier or 1.0

    newx = ev.knockback.x * kb_h_modifier
    newy = ev.knockback.y * kb_v_modifier
    newz = ev.knockback.z * kb_h_modifier

    if ev.knockback.x == 0 or ev.knockback.z == 0:
        newx = source.velocity.x * kb_h_modifier
        newz = source.velocity.z * kb_h_modifier

    if source.is_sprinting and kb_sprint_h_modifier != 1.0:
        newx *= kb_sprint_h_modifier
        newz *= kb_sprint_h_modifier

    if ev.knockback.y < 0:
        newy = (newy * kb_sprint_v_modifier) / 2

    new_kb = Vector(newx, abs(newy), newz)
    ev.knockback = new_kb


def get_custom_tag(config, tags, key):
    """
    Returns the custom KB modifiers, prioritizing tag-specific modifiers.
    If no matching tag or key is found, falls back to global value.
    """
    default = config["modules"]["combat"].get(key)

    tag_mods = config["modules"]["combat"].get("tag_modifiers", {})
    for tag in tags:
        if tag in tag_mods and key in tag_mods[tag]:
            return tag_mods[tag][key]

    return default
