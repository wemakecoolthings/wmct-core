import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Tuple, Any, Dict, Optional
from endstone import ColorFormat
from endstone.util import Vector
from endstone_wmctcore.utils.modUtil import format_time_remaining
from endstone_wmctcore.utils.prefixUtil import modLog
from endstone_wmctcore.utils.timeUtil import TimezoneUtils

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
    block_type: str
    block_state: str

# DB
class DatabaseManager:
    def __init__(self, db_name: str):
        """Initialize the database connection."""
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
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
        self.player_data_cache = {}
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
        """Checks if a user exists and saves them if not, updating cache."""
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

        user = self.player_data_cache.get(xuid)

        if not user:
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

            self.player_data_cache[xuid] = data
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

            # Update cache
            if xuid in self.player_data_cache:
                self.player_data_cache[xuid].update(updates)
            return True

    def _get_from_cache(self, xuid: str, name: str = None) -> Optional[dict]:
        """Private method to check cache for user or mod log data."""
        if xuid in self.player_data_cache:
            if name and self.player_data_cache[xuid].get("name") == name:
                return self.player_data_cache[xuid]
            elif not name:
                return self.player_data_cache[xuid]
        return None

    def get_mod_log(self, xuid: str) -> Optional[ModLog]:
        """Retrieve moderation log for a user, using cache when available."""
        cached_data = self._get_from_cache(xuid)
        if cached_data and "mod_log" in cached_data:
            return cached_data["mod_log"]

        query = "SELECT * FROM mod_logs WHERE xuid = ?"
        self.cursor.execute(query, (xuid,))
        result = self.cursor.fetchone()

        if result:
            mod_log = ModLog(
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

            self.player_data_cache[xuid] = self.player_data_cache.get(xuid, {})
            self.player_data_cache[xuid]["mod_log"] = mod_log

            return mod_log
        return None

    def get_online_user(self, xuid: str) -> Optional[User]:
        """Retrieves all user data as an object, checking cache first."""
        cached_data = self._get_from_cache(xuid)
        if cached_data:
            return User(**cached_data)

        query = "SELECT * FROM users WHERE xuid = ?"
        self.cursor.execute(query, (xuid,))
        result = self.cursor.fetchone()

        if result:
            user = User(*result)
            self.player_data_cache[xuid] = user.__dict__ 
            return user
        return None

    def get_offline_user(self, name: str) -> Optional[User]:
        """Retrieves all user data as an object by name, checking cache first."""
        for xuid, data in self.player_data_cache.items():
            if data.get("name") == name:
                return User(**data)

        query = "SELECT * FROM users WHERE name = ?"
        self.cursor.execute(query, (name,))
        result = self.cursor.fetchone()

        if result:
            user = User(*result)
            self.player_data_cache[result[0]] = user.__dict__  
            return user
        return None

    def get_all_players(self) -> list:
        """Fetches a list of all players from the database."""
        self.cursor.execute("SELECT DISTINCT name FROM punishment_logs")
        return [row[0] for row in self.cursor.fetchall()]

    def enabled_logs(self, xuid: str) -> bool:
        """Checks if logging is enabled for a user by their XUID."""
        query = "SELECT enabled_logs FROM users WHERE xuid = ?"
        self.cursor.execute(query, (xuid,))
        result =  self.cursor.fetchone()

        return result is not None and result[0] == 1

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
        self.cursor.execute(query, (f"{ip_base}%",))
        result = self.cursor.fetchone()

        return result is not None

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

        for action_type, timestamp in active_punishment_logs:
            formatted_time = TimezoneUtils.convert_to_timezone(timestamp, 'EST')

            if action_type == "Ban" and is_banned and timestamp < banned_time and "Ban" not in active_punishments:
                ban_expires_in = format_time_remaining(banned_time)

                ip_ban_status = "IP " if is_ip_banned else ""
                active_punishments["Ban"] = (
                    timestamp,
                    f"{ColorFormat.RED}{ip_ban_status}Ban {ColorFormat.GRAY}- {ColorFormat.YELLOW}{ban_reason} "
                    f"{ColorFormat.GRAY}({ColorFormat.YELLOW}{ban_expires_in}{ColorFormat.GRAY})\n"
                    f"{ColorFormat.ITALIC}Date Issued: {ColorFormat.GRAY}{formatted_time}{ColorFormat.RESET}"
                )
                active_timestamps.add(timestamp)

            elif action_type == "Mute" and is_muted and timestamp < mute_time and "Mute" not in active_punishments:
                mute_expires_in = format_time_remaining(mute_time, True)
                active_punishments["Mute"] = (
                    timestamp,
                    f"{ColorFormat.BLUE}Mute {ColorFormat.GRAY}- {ColorFormat.YELLOW}{mute_reason} "
                    f"{ColorFormat.GRAY}({ColorFormat.YELLOW}{mute_expires_in}{ColorFormat.GRAY})\n"
                    f"{ColorFormat.ITALIC}Date Issued: {ColorFormat.GRAY}{formatted_time}{ColorFormat.RESET}"
                )
                active_timestamps.add(timestamp)

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
            formatted_time = TimezoneUtils.convert_to_timezone(timestamp, 'EST')

            time_status = "EXPIRED"
            punishment_entry = (
                f"{ColorFormat.BLUE}{action_type} {ColorFormat.GRAY}- {ColorFormat.YELLOW}{reason} "
                f"{ColorFormat.GRAY}({ColorFormat.YELLOW}{time_status}{ColorFormat.GRAY})\n"
                f"{ColorFormat.ITALIC}Date Issued: {ColorFormat.GRAY}{formatted_time}{ColorFormat.RESET}"
            )

            if timestamp not in active_timestamps:
                past_punishments.append(punishment_entry)

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

        if page < total_pages:
            msg.append(f"§8Use §e/punishments {name} {page + 1} §8for more.")

        return "\n".join(msg)

    def get_punishment_logs(self, name: str) -> Optional[List[PunishmentLog]]:
        """Fetches all punishment logs for a given player based on their name."""
        query = "SELECT * FROM punishment_logs WHERE name = ?"
        self.cursor.execute(query, (name,))
        results = self.cursor.fetchall() 

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

        if self.cursor.rowcount > 0:
            return True
        else:
            return False

    def remove_punishment_log_by_id(self, name: str, log_id: int):
        """Removes a punishment log for a specific player based on its ID (position)."""
        query = "DELETE FROM punishment_logs WHERE name = ? AND id = ?"
        self.cursor.execute(query, (name, log_id))
        self.conn.commit()

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

    def get_name_by_xuid(self, xuid: str) -> str:
        """Fetch the xuid of a player by their name."""
        query = "SELECT name FROM mod_logs WHERE xuid = ?"
        self.cursor.execute(query, (xuid,))
        result = self.cursor.fetchone()
        if result:
            return result[0]

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
        """Updates a specific column for an existing user in the 'users' table and updates cache."""
        if column not in ['xuid', 'uuid', 'name', 'ping', 'device_os', 'client_ver',
                          'last_join', 'last_leave', 'internal_rank', 'enabled_logs']:
            return

        condition = 'name = ?'
        params = (name,)
        updates = {column: value}
        self.update('users', updates, condition, params)

        for xuid, data in self.player_data_cache.items():
            if data.get("name") == name:
                self.player_data_cache[xuid][column] = value
                if column == "name":
                    self.player_data_cache[value] = self.player_data_cache.pop(xuid)
                break 

class GriefLog(DatabaseManager):
    """Handles actions related to grief logs and session tracking."""

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
            'x': 'REAL',
            'y': 'REAL',
            'z': 'REAL',
            'timestamp': 'INTEGER',
            'block_type': 'TEXT',
            'block_state': 'TEXT'
        }
        session_log_columns = {
            'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'xuid': 'TEXT',
            'name': 'TEXT',
            'start_time': 'INTEGER',
            'end_time': 'INTEGER'
        }
        user_toggle_columns = {
            'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'xuid': 'TEXT',
            'name': 'TEXT',
            'inspect_mode': 'BOOLEAN'
        }
        self.create_table('actions_log', action_log_columns)
        self.create_table('sessions_log', session_log_columns)
        self.create_table('user_toggles', user_toggle_columns)  

    def set_user_toggle(self, xuid: str, name: str):
        """Toggles the inspect mode for a player."""

        existing_toggle = self.get_user_toggle(xuid, name)

        if existing_toggle:
            new_toggle = not existing_toggle[3]  # Assuming 'inspect_mode' is at index 3
            updates = {'inspect_mode': new_toggle}
            condition = 'xuid = ?'
            params = (xuid,)

            try:
                self.update('user_toggles', updates, condition, params)
            except Exception as e:
                print(f"Error updating data: {e}")
        else:
            data = {'xuid': xuid, 'name': name, 'inspect_mode': True}
            try:
                self.insert('user_toggles', data)
            except Exception as e:
                print(f"Error inserting data: {e}")

        self.conn.commit()

    def get_user_toggle(self, xuid: str, name: str):
        """Gets the current inspect mode toggle for a player.
        If no result exists, insert a new default value with name and inspect_mode.
        """
        query = "SELECT * FROM user_toggles WHERE xuid = ?"
        self.cursor.execute(query, (xuid,))
        result = self.cursor.fetchone()

        if result is None:
            default_value = 0  
            insert_query = """
                INSERT INTO user_toggles (xuid, name, inspect_mode) 
                VALUES (?, ?, ?)
            """
            self.cursor.execute(insert_query, (xuid, name, default_value))
            self.conn.commit()

            self.cursor.execute(query, (xuid,))
            result = self.cursor.fetchone()

        return result

    def get_logs_by_coordinates(self, x: float, y: float, z: float, player_name: str = None) -> list[dict]:
        """Returns logs based on coordinates and an optional player name filter."""
        query = "SELECT * FROM actions_log WHERE x = ? AND y = ? AND z = ?"
        params = [x, y, z]  

        if player_name:
            query += " AND name = ?"
            params.append(player_name)

        self.cursor.execute(query, tuple(params))
        logs = self.cursor.fetchall()

        result = []
        for log in logs:
            result.append({
                'id': log[0],
                'xuid': log[1],
                'name': log[2],
                'action': log[3],
                'location': f"{log[4]},{log[5]},{log[6]}",  # Rebuilding the location string
                'timestamp': log[7],
                'block_type': log[8], 
                'block_state': log[9] 
            })
        return result

    def get_logs_by_player(self, player_name: str) -> list[dict]:
        """Returns all logs for a given player name."""
        query = "SELECT * FROM actions_log WHERE name = ?"
        self.cursor.execute(query, (player_name,))
        logs = self.cursor.fetchall()

        result = []
        for log in logs:
            result.append({
                'id': log[0],
                'xuid': log[1],
                'name': log[2],
                'action': log[3],
                'location': log[4],
                'timestamp': log[5],
                'block_type': log[8],  
                'block_state': log[9] 
            })
        return result

    def get_logs_within_radius(self, x: float, y: float, z: float, radius: float) -> List[dict]:
        """Returns logs within a defined radius of the given coordinates."""
        # Query to check for the existence of 'block_type' and 'block_state' columns
        self.cursor.execute("PRAGMA table_info(actions_log);")
        columns = [column[1] for column in self.cursor.fetchall()]
        has_block_type = 'block_type' in columns
        has_block_state = 'block_state' in columns

        # SQL query to fetch logs within the radius
        query = """
        SELECT * FROM actions_log
        WHERE (POWER(x - ?, 2) + POWER(y - ?, 2) + POWER(z - ?, 2)) <= POWER(?, 2)
        """
        self.cursor.execute(query, (x, y, z, radius))
        logs = self.cursor.fetchall()

        result = []
        for log in logs:
            log_dict = {
                'id': log[0],
                'xuid': log[1],
                'name': log[2],
                'action': log[3],
                'location': f"{log[4]},{log[5]},{log[6]}",  # Rebuilding the location string
                'timestamp': log[7],
            }
            if has_block_type:
                log_dict['block_type'] = log[8]
            if has_block_state:
                log_dict['block_state'] = log[9]
            result.append(log_dict)

        return result

    def log_action(self, xuid: str, name: str, action: str, location, timestamp: int, block_type: str = None,
                   block_state: str = None):
        """Logs an action performed by a player, stores x, y, z as separate coordinates, and includes block data if available."""
        # Parse the location if it's a Vec object (assuming it has x, y, z attributes)
        if isinstance(location, Vector):
            x, y, z = location.x, location.y, location.z
        else:
            # If it's not a Vec, assume it's a string or already formatted location
            x, y, z = map(float, location.split(','))

        # Prepare additional block data if available
        data = {
            'xuid': xuid,
            'name': name,
            'action': action,
            'x': x,
            'y': y,
            'z': z,
            'timestamp': timestamp,
        }

        if block_type:
            data['block_type'] = block_type  # Log block type (if applicable)

        if block_state:
            data['block_state'] = block_state  # Log block state (if applicable)

        self.insert('actions_log', data)

    def start_session(self, xuid: str, name: str, start_time: int):
        """Logs the start of a player session and automatically ends any previous sessions in case of a crash."""
        # Fetch the latest session for this player
        current_session = self.get_current_session(xuid)
        if current_session:
            # Automatically end any previous session if it is still open
            self.end_session(xuid, int(time.time()))

        # Now log the new session as a start
        data = {
            'xuid': xuid,
            'name': name,
            'start_time': start_time,
            'end_time': None
        }
        self.insert('sessions_log', data)

    def end_session(self, xuid: str, end_time: int):
        """Logs the end of a player session."""
        query = """
            UPDATE sessions_log
            SET end_time = ?
            WHERE xuid = ? AND end_time IS NULL
        """
        self.cursor.execute(query, (end_time, xuid))
        self.conn.commit()

    def get_current_session(self, xuid: str):
        """Fetches the most recent active session for a player (where end_time is None)."""
        query = "SELECT * FROM sessions_log WHERE xuid = ? AND end_time IS NULL ORDER BY start_time DESC LIMIT 1"
        self.cursor.execute(query, (xuid,))
        result = self.cursor.fetchone()

        if result:
            return result  # Returns the session data if an active session is found
        return None  # Return None if there is no active session

    def get_user_sessions(self, xuid: str) -> list[dict]:
        """
        Gets all sessions for a player with start and end times.
        Automatically calculates the duration for active sessions.
        """
        query = "SELECT start_time, end_time FROM sessions_log WHERE xuid = ?"
        self.cursor.execute(query, (xuid,))
        sessions = self.cursor.fetchall()

        result = []
        for start_time, end_time in sessions:
            if end_time is None:
                duration = int(time.time()) - start_time
                end_time_display = None
            else:
                duration = end_time - start_time
                end_time_display = end_time

            result.append({
                'start_time': start_time,
                'end_time': end_time_display,
                'duration': duration
            })
        return result

    def get_total_playtime(self, xuid: str) -> int:
        """
        Gets the total playtime of a player in seconds.
        Automatically calculates ongoing session times if still active.
        """
        query = "SELECT start_time, end_time FROM sessions_log WHERE xuid = ?"
        self.cursor.execute(query, (xuid,))
        sessions = self.cursor.fetchall()

        total_time = 0
        for start_time, end_time in sessions:
            if end_time:
                total_time += end_time - start_time
            else:
                total_time += int(time.time()) - start_time  # Active session

        return total_time

    def get_all_playtimes(self) -> list[dict]:
        """
        Gets a list of all users and their total playtimes.
        Includes active sessions in real-time.
        This function now searches by player name instead of xuid.
        """
        query = "SELECT xuid, name FROM sessions_log GROUP BY name"
        self.cursor.execute(query)
        users = self.cursor.fetchall()

        result = []
        for xuid, name in users:
            total_playtime = self.get_total_playtime(xuid)
            result.append({
                'xuid': xuid, 
                'name': name,
                'total_playtime': total_playtime
            })
        return result

    from datetime import datetime, timedelta

    def delete_logs_older_than_seconds(self, seconds: int, sendPrint=False):
        """Deletes logs that are older than the given seconds threshold and logs the action."""

        # Fetch current time
        current_time = datetime.utcnow()

        # Fetch logs and count them
        count_query = "SELECT COUNT(*) FROM actions_log"
        self.cursor.execute(count_query)
        count_result = self.cursor.fetchone()
        count = count_result[0] if count_result else 0

        if count == 0:
            print("[WMCTCORE - GriefLog] No logs to delete.")
            return

        # Fetch individual logs and check timestamps
        select_logs_query = "SELECT id, timestamp FROM actions_log"
        self.cursor.execute(select_logs_query)
        logs_to_delete = self.cursor.fetchall()

        # Perform deletion for each individual log that matches the condition
        deleted_count = 0
        for log in logs_to_delete:
            log_id, log_timestamp = log

            log_time = datetime.utcfromtimestamp(log_timestamp)
            time_difference = (current_time - log_time).total_seconds()

            # Compare the time difference with the input seconds
            if time_difference > seconds:
                delete_query = "DELETE FROM actions_log WHERE id = ?"
                self.cursor.execute(delete_query, (log_id,))
                deleted_count += 1

        self.conn.commit()

        time_units = [
            ("day", 86400),
            ("hour", 3600),
            ("minute", 60),
            ("second", 1)
        ]

        for unit, value in time_units:
            if seconds >= value:
                amount = seconds // value
                time_string = f"{amount} {unit}{'s' if amount > 1 else ''}"
                break

        # Final Log Message
        if sendPrint:
            print(f"[WMCTCORE - GriefLog] Purged {deleted_count} logs older than {time_string}")

        return deleted_count

    def delete_logs_within_seconds(self, seconds: int):
        """Deletes logs that are within the given seconds threshold and logs the action."""

        current_time = datetime.utcnow()

        select_logs_query = "SELECT id, timestamp FROM actions_log"
        self.cursor.execute(select_logs_query)
        logs_to_delete = self.cursor.fetchall()

        # Perform deletion for each individual log that matches the condition
        deleted_count = 0
        for log in logs_to_delete:
            log_id, log_timestamp = log

            log_time = datetime.utcfromtimestamp(log_timestamp)
            time_difference = (current_time - log_time).total_seconds()

            # Compare the time difference with the input seconds
            if time_difference <= seconds:
                delete_query = "DELETE FROM actions_log WHERE id = ?"
                self.cursor.execute(delete_query, (log_id,))
                deleted_count += 1

        self.conn.commit()

        return deleted_count

    def delete_all_logs(self):
        """Deletes all logs."""
        self.delete('actions_log', '1', ())  # '1' is just a condition that will match all logs