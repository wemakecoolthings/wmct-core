import sqlite3
import time
from typing import List, Tuple, Any, Dict

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

# DB
class UserDB(DatabaseManager):
    def __init__(self, db_name: str):
        """Initialize the database connection and create tables."""
        super().__init__(db_name)  # Call DatabaseManager's init
        self.create_tables()

    def create_tables(self):
        """Create tables if they don't exist."""
        columns = {
            'xuid': 'INTEGER PRIMARY KEY',
            'uuid': 'INTEGER',
            'name': 'TEXT',
            'ping': 'INTEGER',
            'device': 'TEXT',
            'client_ver': 'TEXT',
            'last_join': 'INTEGER',
            'last_leave': 'INTEGER'
        }
        self.create_table('users', columns)
        
        action_log_columns = {
            'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'xuid': 'INTEGER',
            'action': 'TEXT',
            'location': 'TEXT',
            'timestamp': 'INTEGER'
        }
        self.create_table('actions_log', action_log_columns)

    def log_action(self, xuid: int, action: str, location: str, timestamp: int):
        """Logs an action performed by a player."""
        data = {
            'xuid': xuid,
            'action': action,
            'location': location,
            'timestamp': timestamp
        }
        self.insert('actions_log', data)

    def delete_old_logs(self, cutoff_timestamp: int):
        """Deletes logs older than a given timestamp."""
        condition = 'timestamp < ?'
        params = (cutoff_timestamp,)
        self.delete('actions_log', condition, params)

    def save_user(self, player):
        """Checks if a user exists and saves them if not."""
        xuid = player.xuid
        uuid = player.unique_id
        name = player.name
        ping = player.ping
        device = player.device_os
        client_ver = player.game_version
        last_join = int(time.time())  # Corrected to call time() to get the current timestamp
        last_leave = 0

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
                'last_leave': last_leave
            }
            self.insert('users', data)
            return True 
        else:
            return False

    def update_user_join_time(self, xuid: int, new_join_time: int):
        """Updates the join time for an existing user in the 'users' table."""
        condition = 'xuid = ?'
        params = (xuid,)
        
        updates = {
            'last_join': new_join_time
        }
        
        self.update('users', updates, condition, params)

    def update_user_leave_time(self, xuid: int, new_leave_time: int):
        """Updates the leave time for an existing user in the 'users' table."""
        condition = 'xuid = ?'
        params = (xuid,)
        
        updates = {
            'last_leave': new_leave_time
        }
        
        self.update('users', updates, condition, params)

    def close_connection(self):
        """Closes the database connection."""
        self.close()
