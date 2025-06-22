from ollama import chat
from canvas_tools import get_canvas_info
import json

# Define tool schema for Ollama
TOOLS = [
    {
        "type": "function",
        "function": {
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
    model="qwen3:8b",
    messages=messages,
    tools=TOOLS
)

tool_calls = response.message.tool_calls if hasattr(response.message, 'tool_calls') else None
print("TOOL CALLS RAW:", tool_calls)  # Debug print
print(json.dumps(response.model_dump(), indent=2))

if tool_calls:
    tool_call = tool_calls[0]
    tool_name = tool_call.function.name
    # Handle both dict and string arguments
    tool_args = tool_call.function.arguments if isinstance(tool_call.function.arguments, dict) else json.loads(tool_call.function.arguments)

    if tool_name == "get_canvas_info":
        result = get_canvas_info(
            resource=tool_args.get("resource"),
            filter=tool_args.get("filter"),
            date=tool_args.get("date")
        )

        # Inject tool output into the message stream
        messages.append({"role": "assistant", "tool_calls": tool_calls})
        messages.append({"role": "tool", "name": tool_name, "content": str(result)})

        # Final LLM response with the tool output
        follow_up = chat(
            model="qwen3:8b",
            messages=messages
        )

        print("\n🤖:", follow_up["message"]["content"])
    else:
        print("🚫 Tool was requested, but not implemented:", tool_name)
else:
    print("🤖:", response['message']['content'])
