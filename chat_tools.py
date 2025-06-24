# chat_tools.py

from ollama import chat
from canvas_tools import get_assignments, get_announcements, get_calendar_events, get_courses
from memory import log_message, get_conversation_messages
import json
from datetime import datetime

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
    }
]


def run_chat_message(message: str) -> str:
    # Log the user message first
    log_message("user", message)
    
    today_str = datetime.now().strftime("%B %d, %Y")

    # Get recent conversation history (last 8 messages to keep context manageable)
    recent_history = get_conversation_messages(limit=8)
    
    # Build messages array starting with system prompt
    messages = [
        {
            "role": "system",
            "content": (
                f"You are an AI assistant with access to Canvas LMS tools. "
                f"The current date is {today_str}. "
                "When users ask about assignments, homework, announcements, calendar events, or courses, "
                "use the appropriate tools to get real data. Be helpful and conversational in your responses. "
                "You have access to conversation history to maintain context across interactions."
            )
        }
    ]
    
    # Add recent conversation history
    messages.extend(recent_history)
    
    # Add the current user message (it's already in history, but we need it for the current context)
    messages.append({
        "role": "user",
        "content": message
    })

    response = chat(model="qwen3:4b", messages=messages, tools=TOOLS)
    tool_calls = getattr(response.message, "tool_calls", None)

    if not tool_calls:
        # Log assistant response and return
        assistant_response = response.message.content
        log_message("assistant", assistant_response)
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
        else:
            result = f"Unknown tool: {tool_name}"

        results.append({"role": "tool", "name": tool_name, "content": str(result)})

    messages.append({"role": "assistant", "tool_calls": tool_calls})
    messages.extend(results)

    follow_up = chat(model="qwen3:4b", messages=messages)
    
    # Log the final assistant response
    assistant_response = follow_up.message.content
    log_message("assistant", assistant_response)
    
    return assistant_response
