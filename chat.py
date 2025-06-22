from ollama import chat

response = chat(
    model='llama3:8b-instruct-q4_K_M',
    messages=[
        {"role": "user", "content": "What is the difference between a process and a thread?"}
    ]
)

print(response['message']['content'])

