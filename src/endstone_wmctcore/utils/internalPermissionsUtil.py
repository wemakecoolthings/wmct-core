# Define ranks in order of hierarchy
RANKS = ["Default", "Helper", "Mod", "Admin", "Operator"]

# Define permissions associated with each rank
PERMISSIONS = {
    "Default": [],
    "Helper": [],
    "Mod": [],
    "Admin": [],
    "Operator": []
}

def get_permissions(rank: str) -> list:
    """
    Returns a list of permissions associated with a given rank.
    If the rank is invalid, returns an empty list.
    """
    return PERMISSIONS.get(rank, [])

def check_internal_rank(user1_rank: str, user2_rank: str) -> bool:
    """
    Checks if user1 has a lower rank than user2.
    Returns True if user1_rank is lower, otherwise False.
    """
    if user1_rank not in RANKS or user2_rank not in RANKS:
        return False  # Handle cases where the rank is not found
    return RANKS.index(user1_rank) < RANKS.index(user2_rank)
