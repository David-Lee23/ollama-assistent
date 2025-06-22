from ollama import chat

messages = [
  {"role": "user", "content": "Explain the difference between a process and a thread."}
]

response = chat(
  model='llama3:8b-instruct',
  messages=messages
)

print(response['message']['content'])
