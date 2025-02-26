import sqlite3
import time
from dataclasses import dataclass
from ipaddress import ip_address
from typing import List, Tuple, Any, Dict, Optional

class DatabaseManager:
    def __init__(self, db_name: str):
        """Initialize the database connection."""
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name: str, columns: Dict[str, str]):
        """Create a table if it doesn't exist.
        Args:
            table_name (str): Name of the table.
            columns (Dict[str, str]): Column definitions as a dictionary.
        """
        column_definitions = ', '.join([f"{col} {dtype}" for col, dtype in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions})"
        self.cursor.execute(query)
        self.conn.commit()

    def insert(self, table_name: str, data: Dict[str, Any]):
        """Insert a row into the table."""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data.values()])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, tuple(data.values()))
        self.conn.commit()

    def fetch_all(self, table_name: str) -> List[Dict[str, Any]]:
        """Fetch all rows from a table."""
        self.cursor.execute(f"SELECT * FROM {table_name}")
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def fetch_by_condition(self, table_name: str, condition: str, params: Tuple) -> List[Dict[str, Any]]:
        """Fetch rows based on a condition."""
        query = f"SELECT * FROM {table_name} WHERE {condition}"
        self.cursor.execute(query, params)
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def update(self, table_name: str, updates: Dict[str, Any], condition: str, params: Tuple):
        """Update rows in the table."""
        update_clause = ', '.join([f"{col} = ?" for col in updates.keys()])
        query = f"UPDATE {table_name} SET {update_clause} WHERE {condition}"
        self.cursor.execute(query, tuple(updates.values()) + params)
        self.conn.commit()

    def delete(self, table_name: str, condition: str, params: Tuple):
        """Delete rows from the table."""
        query = f"DELETE FROM {table_name} WHERE {condition}"
        self.cursor.execute(query, params)
        self.conn.commit()

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

@dataclass
class User:
    xuid: str
    uuid: str
    name: str
    ping: int
    device_os: str
    client_ver: str
    last_join: int
    last_leave: int
    internal_rank: str


@dataclass
class ModLog:
    xuid: str
    name: str
    is_muted: bool
    mute_time: int
    mute_reason: str
    is_banned: bool
    banned_time: int
    ban_reason: str
    ip_address: str
    is_ip_banned: bool


@dataclass
class GriefAction:
    id: int
    xuid: str
    action: str
    location: str
    timestamp: int


