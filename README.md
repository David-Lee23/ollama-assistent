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
3. **Per-Project Summary Memory** - Intelligent project-scoped context awareness with LLM-generated summaries
4. **Project Management** - Create, switch between, and manage multiple projects with individual contexts
5. **Autonomous Memory Search** - LLM automatically searches memory when context is needed
6. **Manual Memory Search** - Natural language search through conversation history
7. **Tool-based Function Calling** - Integration with Canvas API through function calls
8. **Interactive Chat Loop** - Timeout-based interaction with user-friendly prompts
9. **Modern Web Interface** - Flask-based responsive web dashboard

### 🌐 **New: Web Interface**

**Modern Dashboard Features:**
- **Chat-Centered Design**: Primary conversation interface with real-time messaging
- **Project Management**: Create, switch between, and manage multiple projects with individual contexts
- **Project Summary Display**: View and generate intelligent project summaries for long-term context
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

### 🧠 Per-Project Summary Memory System:
**Intelligent Context Awareness for Long-Term Projects**

The Per-Project Summary Memory System maintains lightweight, persistent summaries of each project's conversation history, enabling the LLM to understand project context without token bloat:

**Key Features:**
- **Automatic Summarization**: Generates intelligent 3-5 bullet point summaries using the LLM
- **Context Injection**: Project summaries are automatically injected into every conversation
- **Smart Triggers**: 
  - Initial summary generated after 10+ messages
  - Auto-refresh every 25 new messages
  - Manual generation on-demand
- **Project-Scoped**: Each project maintains its own contextual memory
- **Visual Indicators**: 📝 for projects with summaries, 📄 for those without

**How It Works:**
1. As you chat within a project, the system tracks message count
2. When thresholds are met, the LLM automatically generates a summary covering:
   - Key topics and themes discussed
   - Important decisions or conclusions reached
   - Current project status or progress
   - Any ongoing tasks or next steps
3. This summary is injected into every future conversation, providing the LLM with project context

**Usage:**
- **Web Interface**: Click "Generate Summary" button to create/update summaries
- **CLI Commands**: 
  - `projects` - List all projects with summary indicators
  - `generate summary` - Create/update summary for current project
  - `view summary` - Display current project summary

**Benefits:**
- **Context-Efficient**: Long-term project awareness without full history injection
- **Scalable**: Works regardless of conversation length
- **Autonomous**: Automatic management with minimal user intervention
- **Project-Aware**: Clean separation between different projects and contexts

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
- `main_agent.py` - Main CLI application loop with memory status display and project commands
- `app.py` - Flask web application with REST API endpoints and project management
- `start_web.py` - Web interface startup script
- `chat_tools.py` - Chat handling with Canvas tools, autonomous memory search, and summary injection
- `canvas_tools.py` - Canvas LMS API integration
- `memory.py` - SQLite-based conversation memory system with project management and summary features
- `utils.py` - Utility functions for user input and notifications
- `agent_memory.db` - SQLite database storing conversation history and project summaries
- `templates/` - HTML templates for web interface with project management UI
- `static/` - CSS and JavaScript files for web interface including summary functionality

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

The agent will show memory status on startup and maintain conversation context across sessions with intelligent project summaries.

### 🌐 **Web Interface Features:**

**Main Dashboard:**
- Split-view layout with chat on left, tools on right
- Project selector with summary indicators (📝/📄)
- Real-time conversation with message history
- Project summary display for current context
- Memory search and Canvas tools in side panels
- Responsive design for mobile and desktop

**Key Components:**
- 💬 **Chat Interface**: Send messages, view responses, see typing indicators
- 📁 **Project Management**: Create, switch between, and manage multiple projects
- 🧠 **Summary System**: Generate and view intelligent project summaries
- 🔍 **Memory Panel**: Search conversations, view memory stats, clear history
- 🎓 **Canvas Panel**: Quick access to assignments, announcements, calendar
- ⚙️ **System Panel**: Status monitoring, memory management, data export
- 📱 **Mobile Ready**: Collapsible panels and responsive layout

### 🔧 Available Commands:

**Web Interface:**
- Interactive chat with real-time responses and project context
- Project creation, editing, and deletion through modal dialogs
- One-click summary generation with "Generate Summary" button
- Memory search through dedicated search box
- Canvas tool buttons for quick data access
- Clear memory and export data buttons

