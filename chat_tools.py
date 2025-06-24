# chat_tools.py

from ollama import chat
from canvas_tools import get_assignments, get_announcements, get_calendar_events, get_courses
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
    today_str = datetime.now().strftime("%B %d, %Y")

    messages = [
        {
            "role": "system",
            "content": (
                f"You are an AI assistant with access to Canvas LMS tools. "
                f"The current date is {today_str}. "
                "When users ask about assignments, homework, announcements, calendar events, or courses, "
                "use the appropriate tools to get real data. Be helpful and conversational in your responses."
            )
        },
        {
            "role": "user",
            "content": message
        }
    ]


    response = chat(model="mistral", messages=messages, tools=TOOLS)
    tool_calls = getattr(response.message, "tool_calls", None)

    if not tool_calls:
        return response.message.content

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

    follow_up = chat(model="mistral", messages=messages)
    return follow_up.message.content
