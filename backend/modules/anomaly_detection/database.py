"""
SQLite Database Module for Anomaly Detection Persistence
Handles storage and retrieval of anomaly events and chat histories
"""
import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Database file path
DB_PATH = Path(__file__).parent / "anomaly_data.db"


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    """Initialize database tables if they don't exist"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Anomaly events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anomaly_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                type TEXT NOT NULL,
                message TEXT,
                details TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Chat history table (linked to anomaly events)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anomaly_chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                anomaly_id INTEGER,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (anomaly_id) REFERENCES anomaly_events(id)
            )
        ''')
        
        conn.commit()
        logger.info(f"Database initialized at {DB_PATH}")


def save_anomaly_event(event: Dict[str, Any]) -> int:
    """
    Save an anomaly event to the database
    Returns the inserted event ID
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO anomaly_events (timestamp, type, message, details)
            VALUES (?, ?, ?, ?)
        ''', (
            event.get('timestamp'),
            event.get('type'),
            event.get('message'),
            json.dumps(event.get('details', {}))
        ))
        conn.commit()
        event_id = cursor.lastrowid
        logger.info(f"Saved anomaly event {event_id}: {event.get('type')}")
        return event_id


def get_anomaly_events(limit: int = 100) -> List[Dict[str, Any]]:
    """Retrieve anomaly events from database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, timestamp, type, message, details, created_at
            FROM anomaly_events
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        events = []
        for row in cursor.fetchall():
            events.append({
                'id': row['id'],
                'timestamp': row['timestamp'],
                'type': row['type'],
                'message': row['message'],
                'details': json.loads(row['details']) if row['details'] else {},
                'created_at': row['created_at']
            })
        return events


def get_anomaly_event_by_id(event_id: int) -> Optional[Dict[str, Any]]:
    """Get a specific anomaly event by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, timestamp, type, message, details, created_at
            FROM anomaly_events
            WHERE id = ?
        ''', (event_id,))
        
        row = cursor.fetchone()
        if row:
            return {
                'id': row['id'],
                'timestamp': row['timestamp'],
                'type': row['type'],
                'message': row['message'],
                'details': json.loads(row['details']) if row['details'] else {},
                'created_at': row['created_at']
            }
        return None


def save_chat_message(anomaly_id: int, role: str, content: str) -> int:
    """Save a chat message linked to an anomaly"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO anomaly_chats (anomaly_id, role, content)
            VALUES (?, ?, ?)
        ''', (anomaly_id, role, content))
        conn.commit()
        msg_id = cursor.lastrowid
        logger.debug(f"Saved chat message {msg_id} for anomaly {anomaly_id}")
        return msg_id


def get_chat_history(anomaly_id: int) -> List[Dict[str, Any]]:
    """Get chat history for a specific anomaly"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, role, content, created_at
            FROM anomaly_chats
            WHERE anomaly_id = ?
            ORDER BY created_at ASC
        ''', (anomaly_id,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'id': row['id'],
                'role': row['role'],
                'content': row['content'],
                'created_at': row['created_at']
            })
        return messages


def clear_all_data():
    """Clear all data from database (for testing/reset)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM anomaly_chats')
        cursor.execute('DELETE FROM anomaly_events')
        conn.commit()
        logger.warning("All anomaly data cleared from database")
