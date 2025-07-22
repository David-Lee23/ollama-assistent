# Ollama Assistant

An AI-powered student assistant with Canvas LMS integration, conversation memory, and intelligent project management.

## Features

- **Canvas LMS Integration**: Access assignments, announcements, calendar events, and course information
- **Intelligent Memory System**: Persistent conversation history with autonomous search and context awareness
- **Project Management**: Organize conversations by projects with automatic AI-generated summaries
- **Web Search Integration**: Real-time web search with content summarization
- **Modern Web Interface**: Responsive dashboard with real-time chat and tool panels
- **Multi-Interface Support**: Both web UI and command-line interface

## Technology Stack

- **Backend**: Flask, SQLite, Python 3.8+
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **AI Integration**: Ollama (local LLM)
- **APIs**: Canvas LMS API, SerpAPI for web search
- **Database**: SQLite for conversation memory and project management

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ollama-assistant.git
   cd ollama-assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:
   ```bash
   # Canvas LMS Integration (optional)
   CANVAS_TOKEN=your_canvas_api_token
   CANVAS_URL=https://your-institution.instructure.com

   # Web Search (optional)
   SERPAPI_KEY=your_serpapi_key

   # Flask Security
   SECRET_KEY=your_secret_key_here
   ```

4. **Install and configure Ollama**
   ```bash
   # Install Ollama (see https://ollama.ai)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull a model (e.g., llama3)
   ollama pull qwen
   ```

## Usage

### Web Interface (Recommended)
```bash
python start_web.py
```
Navigate to `http://localhost:5000`

### Command Line Interface
```bash
python main_agent.py
```

### Direct Flask Application
```bash
python app.py
```

## Configuration

### Canvas LMS Setup
1. Log into your Canvas instance
2. Go to Account → Settings → Approved Integrations
3. Generate a new access token
4. Add the token and Canvas URL to your `.env` file

### SerpAPI Setup (for web search)
1. Sign up at [SerpAPI](https://serpapi.com/)
2. Get your API key from the dashboard
3. Add it to your `.env` file

## Project Structure

```
ollama-assistant/
├── app.py                 # Main Flask application
├── start_web.py          # Web interface startup script
├── main_agent.py         # CLI interface
├── chat_tools.py         # Core chat functionality
├── canvas_tools.py       # Canvas LMS integration
├── memory.py             # Conversation memory system
├── utils.py              # Utility functions
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates
│   └── dashboard.html
└── static/              # CSS and JavaScript assets
    ├── css/
    └── js/
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Send message to assistant |
| `/api/projects` | GET/POST | Manage projects |
| `/api/projects/{id}` | GET/PUT/DELETE | Individual project operations |
| `/api/projects/{id}/summary` | GET/POST | Project summaries |
| `/api/memory/search` | POST | Search conversation history |
| `/api/memory/status` | GET | Memory statistics |
| `/api/canvas/assignments` | GET | Canvas assignments |
| `/api/canvas/announcements` | GET | Canvas announcements |

## Key Features

### Intelligent Memory System
- Automatic conversation logging with SQLite
- Autonomous memory search (AI decides when to search past conversations)
- Manual memory search with natural language queries
- Context-aware responses using conversation history

### Project Management
- Create and manage multiple conversation projects
- AI-generated project summaries for long-term context
- Project-scoped memory and context isolation
- Automatic summary updates based on conversation activity

### Canvas Integration
- Real-time access to assignments and due dates
- Course announcements and updates
- Calendar event integration
- Direct API integration with Canvas LMS

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Ollama](https://ollama.ai/) for local LLM integration
- [Canvas LMS](https://www.instructure.com/canvas) for educational platform API
- [SerpAPI](https://serpapi.com/) for web search capabilities
