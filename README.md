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
7. **Modern Web Interface** - Flask-based responsive web dashboard

### 🌐 **New: Web Interface**

**Modern Dashboard Features:**
- **Chat-Centered Design**: Primary conversation interface with real-time messaging
- **Memory & Search Panel**: Visual memory status, search functionality, and conversation history
- **Canvas Tools Panel**: Quick access buttons for assignments, announcements, calendar, and courses
- **System Panel**: Memory management, status monitoring, and data export
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Real-time Updates**: Live memory count, status indicators, and notifications

**UI Components:**
- Split-view layout with chat panel and collapsible side panels
- Modern card-based design with clean typography
- Loading states and error handling
- Toast notifications for user feedback
- Keyboard shortcuts and accessibility features

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
- `main_agent.py` - Main CLI application loop with memory status display and commands
- `app.py` - Flask web application with REST API endpoints
- `start_web.py` - Web interface startup script
- `chat_tools.py` - Chat handling with Canvas tools, autonomous & manual memory search
- `canvas_tools.py` - Canvas LMS API integration
- `memory.py` - SQLite-based conversation memory system with search capabilities
- `utils.py` - Utility functions for user input and notifications
- `agent_memory.db` - SQLite database storing conversation history
- `templates/` - HTML templates for web interface
- `static/` - CSS and JavaScript files for web interface

### 🚀 Usage:

**Web Interface (Recommended):**
```bash
python start_web.py
# Opens web dashboard at http://localhost:5000
```

**Command Line Interface:**
```bash
python main_agent.py
```

**Direct Flask App:**
```bash
python app.py
```

The agent will show memory status on startup and maintain conversation context across sessions.

### 🌐 **Web Interface Screenshots:**

**Main Dashboard:**
- Split-view layout with chat on left, tools on right
- Real-time conversation with message history
- Memory search and Canvas tools in side panels
- Responsive design for mobile and desktop

**Key Features:**
- 💬 **Chat Interface**: Send messages, view responses, see typing indicators
- 🧠 **Memory Panel**: Search conversations, view memory stats, clear history
- 🎓 **Canvas Panel**: Quick access to assignments, announcements, calendar
- ⚙️ **System Panel**: Status monitoring, memory management, data export
- 📱 **Mobile Ready**: Collapsible panels and responsive layout

### 🔧 Available Commands:

**Web Interface:**
- Interactive chat with real-time responses
- Memory search through dedicated search box
- Canvas tool buttons for quick data access
- Clear memory and export data buttons

**CLI Interface:**
- **Memory Management**: `memory`, `memory status`, `clear memory`
- **Manual Memory Search**: Natural language queries or `search: <term>`
- **Help**: `help` - Show all available commands
- **Exit**: `quit`, `exit`, `bye`

### 🛠️ Technical Implementation:
- **Flask Backend**: REST API with endpoints for chat, memory, and Canvas tools
- **Modern Frontend**: HTML5, CSS3, JavaScript with responsive design
- **Real-time Communication**: AJAX requests with loading states and error handling
- **search_memory Tool**: Added to TOOLS array for LLM function calling
- **Enhanced System Prompt**: Encourages proactive memory usage
- **Dual Search Modes**: Autonomous (LLM-driven) + Manual (rule-based fallback)
- **Optimized Formatting**: Different result formats for LLM vs human consumption
- **Context Management**: Reduced recent history to 6 messages to make room for memory results

### 🔌 **API Endpoints:**
- `POST /api/chat` - Send message to assistant
- `POST /api/memory/search` - Search conversation history
- `GET /api/memory/status` - Get memory statistics
- `POST /api/memory/clear` - Clear all memory
- `GET /api/canvas/assignments` - Get Canvas assignments
- `GET /api/canvas/announcements` - Get Canvas announcements
- `GET /api/canvas/events` - Get calendar events
- `GET /api/canvas/courses` - Get course list

# 🚀 Post-MVP Feature Ideas:
# 1. ✅ Long-term memory (semantic) - **IMPLEMENTED with SQLite + Autonomous Search**
# 2. ✅ Modern Web Interface - **IMPLEMENTED with Flask + Responsive Design**
# 3. User model / learning preferences
# 4. Subject-aware context switching
# 5. Time-aware scheduling (with calendar integration)
# 6. Self-assessment engine (quizzing, reflection)
# 7. CLI or system tool control (local code helper)
# 8. File awareness (upload docs, ask questions)
# 9. Multimodal interface (voice + text)
# 10. Transparent logic/debug output
# 11. Self-auditing agent loops

# 🎯 Target Users:
# - College student (you)
# - (Later) classmates, family, or open-source community

# 🗓️ Current Status:
# - ✅ Basic chat functionality with Canvas integration
# - ✅ Memory system with SQLite conversation history
# - ✅ Autonomous memory search (LLM-driven) + manual search
# - ✅ Tool-based function calling for Canvas data
# - ✅ Modern web interface with responsive design
# - 🔄 Ready for advanced features and improvements
