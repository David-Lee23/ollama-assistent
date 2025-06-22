from ollama import chat
from canvas_tools import get_canvas_info

# Tool schema definition
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

# Start the conversation
messages = [
    {"role": "system", "content": "You are a helpful assistant with access to tools such as get_canvas_info for checking Canvas LMS data like assignments and due dates."},
    {"role": "user", "content": "What homework is due today?"}
]


# First chat to determine if the LLM wants to call a tool
response = chat(
    model="llama3:8b-instruct-q4_K_M",
    messages=messages,
    options={
        "tools": TOOLS,
        "tool_choice": "auto",
        "format": "json"
    }
)

tool_call = response.get("message", {}).get("tool_calls")

if tool_call:
    # Extract tool name and arguments
    tool_name = tool_call[0]["name"]
    tool_args = tool_call[0].get("args", {})

    if tool_name == "get_canvas_info":
        # Call the real function with parsed args
        tool_output = get_canvas_info(
            resource=tool_args.get("resource"),
            filter=tool_args.get("filter"),
            date=tool_args.get("date")
        )

        # Append to message history and continue conversation
        messages.append({"role": "assistant", "tool_calls": tool_call})
        messages.append({"role": "tool", "name": tool_name, "content": str(tool_output)})

        follow_up = chat(
            model="llama3:8b-instruct-q4_K_M",
            messages=messages
        )

        print("\n🤖:", follow_up["message"]["content"])
    else:
        print("🚫 Unsupported tool requested:", tool_name)
else:
    # No tool needed, just print the response
    print("\n🤖:", response["message"]["content"])
