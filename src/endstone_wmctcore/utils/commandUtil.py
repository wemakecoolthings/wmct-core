# Declare `i` globally
allArgCount = 0

def create_command(command_name: str, description: str, usages: list, permissions: list, default: str = "op", aliases: list = None):
    global allArgCount
    new_usages = []

    for usage in usages:
        if "(all)[selector: All]" in usage:
            allArgCount += 1
            modified_usage = usage.replace("(all)[selector: All]", f"(all)[selector: All_{allArgCount}]")
            new_usages.append(modified_usage)
        else:
            new_usages.append(usage)

    # Create the command dictionary with all its details
    command = {
        command_name: {
            "description": description,
            "usages": new_usages,
            "permissions": permissions,
            "aliases": aliases if aliases else []
        }
    }

    # Define the permission dictionary, assuming the first permission is the main one
    permission = {
        permissions[0]: {
            "description": f"Allows use of the {command_name} command",
            "default": default
        }
    }

    return command, permission