**CLI Interface:**
- **Project Management**: `projects` - List all projects with summary indicators
- **Summary Commands**: `generate summary`, `view summary` - Manage project summaries
- **Memory Management**: `memory`, `memory status`, `clear memory`
- **Manual Memory Search**: Natural language queries or `search: <term>`
- **Help**: `help` - Show all available commands
- **Exit**: `quit`, `exit`, `bye`

### 🛠️ Technical Implementation:
- **Flask Backend**: REST API with endpoints for chat, memory, projects, and Canvas tools
- **Modern Frontend**: HTML5, CSS3, JavaScript with responsive design and project management
- **Real-time Communication**: AJAX requests with loading states and error handling
- **Project Summary System**: LLM-powered automatic summarization with context injection
- **search_memory Tool**: Added to TOOLS array for LLM function calling
- **Enhanced System Prompt**: Encourages proactive memory usage with project awareness
- **Dual Search Modes**: Autonomous (LLM-driven) + Manual (rule-based fallback)
- **Optimized Formatting**: Different result formats for LLM vs human consumption
- **Context Management**: Project summaries + recent history for optimal token usage

### 🔌 **API Endpoints:**
- `POST /api/chat` - Send message to assistant with project context
- `GET /api/projects` - Get all projects
- `POST /api/projects` - Create new project
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project
- `GET /api/projects/{id}/summary` - Get project summary
- `POST /api/projects/{id}/summary` - Generate project summary
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
# 3. ✅ Per-Project Summary Memory - **IMPLEMENTED with LLM-generated summaries**
# 4. User model / learning preferences
# 5. Subject-aware context switching
# 6. Time-aware scheduling (with calendar integration)
# 7. Self-assessment engine (quizzing, reflection)
# 8. CLI or system tool control (local code helper)
# 9. File awareness (upload docs, ask questions)
# 10. Multimodal interface (voice + text)
# 11. Transparent logic/debug output
# 12. Self-auditing agent loops

# 🎯 Target Users:
# - College student (you)
# - (Later) classmates, family, or open-source community

# 🗓️ Current Status:
# - ✅ Basic chat functionality with Canvas integration
# - ✅ Memory system with SQLite conversation history
# - ✅ Per-Project Summary Memory System with intelligent context awareness
# - ✅ Project management with individual contexts and summaries
# - ✅ Autonomous memory search (LLM-driven) + manual search
# - ✅ Tool-based function calling for Canvas data
# - ✅ Modern web interface with responsive design and project management
# - 🔄 Ready for advanced features and improvements

# Ollama Assistant

An AI assistant with Canvas LMS integration, conversation memory, and web search capabilities.

## Features

- **Canvas LMS Integration**: Access assignments, announcements, calendar events, and course information
- **Conversation Memory**: Persistent memory with smart search and project-based organization
- **Enhanced Web Search**: Real-time web search with AI-powered webpage content reading and summarization
- **Project Management**: Organize conversations by projects with automatic summarization

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
# For Canvas LMS integration
export CANVAS_TOKEN="your_canvas_token"
export CANVAS_URL="https://your-institution.instructure.com"

# For web search functionality
export SERPAPI_KEY="your_serpapi_key"
```

3. Run the application:
```bash
python app.py
```

## Web Search Setup

To enable web search functionality:

1. Sign up for a SerpAPI account at https://serpapi.com/
2. Get your API key from the dashboard
3. Set the environment variable:
   ```bash
   export SERPAPI_KEY="your_api_key_here"
   ```

The web search tool will automatically be available to the assistant when the API key is configured.

## Usage

The assistant can:
- Answer questions about your Canvas courses, assignments, and calendar
- Search through conversation history when you reference past discussions  
- Search the web and read webpage content for comprehensive, up-to-date information
- Intelligently summarize web content while keeping conversation memory clean
- Maintain context across conversations within projects

Example queries:
- "What assignments are due this week?"
- "Search for recent news about artificial intelligence" (now includes full article content!)
- "Find Python tutorials and summarize the best practices"
- "What did we discuss about machine learning last time?"
- "Show me my upcoming calendar events"

## Project Structure

- `app.py` - Main application entry point
- `chat_tools.py` - Core chat functionality with tool integration
- `canvas_tools.py` - Canvas LMS API integration
- `memory.py` - Conversation memory and search functionality
- `main_agent.py` - Agent coordination logic
- `start_web.py` - Web interface startup
- `templates/` - HTML templates for web interface
- `static/` - CSS and JavaScript assets