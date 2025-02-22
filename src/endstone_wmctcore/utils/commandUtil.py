def create_command(command_name: str, description: str, usages: list, permissions: list, aliases: list = None):
    command = {
        command_name: {
            "description": description,
            "usages": usages,
            "permissions": permissions,
            "aliases": aliases if aliases else []
        }
    }

    permission = {
        permissions[0]: {  # Assuming the first permission is the main one
            "description": f"Allows use of the {command_name} command",
            "default": "true"
        }
    }

    return command, permission