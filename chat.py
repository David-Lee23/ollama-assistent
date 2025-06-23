from ollama import chat
from canvas_tools import get_assignments, get_announcements, get_calendar_events, get_courses
import json

# Define specialized tool schemas for Ollama
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_assignments",
            "description": "Get Canvas assignments and homework. Can filter by due date and status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "due_date": {
                        "type": "string",
                        "description": "Filter by due date: 'today', 'tomorrow', 'this_week', or specific date (YYYY-MM-DD)"
                    },
                    "status": {
                        "type": "string", 
                        "description": "Filter by status: 'overdue' or 'upcoming'"
                    }
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
                    "unread_only": {
                        "type": "boolean",
                        "description": "Only return unread announcements (default: false)"
                    },
                    "course_id": {
                        "type": "string",
                        "description": "Get announcements for specific course ID"
                    }
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
                    "start_date": {
                        "type": "string",
                        "description": "Start date for events: 'today', 'tomorrow', or specific date (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date for events (YYYY-MM-DD)"
                    }
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

# Test message
messages = [
    {
        "role": "system",
        "content": "You are an AI assistant with access to Canvas LMS tools. When users ask about assignments, homework, announcements, calendar events, or courses, use the appropriate Canvas tools to get real data. Be helpful and conversational in your responses."
    },
    {
        "role": "user",
        "content": "What homework is due today?"
    }
]

# Call the LLM with tools
response = chat(
    model="qwen3:8b",
    messages=messages,
    tools=TOOLS
)

tool_calls = response.message.tool_calls if hasattr(response.message, 'tool_calls') else None
print("TOOL CALLS RAW:", tool_calls)  # Debug print
print(json.dumps(response.model_dump(), indent=2))

if tool_calls:
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        # Handle both dict and string arguments
        tool_args = tool_call.function.arguments if isinstance(tool_call.function.arguments, dict) else json.loads(tool_call.function.arguments)

        print(f"\n🔧 Calling tool: {tool_name}")
        print(f"🔧 Tool args: {tool_args}")

        # Call the appropriate specialized function
        try:
            if tool_name == "get_assignments":
                result = get_assignments(
                    due_date=tool_args.get("due_date"),
                    status=tool_args.get("status")
                )
            elif tool_name == "get_announcements":
                result = get_announcements(
                    unread_only=tool_args.get("unread_only", False),
                    course_id=tool_args.get("course_id")
                )
            elif tool_name == "get_calendar_events":
                result = get_calendar_events(
                    start_date=tool_args.get("start_date"),
                    end_date=tool_args.get("end_date")
                )
            elif tool_name == "get_courses":
                result = get_courses()
            else:
                result = f"Unknown tool: {tool_name}"

            print(f"🔧 Tool result: {result}")

            # Inject tool output into the message stream
            messages.append({"role": "assistant", "tool_calls": tool_calls})
            messages.append({"role": "tool", "name": tool_name, "content": str(result)})

        except Exception as e:
            print(f"🚫 Error calling tool {tool_name}: {e}")
            messages.append({"role": "assistant", "tool_calls": tool_calls})
            messages.append({"role": "tool", "name": tool_name, "content": f"Error: {e}"})

    print("🔧 Calling LLM for final response...")
    # Final LLM response with the tool output
    follow_up = chat(
        model="qwen3:8b",
        messages=messages
    )

    print("\n🤖:", follow_up["message"]["content"])
else:
    print("🤖:", response['message']['content'])
