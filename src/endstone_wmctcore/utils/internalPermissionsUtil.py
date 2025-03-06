# Define ranks in order of hierarchy
RANKS = ["Default", "Helper", "Mod", "Operator"]

# Define permissions associated with each rank
PERMISSIONS = {
    "Default": ["wmctcore.command.spectate", "wmctcore.command.ping"],
    "Helper": ["wmctcore.command.check", "wmctcore.command.monitor"],
    "Mod": ["wmctcore.command.ipban", "wmctcore.command.mute", "wmctcore.command.permban", "wmctcore.command.punishments",
            "wmctcore.command.removeban", "wmctcore.command.tempban", "wmctcore.command.tempmute", "wmctcore.command.unmute",
            "wmctcore.command.nick", "wmctcore.command.logs"],
    "Operator": ["*"]
}

def get_permissions(rank: str) -> list[str]:
    """Returns a list of all permissions for a given rank, including inherited ones."""
    inherited_permissions = []
    rank_order = ["Default", "Helper", "Mod", "Operator"]

    for r in rank_order:
        inherited_permissions.extend(PERMISSIONS.get(r, []))
        if r == rank:
            break  # Stop once we reach the requested rank

    return inherited_permissions

def has_log_perms(rank: str) -> bool:
    """Returns True if the rank has logging permissions (Mod or higher), otherwise False."""
    return rank in RANKS[RANKS.index("Mod"):]

def check_internal_rank(user1_rank: str, user2_rank: str) -> bool:
    """
    Checks if user1 has a lower rank than user2.
    Returns True if user1_rank is lower, otherwise False.
    """
    if user1_rank not in RANKS or user2_rank not in RANKS:
        return False  # Handle cases where the rank is not found
    return RANKS.index(user1_rank) < RANKS.index(user2_rank)
