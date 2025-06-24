# Project: Student Agent Assistant

# 🧠 Goal:
# Build a local AI-powered assistant hosted on a personal server (Linux Mint) using Ollama,
# capable of:
# - RAG (Retrieval-Augmented Generation)
# - Tool use (function calling)
# - Simple agent-like behavior (multi-step reasoning)
#
# Then expand it with powerful custom features for personalization, memory, context, and utility for school and home use.

# 🔨 Tech Stack (MVP):
# - Ollama (local LLM: LLaMA 3 / DeepSeek / Mixtral)
# - Python (Flask or FastAPI)
# - Chroma or Supabase (for vector search / memory)
# - Whisper.cpp (voice input)
# - Piper TTS (voice output)
# - Optional frontends: Streamlit, React, Telegram bot

## 🎯 Current Implementation

### ✅ Completed Features:
1. **Canvas LMS Integration** - Access to assignments, announcements, calendar events, and courses
2. **Memory System** - SQLite-based conversation history with persistent storage
3. **Tool-based Function Calling** - Integration with Canvas API through function calls
4. **Interactive Chat Loop** - Timeout-based interaction with user-friendly prompts

### 🧠 Memory System Features:
- **Persistent Conversation History**: All interactions stored in SQLite database
- **Context Awareness**: Last 8 messages automatically included in conversation context
- **Memory Commands**:
  - `memory` or `memory status` - View current memory statistics
  - `clear memory` - Reset conversation history
- **Automatic Logging**: All user and assistant messages automatically saved
- **Conversation Summaries**: View activity summaries for recent periods

### 📁 File Structure:
- `main_agent.py` - Main application loop with memory status display
- `chat_tools.py` - Chat handling with Canvas tools and memory integration
- `canvas_tools.py` - Canvas LMS API integration
- `memory.py` - SQLite-based conversation memory system
- `utils.py` - Utility functions for user input and notifications
- `agent_memory.db` - SQLite database storing conversation history

### 🚀 Usage:
```bash
python main_agent.py
```

The agent will show memory status on startup and maintain conversation context across sessions.

# 🚀 Post-MVP Feature Ideas:
# 1. ✅ Long-term memory (semantic) - **IMPLEMENTED with SQLite**
# 2. User model / learning preferences
# 3. Subject-aware context switching
# 4. Time-aware scheduling (with calendar integration)
# 5. Self-assessment engine (quizzing, reflection)
# 6. CLI or system tool control (local code helper)
# 7. File awareness (upload docs, ask questions)
# 8. Multimodal interface (voice + text)
# 9. Transparent logic/debug output
# 10. Self-auditing agent loops

# 🎯 Target Users:
# - College student (you)
# - (Later) classmates, family, or open-source community

# 🗓️ Current Status:
# - ✅ Basic chat functionality with Canvas integration
# - ✅ Memory system with SQLite conversation history
# - ✅ Tool-based function calling for Canvas data
# - 🔄 Ready for advanced features and improvements
