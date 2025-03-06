import sqlite3
import time
from dataclasses import dataclass
import pytz
from datetime import datetime
from typing import List, Tuple, Any, Dict, Optional
from endstone import ColorFormat
import endstone_wmctcore
from endstone_wmctcore.utils.modUtil import format_time_remaining
from endstone_wmctcore.utils.prefixUtil import modLog

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
    enabled_logs: str

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
class PunishmentLog:
    id: int
    xuid: str
    name: str
    action_type: str
    reason: str
    timestamp: int
    duration: Optional[int]

@dataclass
class GriefAction:
    id: int
    xuid: str
    action: str
    location: str
    timestamp: int

# DB
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

    def close_connection(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

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
            'internal_rank': 'TEXT',
            'enabled_logs': 'INTEGER'
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

        punishment_log_columns = {
            'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'xuid': 'TEXT',
            'name': 'TEXT',
            'action_type': 'TEXT',
            'reason': 'TEXT',
            'timestamp': 'INTEGER',
            'duration': 'INTEGER'
        }
        self.create_table('punishment_logs', punishment_log_columns)

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

        # Determine rank
        internal_rank = "Operator" if player.is_op else "Default"

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
                'internal_rank': internal_rank,
                'enabled_logs': 1
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
                'client_ver': client_ver
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

    def get_all_players(self) -> list:
        """Fetches a list of all players from the database."""
        self.cursor.execute("SELECT DISTINCT name FROM punishment_logs")
        return [row[0] for row in self.cursor.fetchall()]

    def enabled_logs(self, xuid: str) -> bool:
        """Checks if logging is enabled for a user by their XUID."""
        query = "SELECT enabled_logs FROM users WHERE xuid = ?"
        self.cursor.execute(query, (xuid,))
        result =  self.cursor.fetchone()

        return result is not None and result[0] == 1  # True if enabled_logs is 1

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

        # Log ban action
        log_data = {
            'xuid': xuid,
            'name': self.get_name_by_xuid(xuid),
            'action_type': 'Ban',
            'reason': reason,
            'timestamp': int(time.time()),
            'duration': expiration
        }
        self.insert('punishment_logs', log_data)

    def add_mute(self, xuid: str, expiration: int, reason: str):

        updates = {
            'is_muted': 1,
            'mute_time': expiration,
            'mute_reason': reason
        }
        condition = 'xuid = ?'
        params = (xuid,)
        self.update('mod_logs', updates, condition, params)

        # Log mute action
        log_data = {
            'xuid': xuid,
            'name': self.get_name_by_xuid(xuid),
            'action_type': 'Mute',
            'reason': reason,
            'timestamp': int(time.time()),
            'duration': expiration
        }
        self.insert('punishment_logs', log_data)

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

        # Log unban action
        log_data = {
            'xuid': self.get_xuid_by_name(name),
            'name': name,
            'action_type': 'Unban',
            'reason': 'Ban Removed',
            'timestamp': int(time.time()),
            'duration': 0
        }
        self.insert('punishment_logs', log_data)

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

        # Log unmute action
        log_data = {
            'xuid': self.get_xuid_by_name(name),
            'name': name,
            'action_type': 'Unmute',
            'reason': 'Mute Removed',
            'timestamp': int(time.time()),
            'duration': 0
        }
        self.insert('punishment_logs', log_data)

    def print_punishment_history(self, name: str, page: int = 1):
        """Retrieve all punishments for a user, showing active ones (ban/mute) first and paginate the results."""

        # Query the mod_logs table to check if the player is banned or muted
        query_mod_log = """
            SELECT is_muted, mute_time, mute_reason, is_banned, banned_time, ban_reason, is_ip_banned 
            FROM mod_logs 
            WHERE name = ?
        """
        self.cursor.execute(query_mod_log, (name,))
        mod_log_result = self.cursor.fetchone()

        if not mod_log_result:
            return False

        is_muted, mute_time, mute_reason, is_banned, banned_time, ban_reason, is_ip_banned = mod_log_result

        # Query punishment_logs to get timestamps of active punishments
        query_active_punishments = """
            SELECT action_type, timestamp 
            FROM punishment_logs 
            WHERE name = ? AND (action_type = 'Ban' OR action_type = 'Mute') 
            ORDER BY timestamp DESC
        """
        self.cursor.execute(query_active_punishments, (name,))
        active_punishment_logs = self.cursor.fetchall()

        active_punishments = {}
        active_timestamps = set()

        est = pytz.timezone('America/New_York')
        for action_type, timestamp in active_punishment_logs:
            if action_type == "Ban" and is_banned and timestamp < banned_time and "Ban" not in active_punishments:
                ban_expires_in = format_time_remaining(banned_time)

                ip_ban_status = ""
                if is_ip_banned:
                    ip_ban_status = "IP "

                active_punishments["Ban"] = (
                    timestamp,
                    f"{ColorFormat.RED}{ip_ban_status}Ban {ColorFormat.GRAY}- {ColorFormat.YELLOW}{ban_reason} {ColorFormat.GRAY}({ColorFormat.YELLOW}{ban_expires_in}{ColorFormat.GRAY})\n"
                    f"{ColorFormat.ITALIC}Date Issued: {ColorFormat.GRAY}{datetime.fromtimestamp(timestamp, est).strftime('%Y-%m-%d %I:%M:%S %p %Z')}{ColorFormat.RESET}"
                )
                active_timestamps.add(timestamp)

            elif action_type == "Mute" and is_muted and timestamp < mute_time and "Mute" not in active_punishments:
                mute_expires_in = format_time_remaining(mute_time, True)
                active_punishments["Mute"] = (
                    timestamp,
                    f"{ColorFormat.BLUE}Mute {ColorFormat.GRAY}- {ColorFormat.YELLOW}{mute_reason} {ColorFormat.GRAY}({ColorFormat.YELLOW}{mute_expires_in}{ColorFormat.GRAY})\n"
                    f"{ColorFormat.ITALIC}Date Issued: {ColorFormat.GRAY}{datetime.fromtimestamp(timestamp, est).strftime('%Y-%m-%d %I:%M:%S %p %Z')}{ColorFormat.RESET}"
                )
                active_timestamps.add(timestamp)

        # Query to fetch all past punishments
        query = """
            SELECT action_type, reason, timestamp, duration 
            FROM punishment_logs 
            WHERE name = ? 
            ORDER BY timestamp DESC
        """
        self.cursor.execute(query, (name,))
        result = self.cursor.fetchall()

        if not result:
            return False

        past_punishments = []

        for row in result:
            action_type, reason, timestamp, duration = row
            time_applied = datetime.fromtimestamp(timestamp, pytz.utc).astimezone(est).strftime(
                '%Y-%m-%d %I:%M:%S %p %Z')

            time_status = "EXPIRED"

            punishment_entry = f"{ColorFormat.BLUE}{action_type} {ColorFormat.GRAY}- {ColorFormat.YELLOW}{reason} {ColorFormat.GRAY}({ColorFormat.YELLOW}{time_status}{ColorFormat.GRAY})\n" \
                               f"{ColorFormat.ITALIC}Date Issued: {ColorFormat.GRAY}{time_applied}{ColorFormat.RESET}"

            # Only add past punishments that do not match the timestamp of an active one
            if timestamp not in active_timestamps:
                past_punishments.append(punishment_entry)

        # Paginate (5 per page)
        per_page = 5
        total_pages = (len(past_punishments) + per_page - 1) // per_page
        start = (page - 1) * per_page
        end = start + per_page
        paginated_history = past_punishments[start:end]

        # Build response
        msg = [f"{modLog()}Punishment Information\n---------------"]

        if active_punishments:
            msg.append(
                f"{ColorFormat.GREEN}Active {ColorFormat.GOLD}Punishments for {ColorFormat.YELLOW}{name}{ColorFormat.GOLD}:"
            )
            for _, entry in active_punishments.values():
                msg.append(f"§7- {entry}")
            msg.append(f"{ColorFormat.GOLD}---------------")

        msg.append(
            f"{ColorFormat.DARK_RED}Past {ColorFormat.GOLD}Punishments for {ColorFormat.YELLOW}{name}{ColorFormat.GOLD}:§r"
        )

        for entry in paginated_history:
            msg.append(f"§7- {entry}")

        msg.append(f"{ColorFormat.GOLD}---------------")

        # Show navigation hint
        if page < total_pages:
            msg.append(f"§8Use §e/punishments {name} {page + 1} §8for more.")

        return "\n".join(msg)

    def get_punishment_logs(self, name: str) -> Optional[List[PunishmentLog]]:
        """Fetches all punishment logs for a given player based on their name."""
        query = "SELECT * FROM punishment_logs WHERE name = ?"
        self.cursor.execute(query, (name,))
        results = self.cursor.fetchall()  # Use fetchall() to get all results

        if results:
            punishment_logs = []
            for result in results:
                punishment_logs.append(
                    PunishmentLog(
                        id=result[0],
                        xuid=result[1],
                        name=result[2],
                        action_type=result[3],
                        reason=result[4],
                        timestamp=result[5],
                        duration=result[6] if result[6] is not None else None
                    )
                )
            return punishment_logs
        return None

    def delete_all_punishment_logs_by_name(self, name: str):
        """Deletes all punishment logs for a specific player by name."""
        query = "DELETE FROM punishment_logs WHERE name = ?"
        self.cursor.execute(query, (name,))
        self.conn.commit()

        # Check if the deletion was successful
        if self.cursor.rowcount > 0:
            return True
        else:
            return False

    def remove_punishment_log_by_id(self, name: str, log_id: int):
        """Removes a punishment log for a specific player based on its ID (position)."""
        query = "DELETE FROM punishment_logs WHERE name = ? AND id = ?"
        self.cursor.execute(query, (name, log_id))
        self.conn.commit()

        # Check if the deletion was successful
        if self.cursor.rowcount > 0:
            return True
        else:
            return False

    def get_xuid_by_name(self, player_name: str) -> str:
        """Fetch the xuid of a player by their name."""
        query = "SELECT xuid FROM mod_logs WHERE name = ?"
        self.cursor.execute(query, (player_name,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            raise ValueError(f"Player {player_name} not found in database.")

    def get_name_by_xuid(self, xuid: str) -> str:
        """Fetch the xuid of a player by their name."""
        query = "SELECT name FROM mod_logs WHERE xuid = ?"
        self.cursor.execute(query, (xuid,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            raise ValueError(f"XUID {xuid} not found in database.")

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

    def update_user_data(self, name: str, column: str, value):
        """Updates a specific column for an existing user in the 'users' table."""
        if column not in ['xuid', 'uuid', 'name', 'ping', 'device_os', 'client_ver',
                          'last_join', 'last_leave', 'internal_rank', 'enabled_logs']:
            raise ValueError(f"Invalid column name: {column}")

        condition = 'name = ?'
        params = (name,)
        updates = {column: value}
        self.update('users', updates, condition, params)

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