# main_agent.py

import time
from chat_tools import run_chat_message
from utils import get_user_input, notify_user
from memory import (
    get_message_count, clear_history, get_conversation_summary,
    generate_project_summary, get_projects, get_project_summary
)

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
                print("  • projects - List all projects")
                print("  • generate summary - Create project summary")
                print("  • view summary - Show current project summary")
                print("  • help - Show this help message")
                print("  • quit / exit / bye - Stop the agent")
                print()
                print("🧠 Memory Features:")
                print("  • Autonomous: Assistant automatically searches memory when needed")
                print("  • Manual: 'What did I say about...' or 'Did I mention...'")
                print("  • Direct: 'search: <term>' for specific searches")
                print("  • Per-Project: Summaries provide context awareness")
                continue
            
            if user_input.lower() == 'projects':
                projects = get_projects()
                print("📁 Available Projects:")
                for project in projects:
                    summary_indicator = "📝" if project.get('summary') else "📄"
                    print(f"  {summary_indicator} {project['name']} (ID: {project['id']}, {project['message_count']} messages)")
                continue
            
            if user_input.lower() == 'generate summary':
                # For CLI, use default project (ID 1)
                project_id = 1
                message_count = get_message_count(project_id)
                if message_count < 5:
                    print("⚠️ Need at least 5 messages to generate a summary")
                else:
                    print("🧠 Generating project summary...")
                    summary = generate_project_summary(project_id)
                    if summary:
                        print(f"✅ Summary generated:\n{summary}")
                    else:
                        print("❌ Failed to generate summary")
                continue
            
            if user_input.lower() == 'view summary':
                # For CLI, use default project (ID 1)
                project_id = 1
                summary = get_project_summary(project_id)
                if summary:
                    print(f"📋 Current Project Summary:\n{summary}")
                else:
                    print("📋 No summary available for this project")
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
