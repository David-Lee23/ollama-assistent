from ollama import chat
from canvas_tools import get_canvas_info
import json

# Define tool schema
TOOLS = [
    {
        "name": "get_canvas_info",
        "description": "Get Canvas data such as assignments, announcements, or calendar events.",
        "parameters": {
            "type": "object",
            "properties": {
                "resource": {
                    "type": "string",
                    "description": "What kind of Canvas data to fetch (assignments, announcements, calendar)"
                },
                "filter": {
                    "type": "string",
                    "description": "Optional filter like 'unread' or 'overdue'"
                },
                "date": {
                    "type": "string",
                    "description": "Optional date or timeframe like 'today', '2024-06-24', or 'next_week'"
                }
            },
            "required": ["resource"]
        }
    }
]

# Test message with stronger prompt
messages = [
    {
        "role": "system",
        "content": "You are an AI assistant with access to the tool `get_canvas_info`, which retrieves live assignment and schedule data from Canvas LMS. If the user asks about anything Canvas-related, you must call this tool using JSON format."
    },
    {
        "role": "user",
        "content": "What homework is due today?"
    }
]


# Force the tool call for testing
response = chat(
    model = "deepseek-coder:6.7b-instruct-q4_K_M",
    messages=messages,
    options={
        "tools": TOOLS,
        "tool_choice": {"type": "required", "name": "get_canvas_info"},  # Force the tool
        "format": "json"
    }
)

tool_call = response.get("message", {}).get("tool_calls")
print("TOOL CALL RAW:", tool_call)  # Debug print
print(json.dumps(response.model_dump(), indent=2))

if tool_call:
    tool_name = tool_call[0]["name"]
    tool_args = tool_call[0].get("args", {})

    if tool_name == "get_canvas_info":
        result = get_canvas_info(
            resource=tool_args.get("resource"),
            filter=tool_args.get("filter"),
            date=tool_args.get("date")
        )

        # Inject tool output into the message stream
        messages.append({"role": "assistant", "tool_calls": tool_call})
        messages.append({"role": "tool", "name": tool_name, "content": str(result)})

        # Final LLM response with the tool output
        follow_up = chat(
            model="llama3:8b-instruct-q4_K_M",
            messages=messages
        )

        print("\n🤖:", follow_up["message"]["content"])
    else:
        print("🚫 Tool was requested, but not implemented:", tool_name)
else:
    print("🤖:", response['message']['content'])