class UserDB(DatabaseManager):
    def __init__(self, db_name: str):
        """Initialize the database connection and create tables."""
        super().__init__(db_name)
        self.db_name = db_name
        self.create_tables()

    def create_tables(self):
        """Create tables if they don't exist."""
        user_info_columns = {
            'xuid': 'TEXT PRIMARY KEY',
            'uuid': 'TEXT',
            'name': 'TEXT',
            'ping': 'INTEGER',
            'device_os': 'TEXT',
            'client_ver': 'TEXT',
            'last_join': 'INTEGER',
            'last_leave': 'INTEGER',
            'internal_rank': 'TEXT'
        }
        self.create_table('users', user_info_columns)

        moderation_log_columns = {
            'xuid': 'TEXT PRIMARY KEY',
            'name': 'TEXT',
            'is_muted': 'INTEGER',
            'mute_time': 'INTEGER',
            'mute_reason': 'TEXT',
            'is_banned': 'INTEGER',
            'banned_time': 'INTEGER',
            'ban_reason': 'TEXT',
            'ip_address': 'TEXT',
            'is_ip_banned': 'INTEGER'
        }
        self.create_table('mod_logs', moderation_log_columns)

    def save_user(self, player):
        """Checks if a user exists and saves them if not."""
        xuid = player.xuid
        uuid = str(player.unique_id)
        name = player.name
        ping = player.ping
        device = player.device_os
        client_ver = player.game_version
        last_join = int(time.time())
        last_leave = 0
        ip = str(player.address)

        self.cursor.execute("SELECT * FROM users WHERE xuid = ?", (xuid,))
        user = self.cursor.fetchone()

        if not user:
            data = {
                'xuid': xuid,
                'uuid': uuid,
                'name': name,
                'ping': ping,
                'device_os': device,
                'client_ver': client_ver,
                'last_join': last_join,
                'last_leave': last_leave,
                'internal_rank': 'Default'
            }

            mod_data = {
                'xuid': xuid,
                'name': name,
                'is_muted': 0,
                'mute_time': 0,
                'mute_reason': "None",
                'is_banned': 0,
                'banned_time': 0,
                'ban_reason': "None",
                'ip_address': ip,
                'is_ip_banned': 0
            }

            self.insert('users', data)
            self.insert('mod_logs', mod_data)
            return True
        else:
            condition = 'xuid = ?'
            params = (xuid,)
            updates = {
                'uuid': uuid,
                'name': name,
                'ping': ping,
                'device_os': device,
                'client_ver': client_ver,
                'last_join': int(time.time()),
            }
            self.update('users', updates, condition, params)
            return True

    def get_mod_log(self, xuid: str) -> Optional[ModLog]:
        query = "SELECT * FROM mod_logs WHERE xuid = ?"
        self.cursor.execute(query, (xuid,))
        result = self.cursor.fetchone()

        if result:
            return ModLog(
                xuid=result[0],
                name=result[1],
                is_muted=bool(result[2]),
                mute_time=result[3],
                mute_reason=result[4],
                is_banned=bool(result[5]),
                banned_time=result[6],
                ban_reason=result[7],
                ip_address=result[8],
                is_ip_banned=bool(result[9]),
            )
        return None

    def get_online_user(self, xuid: str) -> Optional[User]:
        """Retrieves all user data as an object."""
        query = "SELECT * FROM users WHERE xuid = ?"
        self.cursor.execute(query, (xuid,))
        result = self.cursor.fetchone()

        if result:
            return User(*result)
        return None  # Return None if user not found

    def get_offline_user(self, name: str) -> Optional[User]:
        """Retrieves all user data as an object."""
        query = "SELECT * FROM users WHERE name = ?"
        self.cursor.execute(query, (name,))
        result = self.cursor.fetchone()

        if result:
            return User(*result)
        return None  # Return None if user not found

    def add_ban(self, xuid, expiration: int, reason: str, ip_ban: bool = False):
        """Bans a player by updating the mod_logs table."""
        updates = {
            'is_banned': 1,
            'banned_time': expiration,
            'ban_reason': reason,
            'is_ip_banned': ip_ban
        }
        condition = 'xuid = ?'
        params = (xuid,)

        self.update('mod_logs', updates, condition, params)

    def add_mute(self, xuid: str, expiration: int, reason: str):

        updates = {
            'is_muted': 1,
            'mute_time': expiration,
            'mute_reason': reason
        }
        condition = 'xuid = ?'
        params = (xuid,)
        self.update('mod_logs', updates, condition, params)

    def remove_ban(self, name: str):
        """Bans a player by updating the mod_logs table."""
        updates = {
            'is_banned': 0,
            'banned_time': 0,
            'ban_reason': "None",
            'is_ip_banned': 0
        }
        condition = 'name = ?'
        params = (name,)

        self.update('mod_logs', updates, condition, params)

    def check_ip_ban(self, ip: str) -> bool:
        """Checks if the given IP address matches a user who is IP banned."""
        # Strip the port if the IP has one
        ip_base = ip.split(':')[0]

        query = "SELECT 1 FROM mod_logs WHERE ip_address LIKE ? AND is_ip_banned = 1 LIMIT 1"
        self.cursor.execute(query, (f"{ip_base}%",))  # % is used to match any port number
        result = self.cursor.fetchone()

        return result is not None  # Return True if a banned user is found, False otherwise

    def remove_mute(self,  name: str):
        updates = {
            'is_muted': 0,
            'mute_time': 0,
            'mute_reason': "None"
        }
        condition = 'name = ?'
        params = (name,)
        self.update('mod_logs', updates, condition, params)

    def get_xuid_by_name(self, player_name: str) -> str:
        """Fetch the xuid of a player by their name."""
        query = "SELECT xuid FROM mod_logs WHERE name = ?"
        self.cursor.execute(query, (player_name,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            raise ValueError(f"Player {player_name} not found in database.")

    def get_offline_mod_log(self, name: str) -> Optional[ModLog]:
        """Retrieves a user's moderation log as an object."""
        query = "SELECT * FROM mod_logs WHERE name = ?"
        self.cursor.execute(query, (name,))
        result = self.cursor.fetchone()

        if result:
            return ModLog(
                xuid=result[0],
                name=result[1],
                is_muted=bool(result[2]),
                mute_time=result[3],
                mute_reason=result[4],
                is_banned=bool(result[5]),
                banned_time=result[6],
                ban_reason=result[7],
                ip_address=result[8],
                is_ip_banned=bool(result[9]),
            )
        return None

    def update_user_leave_data(self, name: str):
        """Updates the leave time for an existing user in the 'users' table."""
        condition = 'name = ?'
        params = (name,)
        updates = {'last_leave': int(time.time())}
        self.update('users', updates, condition, params)

    def close_connection(self):
        """Closes the database connection."""
        self.close()

# CURRENTLY NOT IN USE BUT IN PROGRESS OF BEING MADE
class GriefLog(DatabaseManager):
    """Handles actions related to grief logs."""
    def __init__(self, db_name: str):
        """Initialize the database connection and create tables."""
        super().__init__(db_name)
        self.create_tables()

    def create_tables(self):
        """Create tables if they don't exist."""
        action_log_columns = {
            'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'xuid': 'TEXT',
            'name': 'TEXT',
            'action': 'TEXT',
            'location': 'TEXT',
            'timestamp': 'INTEGER'
        }
        self.create_table('actions_log', action_log_columns)

    def log_action(db, xuid: str, name: str, action: str, location: str, timestamp: int):
        """Logs an action performed by a player."""
        data = {
            'xuid': xuid,
            'name': name,
            'action': action,
            'location': location,
            'timestamp': timestamp
        }
        db.insert('actions_log', data)

    def get_grief_logs(db, name: str) -> list[GriefAction]:
        """Retrieves all logged actions for a user as a list of objects."""
        query = "SELECT * FROM actions_log WHERE name = ?"
        db.cursor.execute(query, (name,))
        results = db.cursor.fetchall()

        return [GriefAction(*row) for row in results] if results else []

    def delete_old_grief_logs(db, cutoff_timestamp: int):
        """Deletes logs older than a given timestamp."""
        condition = 'timestamp < ?'
        params = (cutoff_timestamp,)
        db.delete('actions_log', condition, params)

    def close_connection(self):
        """Closes the database connection."""
        self.close()
