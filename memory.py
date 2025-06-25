# memory.py

import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional, Dict

DATABASE_PATH = "agent_memory.db"

def init_database():
    """Initialize the database with required tables."""
    with sqlite3.connect(DATABASE_PATH) as conn:
        # Create projects table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                system_prompt TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add project_id column to messages table if it doesn't exist
        try:
            conn.execute("ALTER TABLE messages ADD COLUMN project_id INTEGER REFERENCES projects(id)")
        except sqlite3.OperationalError:
            # Column already exists
            pass
        
        # Create default project if none exists
        cursor = conn.execute("SELECT COUNT(*) FROM projects")
        if cursor.fetchone()[0] == 0:
            conn.execute("""
                INSERT INTO projects (name, description, system_prompt) 
                VALUES (?, ?, ?)
            """, (
                "General Chat", 
                "Default project for general conversations",
                "You are an AI assistant with access to Canvas LMS tools and conversation memory. Be helpful and conversational in your responses."
            ))

def create_project(name: str, description: str = "", system_prompt: str = "") -> int:
    """Create a new project.
    
    Args:
        name: Project name (must be unique)
        description: Project description
        system_prompt: Custom system prompt for this project
        
    Returns:
        Project ID of the created project
        
    Raises:
        sqlite3.IntegrityError: If project name already exists
    """
    if not system_prompt:
        system_prompt = f"You are an AI assistant working on the '{name}' project. {description}"
    
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.execute("""
            INSERT INTO projects (name, description, system_prompt, updated_at) 
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (name, description, system_prompt))
        return cursor.lastrowid

def get_projects() -> List[Dict]:
    """Get all projects.
    
    Returns:
        List of project dictionaries
    """
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("""
            SELECT p.*, COUNT(m.id) as message_count 
            FROM projects p 
            LEFT JOIN messages m ON p.id = m.project_id 
            GROUP BY p.id 
            ORDER BY p.updated_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

def get_project(project_id: int) -> Optional[Dict]:
    """Get a specific project by ID.
    
    Args:
        project_id: Project ID
        
    Returns:
        Project dictionary or None if not found
    """
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_project(project_id: int, name: str = None, description: str = None, system_prompt: str = None, summary: str = None) -> bool:
    """Update a project.
    
    Args:
        project_id: Project ID
        name: New name (optional)
        description: New description (optional)
        system_prompt: New system prompt (optional)
        summary: New summary (optional)
        
    Returns:
        True if project was updated, False if not found
    """
    updates = []
    params = []
    
    if name is not None:
        updates.append("name = ?")
        params.append(name)
    if description is not None:
        updates.append("description = ?")
        params.append(description)
    if system_prompt is not None:
        updates.append("system_prompt = ?")
        params.append(system_prompt)
    if summary is not None:
        updates.append("summary = ?")
        params.append(summary)
    
    if not updates:
        return False
    
    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.append(project_id)
    
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.execute(f"""
            UPDATE projects SET {', '.join(updates)} WHERE id = ?
        """, params)
        return cursor.rowcount > 0

def delete_project(project_id: int) -> bool:
    """Delete a project and all its messages.
    
    Args:
        project_id: Project ID
        
    Returns:
        True if project was deleted, False if not found
    """
    with sqlite3.connect(DATABASE_PATH) as conn:
        # Delete messages first (foreign key constraint)
        conn.execute("DELETE FROM messages WHERE project_id = ?", (project_id,))
        # Delete project
        cursor = conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        return cursor.rowcount > 0

def log_message(role: str, content: str, project_id: int = None) -> None:
    """Log a message to the conversation history database.
    
    Args:
        role: The role of the message sender ('user' or 'assistant')
        content: The content of the message
        project_id: Project ID (uses default project if None)
    """
    if project_id is None:
        # Get default project ID (first project, usually "General Chat")
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.execute("SELECT id FROM projects ORDER BY id LIMIT 1")
            result = cursor.fetchone()
            project_id = result[0] if result else 1
    
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute(
            "INSERT INTO messages (role, content, project_id) VALUES (?, ?, ?)", 
            (role, content, project_id)
        )

def get_recent_history(limit: int = 10, project_id: int = None) -> List[Tuple[str, str]]:
    """Get recent conversation history from the database.
    
    Args:
        limit: Maximum number of messages to retrieve
        project_id: Project ID to filter by (all projects if None)
        
    Returns:
        List of tuples containing (role, content) in chronological order
    """
    with sqlite3.connect(DATABASE_PATH) as conn:
        if project_id is not None:
            cursor = conn.execute(
                "SELECT role, content FROM messages WHERE project_id = ? ORDER BY timestamp DESC LIMIT ?", 
                (project_id, limit)
            )
        else:
            cursor = conn.execute(
                "SELECT role, content FROM messages ORDER BY timestamp DESC LIMIT ?", 
                (limit,)
            )
        # Reverse the list to get chronological order (oldest first)
        return list(reversed(cursor.fetchall()))

def get_conversation_messages(limit: int = 10, project_id: int = None) -> List[dict]:
    """Get recent conversation history formatted for the chat model.
    
    Args:
        limit: Maximum number of messages to retrieve
        project_id: Project ID to filter by (all projects if None)
        
    Returns:
        List of message dictionaries with 'role' and 'content' keys
    """
    recent_history = get_recent_history(limit, project_id)
    return [{"role": role, "content": content} for role, content in recent_history]

def clear_history(project_id: int = None) -> None:
    """Clear conversation history from the database.
    
    Args:
        project_id: Project ID to clear (all projects if None)
    """
    with sqlite3.connect(DATABASE_PATH) as conn:
        if project_id is not None:
            conn.execute("DELETE FROM messages WHERE project_id = ?", (project_id,))
        else:
            conn.execute("DELETE FROM messages")

def get_message_count(project_id: int = None) -> int:
    """Get the total number of messages in the database.
    
    Args:
        project_id: Project ID to filter by (all projects if None)
        
    Returns:
        Total number of messages stored
    """
    with sqlite3.connect(DATABASE_PATH) as conn:
        if project_id is not None:
            cursor = conn.execute("SELECT COUNT(*) FROM messages WHERE project_id = ?", (project_id,))
        else:
            cursor = conn.execute("SELECT COUNT(*) FROM messages")
        return cursor.fetchone()[0]

def search_memory(term: str, limit: int = 5, project_id: int = None) -> List[Tuple[str, str, str]]:
    """Search memory for user or assistant messages containing a keyword.
    
    Args:
        term: The search term to look for in message content
        limit: Maximum number of results to return
        project_id: Project ID to filter by (all projects if None)
        
    Returns:
        List of tuples containing (role, content, timestamp) for matching messages
    """
    with sqlite3.connect(DATABASE_PATH) as conn:
        if project_id is not None:
            cursor = conn.execute(
                "SELECT role, content, timestamp FROM messages WHERE content LIKE ? AND project_id = ? ORDER BY timestamp DESC LIMIT ?",
                (f"%{term}%", project_id, limit)
            )
        else:
            cursor = conn.execute(
                "SELECT role, content, timestamp FROM messages WHERE content LIKE ? ORDER BY timestamp DESC LIMIT ?",
                (f"%{term}%", limit)
            )
        return cursor.fetchall()

def search_memory_by_role(term: str, role: str = None, limit: int = 5, project_id: int = None) -> List[Tuple[str, str, str]]:
    """Search memory for messages containing a keyword, optionally filtered by role.
    
    Args:
        term: The search term to look for in message content
        role: Optional role filter ('user' or 'assistant')
        limit: Maximum number of results to return
        project_id: Project ID to filter by (all projects if None)
        
    Returns:
        List of tuples containing (role, content, timestamp) for matching messages
    """
    with sqlite3.connect(DATABASE_PATH) as conn:
        if project_id is not None:
            if role:
                cursor = conn.execute(
                    "SELECT role, content, timestamp FROM messages WHERE content LIKE ? AND role = ? AND project_id = ? ORDER BY timestamp DESC LIMIT ?",
                    (f"%{term}%", role, project_id, limit)
                )
            else:
                cursor = conn.execute(
                    "SELECT role, content, timestamp FROM messages WHERE content LIKE ? AND project_id = ? ORDER BY timestamp DESC LIMIT ?",
                    (f"%{term}%", project_id, limit)
                )
        else:
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

def get_conversation_summary(days: int = 7, project_id: int = None) -> Optional[str]:
    """Get a summary of conversations from the last N days.
    
    Args:
        days: Number of days to look back
        project_id: Project ID to filter by (all projects if None)
        
    Returns:
        Summary string or None if no conversations found
    """
    with sqlite3.connect(DATABASE_PATH) as conn:
        if project_id is not None:
            cursor = conn.execute(
                """SELECT role, content FROM messages 
                   WHERE timestamp >= datetime('now', '-{} days') AND project_id = ?
                   ORDER BY timestamp""".format(days),
                (project_id,)
            )
        else:
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

def update_project_summary(project_id: int, summary: str) -> bool:
    """Update the summary for a specific project.
    
    Args:
        project_id: Project ID
        summary: The new summary text
        
    Returns:
        True if project summary was updated, False if project not found
    """
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.execute(
            "UPDATE projects SET summary = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (summary, project_id)
        )
        return cursor.rowcount > 0

def get_project_summary(project_id: int) -> Optional[str]:
    """Get the summary for a specific project.
    
    Args:
        project_id: Project ID
        
    Returns:
        Project summary or None if not found or no summary exists
    """
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.execute("SELECT summary FROM projects WHERE id = ?", (project_id,))
        result = cursor.fetchone()
        return result[0] if result and result[0] else None

def generate_project_summary(project_id: int, limit: int = 50) -> Optional[str]:
    """Generate a new summary for a project using recent conversation history.
    
    Args:
        project_id: Project ID
        limit: Number of recent messages to include in summarization
        
    Returns:
        Generated summary or None if no messages found or generation failed
    """
    # Import here to avoid circular dependency
    from ollama import chat
    
    # Get recent conversation messages for this project
    messages = get_conversation_messages(limit=limit, project_id=project_id)
    
    if not messages:
        return None
    
    # Get project info for context
    project = get_project(project_id)
    project_name = project.get('name', 'Unknown Project') if project else 'Unknown Project'
    
    # Build summarization prompt
    summary_prompt = [
        {
            "role": "system", 
            "content": f"You are summarizing the conversation history for the project '{project_name}'. "
                      "Create a concise 3-5 bullet point summary that captures:\n"
                      "• Key topics and themes discussed\n"
                      "• Important decisions or conclusions reached\n"
                      "• Current project status or progress\n"
                      "• Any ongoing tasks or next steps\n"
                      "Keep it brief but informative. Use bullet points starting with '•'."
        }
    ]
    
    # Add the conversation history
    summary_prompt.extend(messages)
    
    try:
        # Generate summary using the LLM
        response = chat(model="qwen3:4b", messages=summary_prompt)
        summary = response.message.content.strip()
        
        # Store the generated summary
        if summary and update_project_summary(project_id, summary):
            return summary
        
    except Exception as e:
        print(f"⚠️ Failed to generate project summary: {e}")
    
    return None

def should_update_summary(project_id: int, message_threshold: int = 25) -> bool:
    """Check if a project summary should be updated based on recent activity.
    
    Args:
        project_id: Project ID
        message_threshold: Number of new messages since last update to trigger summary refresh
        
    Returns:
        True if summary should be updated
    """
    # Get project info including when it was last updated
    project = get_project(project_id)
    if not project:
        return False
    
    # Get message count for this project
    message_count = get_message_count(project_id)
    
    # If no messages, no need for summary
    if message_count == 0:
        return False
    
    # If no existing summary, definitely create one (but only if we have enough messages)
    if not project.get('summary'):
        return message_count >= 10  # Wait until we have at least 10 messages
    
    # Check if enough new messages have been added since last update
    # This is a simple heuristic - in a more advanced system you could track 
    # message counts at the time of last summary update
    return message_count >= message_threshold

# Initialize database on import
init_database() 