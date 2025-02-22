class CommandRegister:
    @staticmethod
    def create_command(command_name: str, description: str, permissions: list):
        command = {
            command_name: {
                "description": description,
                "usages": [f"/{command_name}"],
                "permissions": permissions
            }
        }

        permission = {
            permissions[0]: {  # Assuming the first permission is the main one
                "description": f"Allows use of {command_name} command",
                "default": "true"
            }
        }

        return command, permission
