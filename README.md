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
3. **Autonomous Memory Search** - LLM automatically searches memory when context is needed
4. **Manual Memory Search** - Natural language search through conversation history
5. **Tool-based Function Calling** - Integration with Canvas API through function calls
6. **Interactive Chat Loop** - Timeout-based interaction with user-friendly prompts

### 🧠 Memory System Features:
- **Persistent Conversation History**: All interactions stored in SQLite database
- **Context Awareness**: Last 6 messages automatically included in conversation context
- **Autonomous Memory Search**: LLM automatically decides when to search memory for context
  - No explicit commands needed - just ask naturally
  - Example: "Can you help with my exam?" → LLM searches for "exam" automatically
- **Manual Memory Search**: Ask questions like:
  - "What did I say about math?"
  - "Did I mention Python?"
  - "Have we talked about exams?"
  - "Remind me about my project"
  - "search: calculus" (direct search)
- **Memory Commands**:
  - `memory` or `memory status` - View current memory statistics
  - `clear memory` - Reset conversation history
  - `help` - Show all available commands
- **Automatic Logging**: All user and assistant messages automatically saved
- **Conversation Summaries**: View activity summaries for recent periods

### 🤖 Autonomous Memory Search:
The assistant now intelligently searches its memory without being explicitly told to:

```
User: "Can you help me prepare for my exam?"
LLM: *automatically searches memory for "exam"*
Assistant: "I remember you mentioned a calculus exam on Thursday that you're stressed about. 
          Let me help you prepare! What specific topics would you like to focus on?"
```

**How it works:**
1. User mentions something that might reference past conversations
2. LLM detects context dependency and calls `search_memory` tool automatically
3. Relevant conversation history is retrieved and injected into the response
4. Assistant provides contextually-aware answers using past information

### 🔍 Memory Search Examples:
```
Manual Search:
User: "What did I say about my Python project?"
Agent: 🔍 Found 2 result(s) for 'python project':
       1. Jun 24, 2025 at 2:30 PM — 👤 user: I'm working on a Python project...
       2. Jun 24, 2025 at 2:31 PM — 🤖 assistant: That sounds interesting! What kind...

Autonomous Search:
User: "How should I approach my project?"
Agent: Based on our previous discussion about your Python web scraping project for CS class,
       I'd recommend starting with the requests library and BeautifulSoup...
```

### 📁 File Structure:
- `main_agent.py` - Main application loop with memory status display and commands
- `chat_tools.py` - Chat handling with Canvas tools, autonomous & manual memory search
- `canvas_tools.py` - Canvas LMS API integration
- `memory.py` - SQLite-based conversation memory system with search capabilities
- `utils.py` - Utility functions for user input and notifications
- `agent_memory.db` - SQLite database storing conversation history

### 🚀 Usage:
```bash
python main_agent.py
```

The agent will show memory status on startup and maintain conversation context across sessions.

### 🔧 Available Commands:
- **Memory Management**: `memory`, `memory status`, `clear memory`
- **Manual Memory Search**: Natural language queries or `search: <term>`
- **Help**: `help` - Show all available commands
- **Exit**: `quit`, `exit`, `bye`

### 🛠️ Technical Implementation:
- **search_memory Tool**: Added to TOOLS array for LLM function calling
- **Enhanced System Prompt**: Encourages proactive memory usage
- **Dual Search Modes**: Autonomous (LLM-driven) + Manual (rule-based fallback)
- **Optimized Formatting**: Different result formats for LLM vs human consumption
- **Context Management**: Reduced recent history to 6 messages to make room for memory results

# 🚀 Post-MVP Feature Ideas:
# 1. ✅ Long-term memory (semantic) - **IMPLEMENTED with SQLite + Autonomous Search**
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
# - ✅ Autonomous memory search (LLM-driven) + manual search
# - ✅ Tool-based function calling for Canvas data
# - 🔄 Ready for advanced features and improvements
