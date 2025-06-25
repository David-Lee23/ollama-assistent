# chat_tools.py

from ollama import chat
from canvas_tools import get_assignments, get_announcements, get_calendar_events, get_courses
from memory import (
    log_message, get_conversation_messages, search_memory, get_project,
    get_project_summary, generate_project_summary, should_update_summary
)
import json
from datetime import datetime
from typing import Optional

TOOLS = [  # same tool schema from chat.py
    {
        "type": "function",
        "function": {
            "name": "get_assignments",
            "description": "Get Canvas assignments and homework. Can filter by due date and status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "due_date": {"type": "string"},
                    "status": {"type": "string"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_announcements",
            "description": "Get Canvas announcements and news from courses.",
            "parameters": {
                "type": "object",
                "properties": {
                    "unread_only": {"type": "boolean"},
                    "course_id": {"type": "string"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_calendar_events",
            "description": "Get Canvas calendar events and scheduled activities.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_courses",
            "description": "Get list of current active Canvas courses.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_memory",
            "description": "Search through past conversation history for relevant information. Use this when the user refers to previous discussions, asks about past topics, or when context from earlier conversations would be helpful to answer their question.",
            "parameters": {
                "type": "object",
                "properties": {
                    "term": {
                        "type": "string",
                        "description": "The search term or keyword to look for in past conversations. Use relevant keywords from the user's query."
                    }
                },
                "required": ["term"]
            }
        }
    }
]

def detect_memory_query(message: str) -> Optional[str]:
    """Simple rule-based NLP to detect memory search intent.
    
    Args:
        message: The user's input message
        
    Returns:
        Search term if memory query detected, None otherwise
    """
    memory_keywords = [
        "did i mention", "what did i say", "have i talked about", 
        "remind me about", "memory of", "search memory for",
        "do you remember", "what did we discuss", "have we talked about",
        "did we discuss", "recall", "remember when", "what was that about",
        "find in memory", "look up", "search for"
    ]
    
    message_lower = message.lower()
    
    # Check for direct memory search commands first
    if message_lower.startswith("search:") or message_lower.startswith("find:"):
        return message[message.find(":")+1:].strip()
    
    for phrase in memory_keywords:
        if phrase in message_lower:
            # Different extraction strategies based on the phrase
            if phrase in ["what did i say", "did i mention", "have i talked about", "did we discuss", "what did we discuss"]:
                # Look for "about X" pattern
                about_pos = message_lower.find("about")
                if about_pos > -1:
                    search_term = message[about_pos + 5:].strip(" ?\"'.,!").strip()
                    # Remove "about" if it got included
                    if search_term.lower().startswith("about "):
                        search_term = search_term[6:]
                else:
                    # Extract everything after the phrase
                    parts = message_lower.split(phrase)
                    if len(parts) > 1:
                        search_term = parts[-1].strip(" ?\"'.,!").strip()
                    else:
                        continue
            elif phrase in ["remind me about", "memory of", "search memory for", "search for"]:
                # Extract term after these phrases
                parts = message_lower.split(phrase)
                if len(parts) > 1:
                    search_term = parts[-1].strip(" ?\"'.,!").strip()
                else:
                    continue
            else:
                # Generic extraction
                parts = message_lower.split(phrase)
                if len(parts) > 1:
                    search_term = parts[-1].strip(" ?\"'.,!").strip()
                else:
                    continue
            
            # Clean up the search term
            if search_term:
                # Remove common stop words that don't help search
                stop_words = ["the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "anything", "something"]
                search_words = [word for word in search_term.split() if word not in stop_words and len(word) > 1]
                if search_words:
                    return " ".join(search_words)
    
    return None

def format_memory_results(results: list, search_term: str) -> str:
    """Format memory search results for display.
    
    Args:
        results: List of tuples (role, content, timestamp)
        search_term: The original search term
        
    Returns:
        Formatted string with search results
    """
    if not results:
        return f"🔍 I didn't find anything in memory about '{search_term}'."
    
    formatted_results = [f"🔍 Found {len(results)} result(s) for '{search_term}':\n"]
    
    for i, (role, content, timestamp) in enumerate(results, 1):
        # Format timestamp nicely
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime("%b %d, %Y at %I:%M %p")
        except:
            time_str = timestamp
        
        # Truncate long messages
        if len(content) > 150:
            content = content[:147] + "..."
        
        role_icon = "👤" if role == "user" else "🤖"
        formatted_results.append(f"{i}. {time_str} — {role_icon} {role}: {content}")
    
    return "\n".join(formatted_results)

def format_memory_results_for_llm(results: list) -> str:
    """Format memory search results for LLM consumption.
    
    Args:
        results: List of tuples (role, content, timestamp)
        
    Returns:
        Formatted string optimized for LLM context
    """
    if not results:
        return "No relevant information found in conversation history."
    
    formatted_results = ["Relevant conversation history:"]
    
    for role, content, timestamp in results:
        # Format timestamp
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime("%b %d, %Y")
        except:
            time_str = timestamp
        
        formatted_results.append(f"[{time_str}] {role.title()}: {content}")
    
    return "\n".join(formatted_results)

def run_chat_message(message: str, project_id: int = None) -> str:
    # Log the user message first
    log_message("user", message, project_id)
    
    # Check if we should generate/update project summary (periodic summarization)
    if project_id and should_update_summary(project_id):
        print("🧠 Updating project summary...")
        generate_project_summary(project_id)
    
    # Check if this is a manual memory search query first (fallback behavior)
    manual_search_term = detect_memory_query(message)
    if manual_search_term:
        results = search_memory(manual_search_term, project_id=project_id)
        reply = format_memory_results(results, manual_search_term)
        log_message("assistant", reply, project_id)
        return reply
    
    today_str = datetime.now().strftime("%B %d, %Y")

    # Get recent conversation history (last 6 messages to leave room for memory search results)
    recent_history = get_conversation_messages(limit=6, project_id=project_id)
    
    # Get project-specific system prompt
    project_system_prompt = "You are an AI assistant with access to Canvas LMS tools and conversation memory."
    if project_id:
        project = get_project(project_id)
        if project and project.get('system_prompt'):
            project_system_prompt = project['system_prompt']
    
    # Build messages array starting with enhanced system prompt
    messages = [
        {
            "role": "system",
            "content": (
                f"{project_system_prompt} "
                f"The current date is {today_str}. "
                "When users ask about assignments, homework, announcements, calendar events, or courses, "
                "use the appropriate Canvas tools to get real data. "
                "When users refer to past conversations, ask about previous topics they mentioned, "
                "or when context from earlier discussions would help answer their question, "
                "use the search_memory tool to find relevant information from conversation history. "
                "Be helpful and conversational in your responses, and use memory search proactively "
                "when it would provide valuable context for your answer."
            )
        }
    ]
    
    # Inject project summary if available (context injection)
    if project_id:
        summary = get_project_summary(project_id)
        if summary:
            messages.append({
                "role": "system",
                "content": f"🧠 Project Summary: {summary}"
            })
    
    # Add recent conversation history
    messages.extend(recent_history)
    
    # Add the current user message
    messages.append({
        "role": "user",
        "content": message
    })

    response = chat(model="qwen3:4b", messages=messages, tools=TOOLS)
    tool_calls = getattr(response.message, "tool_calls", None)

    if not tool_calls:
        # Log assistant response and return
        assistant_response = response.message.content
        log_message("assistant", assistant_response, project_id)
        return assistant_response

    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        tool_args = tool_call.function.arguments
        if isinstance(tool_args, str):
            tool_args = json.loads(tool_args)

        if tool_name == "get_assignments":
            result = get_assignments(**tool_args)
        elif tool_name == "get_announcements":
            result = get_announcements(**tool_args)
        elif tool_name == "get_calendar_events":
            result = get_calendar_events(**tool_args)
        elif tool_name == "get_courses":
            result = get_courses()
        elif tool_name == "search_memory":
            # Handle autonomous memory search (project-scoped)
            search_term = tool_args.get("term", "")
            memory_results = search_memory(search_term, limit=5, project_id=project_id)
            result = format_memory_results_for_llm(memory_results)
        else:
            result = f"Unknown tool: {tool_name}"

        results.append({"role": "tool", "name": tool_name, "content": str(result)})

    messages.append({"role": "assistant", "tool_calls": tool_calls})
    messages.extend(results)

    follow_up = chat(model="qwen3:4b", messages=messages)
    
    # Log the final assistant response
    assistant_response = follow_up.message.content
    log_message("assistant", assistant_response, project_id)
    
    return assistant_response
