# main_agent.py

import time
from chat_tools import run_chat_message
from utils import get_user_input, notify_user

def main():
    print("📚 Student Assistant Agent is running. Type your question or Ctrl+C to stop.")
    
    while True:
        try:
            user_input = get_user_input(timeout=30)
            if user_input:
                response = run_chat_message(user_input)
                notify_user(response)

        except KeyboardInterrupt:
            print("🛑 Agent stopped manually.")
            break
        except Exception as e:
            print(f"⚠️ Agent error: {e}")

        time.sleep(1)

if __name__ == "__main__":
    main()
