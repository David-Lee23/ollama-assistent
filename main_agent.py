# main_agent.py

import time
from chat_tools import run_chat_message
from utils import get_user_input, notify_user

def main():
    print("📚 Student Assistant Agent is running. Type your question or Ctrl+C to stop.")
    print("💡 Press Enter without typing anything to check for updates, or type 'quit' to exit.")
    
    while True:
        try:
            user_input = get_user_input(timeout=60)  # Longer timeout, less frequent prompts
            
            if user_input is None:
                # Timeout occurred - could add proactive checks here
                print("⏰ Checking for updates...")
                time.sleep(2)  # Brief pause before next prompt
                continue
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
                
            if user_input:  # Non-empty input
                response = run_chat_message(user_input)
                notify_user(response)
            
            # Small delay before next iteration
            time.sleep(0.5)

        except KeyboardInterrupt:
            print("\n🛑 Agent stopped manually.")
            break
        except Exception as e:
            print(f"⚠️ Agent error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
