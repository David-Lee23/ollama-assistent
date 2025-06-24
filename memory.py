# memory.py

import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional

DATABASE_PATH = "agent_memory.db"

def log_message(role: str, content: str) -> None:
    """Log a message to the conversation history database.
    
    Args:
        role: The role of the message sender ('user' or 'assistant')
        content: The content of the message
    """
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute(
            "INSERT INTO messages (role, content) VALUES (?, ?)", 
            (role, content)
        )

def get_recent_history(limit: int = 10) -> List[Tuple[str, str]]:
    """Get recent conversation history from the database.
    
    Args:
        limit: Maximum number of messages to retrieve
        
    Returns:
        List of tuples containing (role, content) in chronological order
    """
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.execute(
            "SELECT role, content FROM messages ORDER BY timestamp DESC LIMIT ?", 
            (limit,)
        )
        # Reverse the list to get chronological order (oldest first)
        return list(reversed(cursor.fetchall()))

def get_conversation_messages(limit: int = 10) -> List[dict]:
    """Get recent conversation history formatted for the chat model.
    
    Args:
        limit: Maximum number of messages to retrieve
        
    Returns:
        List of message dictionaries with 'role' and 'content' keys
    """
    recent_history = get_recent_history(limit)
    return [{"role": role, "content": content} for role, content in recent_history]

def clear_history() -> None:
    """Clear all conversation history from the database."""
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute("DELETE FROM messages")

def get_message_count() -> int:
    """Get the total number of messages in the database.
    
    Returns:
        Total number of messages stored
    """
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM messages")
        return cursor.fetchone()[0]

def search_memory(term: str, limit: int = 5) -> List[Tuple[str, str, str]]:
    """Search memory for user or assistant messages containing a keyword.
    
    Args:
        term: The search term to look for in message content
        limit: Maximum number of results to return
        
    Returns:
        List of tuples containing (role, content, timestamp) for matching messages
    """
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.execute(
            "SELECT role, content, timestamp FROM messages WHERE content LIKE ? ORDER BY timestamp DESC LIMIT ?",
            (f"%{term}%", limit)
        )
        return cursor.fetchall()

def search_memory_by_role(term: str, role: str = None, limit: int = 5) -> List[Tuple[str, str, str]]:
    """Search memory for messages containing a keyword, optionally filtered by role.
    
    Args:
        term: The search term to look for in message content
        role: Optional role filter ('user' or 'assistant')
        limit: Maximum number of results to return
        
    Returns:
        List of tuples containing (role, content, timestamp) for matching messages
    """
    with sqlite3.connect(DATABASE_PATH) as conn:
        if role:
            cursor = conn.execute(
                "SELECT role, content, timestamp FROM messages WHERE content LIKE ? AND role = ? ORDER BY timestamp DESC LIMIT ?",
                (f"%{term}%", role, limit)
            )
        else:
            cursor = conn.execute(
                "SELECT role, content, timestamp FROM messages WHERE content LIKE ? ORDER BY timestamp DESC LIMIT ?",
                (f"%{term}%", limit)
            )
        return cursor.fetchall()

def get_conversation_summary(days: int = 7) -> Optional[str]:
    """Get a summary of conversations from the last N days.
    
    Args:
        days: Number of days to look back
        
    Returns:
        Summary string or None if no conversations found
    """
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.execute(
            """SELECT role, content FROM messages 
               WHERE timestamp >= datetime('now', '-{} days')
               ORDER BY timestamp""".format(days)
        )
        messages = cursor.fetchall()
        
    if not messages:
        return None
        
    total_messages = len(messages)
    user_messages = len([m for m in messages if m[0] == 'user'])
    
    return f"Last {days} days: {total_messages} messages ({user_messages} from user)" 