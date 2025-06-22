from ollama import chat

response = chat(
    model='llama3:8b-instruct-q4_K_M',
    messages=[
        {"role": "user", "content": "What homework is due today?"}
    ]
)

print(response['message']['content'])

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
