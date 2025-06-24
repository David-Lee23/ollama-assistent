# utils.py

import sys
import select

def get_user_input(timeout=60):
    """Get user input with timeout support"""
    try:
        print("👤 You: ", end="", flush=True)
        
        # Check if input is available within timeout
        if sys.stdin in select.select([sys.stdin], [], [], timeout)[0]:
            line = input().strip()
            return line
        else:
            print("⏰ (timeout)")  # Clear indication of timeout
            return None  # Timeout occurred
    except EOFError:
        return None
    except KeyboardInterrupt:
        raise  # Re-raise KeyboardInterrupt to be caught by main loop

def notify_user(message: str):
    print(f"🤖 Assistant: {message}")
    print()  # Add blank line for better readability
