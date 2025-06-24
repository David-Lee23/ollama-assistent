# main_agent.py

import time
from chat_tools import run_chat_message
from utils import get_user_input, notify_user
from memory import get_message_count, clear_history, get_conversation_summary

def main():
    # Show memory status on startup
    message_count = get_message_count()
    print("📚 Student Assistant Agent is running. Type your question or Ctrl+C to stop.")
    print("💡 Press Enter without typing anything to check for updates, or type 'quit' to exit.")
    print("🧠 The assistant automatically searches memory when context is needed!")
    print("🔍 Or try: 'What did I say about...' or 'Did I mention...' for manual search")
    
    if message_count > 0:
        print(f"🧠 Memory: {message_count} messages stored")
        summary = get_conversation_summary()
        if summary:
            print(f"📊 {summary}")
    else:
        print("🧠 Memory: Starting fresh (no previous conversations)")
    
    print()  # Add blank line for readability
    
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
            
            # Handle memory commands
            if user_input.lower() == 'clear memory':
                clear_history()
                print("🧠 Memory cleared! Starting fresh.")
                continue
            
            if user_input.lower() in ['memory status', 'memory']:
                count = get_message_count()
                summary = get_conversation_summary()
                print(f"🧠 Memory Status: {count} messages stored")
                if summary:
                    print(f"📊 {summary}")
                else:
                    print("📊 No recent conversations found")
                continue
            
            if user_input.lower() == 'help':
                print("🔧 Available Commands:")
                print("  • memory / memory status - View memory statistics")
                print("  • clear memory - Reset conversation history")
                print("  • help - Show this help message")
                print("  • quit / exit / bye - Stop the agent")
                print()
                print("🧠 Memory Features:")
                print("  • Autonomous: Assistant automatically searches memory when needed")
                print("  • Manual: 'What did I say about...' or 'Did I mention...'")
                print("  • Direct: 'search: <term>' for specific searches")
                continue
                
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
