# chat_tools.py

from ollama import chat
from canvas_tools import get_assignments, get_announcements, get_calendar_events, get_courses
from memory import (
    log_message, get_conversation_messages, search_memory, get_project,
    get_project_summary, generate_project_summary, should_update_summary
)
import json
import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
from typing import Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from serpapi import GoogleSearch

TOOLS = [  # same tool schema from chat.py
    {
        "type": "function",
        "function": {
            "name": "get_assignments",
            "description": "Get Canvas assignments and homework. Can filter by due date and status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "due_date": {"type": "string"},
                    "status": {"type": "string"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_announcements",
            "description": "Get Canvas announcements and news from courses.",
            "parameters": {
                "type": "object",
                "properties": {
                    "unread_only": {"type": "boolean"},
                    "course_id": {"type": "string"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_calendar_events",
            "description": "Get Canvas calendar events and scheduled activities.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_courses",
            "description": "Get list of current active Canvas courses.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_memory",
            "description": "Search through past conversation history for relevant information. Use this when the user refers to previous discussions, asks about past topics, or when context from earlier conversations would be helpful to answer their question.",
            "parameters": {
                "type": "object",
                "properties": {
                    "term": {
                        "type": "string",
                        "description": "The search term or keyword to look for in past conversations. Use relevant keywords from the user's query."
                    }
                },
                "required": ["term"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for information. Use this when the user asks a question that requires real-time information or data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look for on the web"
                    },
                    "location": {
                        "type": "string",
                        "description": "Location for localized search results (optional, defaults to 'United States')"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

def detect_memory_query(message: str) -> Optional[str]:
    """Simple rule-based NLP to detect memory search intent.
    
    Args:
        message: The user's input message
        
    Returns:
        Search term if memory query detected, None otherwise
    """
    memory_keywords = [
        "did i mention", "what did i say", "have i talked about", 
        "remind me about", "memory of", "search memory for",
        "do you remember", "what did we discuss", "have we talked about",
        "did we discuss", "recall", "remember when", "what was that about",
        "find in memory", "look up", "search for"
    ]
    
    message_lower = message.lower()
    
    # Check for direct memory search commands first
    if message_lower.startswith("search:") or message_lower.startswith("find:"):
        return message[message.find(":")+1:].strip()
    
    for phrase in memory_keywords:
        if phrase in message_lower:
            # Different extraction strategies based on the phrase
            if phrase in ["what did i say", "did i mention", "have i talked about", "did we discuss", "what did we discuss"]:
                # Look for "about X" pattern
                about_pos = message_lower.find("about")
                if about_pos > -1:
                    search_term = message[about_pos + 5:].strip(" ?\"'.,!").strip()
                    # Remove "about" if it got included
                    if search_term.lower().startswith("about "):
                        search_term = search_term[6:]
                else:
                    # Extract everything after the phrase
                    parts = message_lower.split(phrase)
                    if len(parts) > 1:
                        search_term = parts[-1].strip(" ?\"'.,!").strip()
                    else:
                        continue
            elif phrase in ["remind me about", "memory of", "search memory for", "search for"]:
                # Extract term after these phrases
                parts = message_lower.split(phrase)
                if len(parts) > 1:
                    search_term = parts[-1].strip(" ?\"'.,!").strip()
                else:
                    continue
            else:
                # Generic extraction
                parts = message_lower.split(phrase)
                if len(parts) > 1:
                    search_term = parts[-1].strip(" ?\"'.,!").strip()
                else:
                    continue
            
            # Clean up the search term
            if search_term:
                # Remove common stop words that don't help search
                stop_words = ["the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "anything", "something"]
                search_words = [word for word in search_term.split() if word not in stop_words and len(word) > 1]
                if search_words:
                    return " ".join(search_words)
    
    return None

def format_memory_results(results: list, search_term: str) -> str:
    """Format memory search results for display.
    
    Args:
        results: List of tuples (role, content, timestamp)
        search_term: The original search term
        
    Returns:
        Formatted string with search results
    """
    if not results:
        return f"🔍 I didn't find anything in memory about '{search_term}'."
    
    formatted_results = [f"🔍 Found {len(results)} result(s) for '{search_term}':\n"]
    
    for i, (role, content, timestamp) in enumerate(results, 1):
        # Format timestamp nicely
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime("%b %d, %Y at %I:%M %p")
        except:
            time_str = timestamp
        
        # Truncate long messages
        if len(content) > 150:
            content = content[:147] + "..."
        
        role_icon = "👤" if role == "user" else "🤖"
        formatted_results.append(f"{i}. {time_str} — {role_icon} {role}: {content}")
    
    return "\n".join(formatted_results)

def format_memory_results_for_llm(results: list) -> str:
    """Format memory search results for LLM consumption.
    
    Args:
        results: List of tuples (role, content, timestamp)
        
    Returns:
        Formatted string optimized for LLM context
    """
    if not results:
        return "No relevant information found in conversation history."
    
    formatted_results = ["Relevant conversation history:"]
    
    for role, content, timestamp in results:
        # Format timestamp
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime("%b %d, %Y")
        except:
            time_str = timestamp
        
        formatted_results.append(f"[{time_str}] {role.title()}: {content}")
    
    return "\n".join(formatted_results)

def fetch_webpage_content(url: str, timeout: int = 5) -> str:
    """Fast webpage content fetching with shorter timeout and optimized parsing.
    
    Args:
        url: The URL to fetch content from
        timeout: Request timeout in seconds (reduced from 10 to 5)
        
    Returns:
        Clean text content from the webpage
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=timeout, stream=True)
        response.raise_for_status()
        
        # Limit content size to prevent processing huge files
        content_limit = 100000  # 100KB max
        content = b''
        for chunk in response.iter_content(chunk_size=8192):
            content += chunk
            if len(content) > content_limit:
                break
        
        # Parse HTML content
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remove script and style elements quickly
        for script in soup(["script", "style", "nav", "header", "footer", "aside", "iframe"]):
            script.decompose()
        
        # Extract text from main content areas (prioritized approach)
        main_content = (
            soup.find('main') or 
            soup.find('article') or 
            soup.find('div', class_=re.compile(r'content|main|article|post', re.I)) or
            soup.find('div', id=re.compile(r'content|main|article|post', re.I)) or
            soup.body
        )
        
        if main_content:
            text = main_content.get_text(separator=' ', strip=True)
        else:
            text = soup.get_text(separator=' ', strip=True)
        
        # Quick text cleanup
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Return first 3000 chars to avoid processing huge content
        return text[:3000] if len(text) > 3000 else text
        
    except Exception as e:
        return f"❌ Could not fetch content from {url}: {str(e)}"

def summarize_content_with_ai(content: str, max_length: int = 400) -> str:
    """Fast content summarization without AI calls for better performance.
    
    Args:
        content: The content to summarize
        max_length: Maximum length of the summary
        
    Returns:
        Summarized content using intelligent truncation
    """
    if len(content) <= max_length:
        return content
    
    # Try to find good break points (sentences, paragraphs)
    sentences = content.split('. ')
    summary = ""
    
    for sentence in sentences:
        if len(summary + sentence + '. ') <= max_length - 20:
            summary += sentence + '. '
        else:
            break
    
    # If we couldn't build a good summary, just truncate intelligently
    if len(summary) < max_length // 2:
        summary = content[:max_length-3] + "..."
    
    return summary.strip()

def process_webpage_content(url: str, max_chars: int = 500) -> str:
    """Fast webpage content processing without AI summarization.
    
    Args:
        url: URL to process
        max_chars: Maximum characters for the final content
        
    Returns:
        Processed content
    """
    try:
        # Fetch the webpage content
        raw_content = fetch_webpage_content(url, timeout=3)  # Even shorter timeout
        
        if raw_content.startswith("❌"):
            return raw_content
        
        # Filter out very short content
        if len(raw_content.strip()) < 50:
            return f"📄 Content too brief from {url}"
        
        # Use simple summarization instead of AI
        summary = summarize_content_with_ai(raw_content, max_chars)
        
        return f"📄 {summary}"
        
    except Exception as e:
        return f"❌ Error processing {url}: {str(e)}"

def process_urls_concurrently(urls_data: list, max_chars: int = 500) -> list:
    """Process multiple URLs concurrently for much better performance.
    
    Args:
        urls_data: List of tuples (idx, title, url)
        max_chars: Maximum characters per content summary
        
    Returns:
        List of formatted content summaries
    """
    if not urls_data:
        return []
    
    content_summaries = []
    
    # Process URLs concurrently with a ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all tasks
        future_to_data = {
            executor.submit(process_webpage_content, url, max_chars): (idx, title, url)
            for idx, title, url in urls_data
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_data, timeout=10):  # 10 second total timeout
            idx, title, url = future_to_data[future]
            try:
                content = future.result(timeout=1)  # 1 second per result
                content_summaries.append((idx, title, content))
            except Exception as e:
                content_summaries.append((idx, title, f"❌ Timeout processing {title}"))
    
    # Sort by original index to maintain order
    content_summaries.sort(key=lambda x: x[0])
    
    # Format results
    formatted_summaries = []
    for idx, title, content in content_summaries:
        formatted_summaries.append(f"**{idx}. {title}**")
        formatted_summaries.append(f"{content}\n")
    
    return formatted_summaries

def search_web_enhanced(query: str, location: str = "United States", include_content: bool = True) -> Tuple[str, str]:
    """Enhanced web search with optional webpage content reading.
    
    Args:
        query: The search query
        location: Location for localized results
        include_content: Whether to fetch and summarize webpage content
        
    Returns:
        Tuple of (full_response_for_user, condensed_version_for_memory)
    """
    try:
        # Get API key from environment variable
        api_key = os.getenv('SERPAPI_KEY')
        if not api_key:
            error_msg = "❌ Web search unavailable: SERPAPI_KEY environment variable not set"
            return error_msg, error_msg
        
        params = {
            "q": query,
            "location": location,
            "hl": "en",
            "gl": "us",
            "google_domain": "google.com",
            "api_key": api_key,
            "num": 5  # Limit to 5 results
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Check for errors
        if "error" in results:
            error_msg = f"❌ Search error: {results['error']}"
            return error_msg, error_msg
        
        # Format the basic results
        organic_results = results.get("organic_results", [])
        if not organic_results:
            no_results_msg = f"🔍 No web search results found for '{query}'"
            return no_results_msg, no_results_msg
        
        # Build basic search results
        formatted_results = [f"🌐 Web search results for '{query}':\n"]
        urls_processed = []
        
        for i, result in enumerate(organic_results[:5], 1):  # Top 5 results
            title = result.get("title", "No title")
            link = result.get("link", "")
            snippet = result.get("snippet", "No description available")
            
            # Truncate long snippets
            if len(snippet) > 200:
                snippet = snippet[:197] + "..."
            
            formatted_results.append(f"{i}. **{title}**")
            formatted_results.append(f"   {snippet}")
            formatted_results.append(f"   🔗 {link}\n")
            
            # Collect URLs for content processing (top 3 only to avoid being slow)
            if include_content and i <= 3 and link:
                urls_processed.append((i, title, link))
        
        basic_results = "\n".join(formatted_results)
        
        # Process webpage content concurrently if requested
        full_response = basic_results
        if include_content and urls_processed:
            print(f"🔄 Processing {len(urls_processed)} websites concurrently...")
            
            # Use concurrent processing instead of sequential
            content_summaries = process_urls_concurrently(urls_processed, max_chars=400)
            
            if content_summaries:
                full_response += "\n📖 **Webpage Content Summaries:**\n" + "\n".join(content_summaries)
        
        # Create condensed version for memory (memory-safe)
        num_results = len(organic_results)
        memory_version = f"🌐 Web search: '{query}' - Found {num_results} results"
        if include_content:
            memory_version += f" with content summaries from top {len(urls_processed)} websites"
        
        return full_response, memory_version
        
    except Exception as e:
        error_msg = f"❌ Enhanced web search failed: {str(e)}"
        return error_msg, error_msg

def search_web(query: str, location: str = "United States") -> str:
    """Original search_web function - now uses enhanced version internally.
    
    Args:
        query: The search query
        location: Location for localized results
        
    Returns:
        Formatted string with search results and webpage content
    """
    full_response, _ = search_web_enhanced(query, location, include_content=True)
    return full_response

def run_chat_message(message: str, project_id: int = None) -> str:
    # Log the user message first
    log_message("user", message, project_id)
    
    # Check if we should generate/update project summary (periodic summarization)
    if project_id and should_update_summary(project_id):
        print("🧠 Updating project summary...")
        generate_project_summary(project_id)
    
    # Check if this is a manual memory search query first (fallback behavior)
    manual_search_term = detect_memory_query(message)
    if manual_search_term:
        results = search_memory(manual_search_term, project_id=project_id)
        reply = format_memory_results(results, manual_search_term)
        log_message("assistant", reply, project_id)
        return reply
    
    today_str = datetime.now().strftime("%B %d, %Y")

    # Get recent conversation history (last 6 messages to leave room for memory search results)
    recent_history = get_conversation_messages(limit=6, project_id=project_id)
    
    # Get project-specific system prompt
    project_system_prompt = "You are an AI assistant with access to Canvas LMS tools and conversation memory."
    if project_id:
        project = get_project(project_id)
        if project and project.get('system_prompt'):
            project_system_prompt = project['system_prompt']
    
    # Build messages array starting with enhanced system prompt
    messages = [
        {
            "role": "system",
            "content": (
                f"{project_system_prompt} "
                f"The current date is {today_str}. "
                "When users ask about assignments, homework, announcements, calendar events, or courses, "
                "use the appropriate Canvas tools to get real data. "
                "When users refer to past conversations, ask about previous topics they mentioned, "
                "or when context from earlier discussions would help answer their question, "
                "use the search_memory tool to find relevant information from conversation history. "
                "Be helpful and conversational in your responses, and use memory search proactively "
                "when it would provide valuable context for your answer."
            )
        }
    ]
    
    # Inject project summary if available (context injection)
    if project_id:
        summary = get_project_summary(project_id)
        if summary:
            messages.append({
                "role": "system",
                "content": f"🧠 Project Summary: {summary}"
            })
    
    # Add recent conversation history
    messages.extend(recent_history)
    
    # Add the current user message
    messages.append({
        "role": "user",
        "content": message
    })

    response = chat(model="qwen3:4b", messages=messages, tools=TOOLS)
    tool_calls = getattr(response.message, "tool_calls", None)

    if not tool_calls:
        # Log assistant response and return
        assistant_response = response.message.content
        log_message("assistant", assistant_response, project_id)
        return assistant_response

    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        tool_args = tool_call.function.arguments
        if isinstance(tool_args, str):
            tool_args = json.loads(tool_args)

        if tool_name == "get_assignments":
            result = get_assignments(**tool_args)
        elif tool_name == "get_announcements":
            result = get_announcements(**tool_args)
        elif tool_name == "get_calendar_events":
            result = get_calendar_events(**tool_args)
        elif tool_name == "get_courses":
            result = get_courses()
        elif tool_name == "search_memory":
            # Handle autonomous memory search (project-scoped)
            search_term = tool_args.get("term", "")
            memory_results = search_memory(search_term, limit=5, project_id=project_id)
            result = format_memory_results_for_llm(memory_results)
        elif tool_name == "search_web":
            # Handle web search with enhanced content reading
            query = tool_args.get("query", "")
            location = tool_args.get("location", "United States")
            
            # Use enhanced search that returns both full response and memory-safe version
            full_response, memory_version = search_web_enhanced(query, location, include_content=True)
            
            # Log the memory-safe version instead of the full response
            log_message("assistant", f"🔧 Web Search Tool: {memory_version}", project_id)
            
            # Return the full response for the AI to use
            result = full_response
        else:
            result = f"Unknown tool: {tool_name}"

        results.append({"role": "tool", "name": tool_name, "content": str(result)})

    messages.append({"role": "assistant", "tool_calls": tool_calls})
    messages.extend(results)

    follow_up = chat(model="qwen3:4b", messages=messages)
    
    # Log the final assistant response
    assistant_response = follow_up.message.content
    log_message("assistant", assistant_response, project_id)
    
    return assistant_response
