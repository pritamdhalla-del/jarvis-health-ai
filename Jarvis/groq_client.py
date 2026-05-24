"""
Groq Client Manager with Tool Calling
=====================================
Handles all interactions with the Groq API for Jarvis with system control capabilities.
"""

from groq import Groq
from typing import Generator, List, Dict, Optional
import json
import re
import time
from config import GROQ_API_KEY, MAX_TOKENS, TEMPERATURE, TOP_P, MAX_HISTORY_LENGTH, MODEL_NAME, FALLBACK_MODELS
from system_tools import execute_tool
from web_tools import WebTools
from usage_tracker import UsageTracker


# Smart system prompt - natural conversation + tool awareness
SYSTEM_PROMPT = """You are JARVIS (Just A Rather Very Intelligent System), Tony Stark's AI assistant.

=== YOUR BRAIN (Knowledge & Personality) ===
- You are sophisticated, witty, warm, and personable
- Address the user as "Sir" occasionally
- Keep responses concise - 1-2 sentences max
- You have vast general knowledge to answer questions

=== YOUR HANDS (System Capabilities) ===
When someone asks "What can you do?" respond with this list:
- Open/close applications (Chrome, Safari, VSCode, Spotify, etc.)
- Browse websites (open single or multiple sites)
- Control Chrome tabs (list, close, scroll, zoom, navigate)
- Search and control YouTube (search, play, pause, skip, volume)
- Manage files (list folders, find files, read files)
- System controls (volume, screenshot, battery, trash)
- Run terminal commands
- **ACCESS THE INTERNET**: Search Google and read web pages to answer up-to-date questions.
- **TRACK API USAGE**: Report how many API calls you have made.

=== CRITICAL: WHEN TO USE TOOLS vs JUST TALK ===

❌ DO NOT USE TOOLS FOR:
- Greetings: "Hi", "Hello", "How are you" → Just respond warmly
- Opinions: "What do you think about X?" → Share your perspective  
- Jokes/Chat: "Tell me a joke" → Be witty
- Asking about you: "What can you do?", "Who made you?" → Explain yourself
- Advice: "How should I learn coding?" → Give advice

✅ USE TOOLS ONLY FOR:
- "Open Chrome/YouTube/Spotify" → open_application
- "Search online for X" → search_internet
- "What is the latest news on Y" → search_internet -> read_url (if needed)
- "Read this article..." → read_url
- "How many API calls have you made?" → get_api_usage
- "Open youtube.com" → open_url
- "Scroll down" → scroll_chrome
- "Search cats on YouTube" → youtube_search

=== CRITICAL INSTRUCTION FOR APPS ===
If user asks to open an app you don't know (e.g., "Superwhisper", "Cursor", "Linear"):
1. DO NOT say "I don't know that app"
2. JUST TRY to open it: {"tool": "open_application", "app_name": "Superwhisper"}
3. The system will handle it if it doesn't exist. YOUR JOB is to try.

=== OUTPUT RULES ===

WEB:
{"tool": "search_internet", "query": "latest AI news"}
{"tool": "read_url", "url": "https://example.com"}

USAGE:
{"tool": "get_api_usage"}

FILES:
{"tool": "list_directory", "path": "~/Desktop"}
{"tool": "find_folder", "folder_name": "Projects"}
{"tool": "search_files", "pattern": "*.pdf"}
{"tool": "read_file", "file_path": "~/notes.txt"}
{"tool": "open_file", "file_path": "~/doc.pdf"}

APPS:
{"tool": "open_application", "app_name": "Chrome"}
{"tool": "close_application", "app_name": "Safari"}
{"tool": "list_running_apps"}

BROWSER (single):
{"tool": "open_url", "url": "youtube.com"}
{"tool": "close_chrome_tab", "tab": "YouTube"}

BROWSER (multiple - USE ARRAYS):
{"tool": "open_urls", "urls": ["youtube.com", "instagram.com"]}
{"tool": "close_chrome_tabs", "tabs": ["YouTube", "Instagram"]}

CHROME CONTROL:
{"tool": "list_chrome_tabs"}
{"tool": "scroll_chrome", "direction": "down"}
{"tool": "chrome_navigate", "action": "back"}
{"tool": "type_in_chrome", "text": "hello"}
{"tool": "chrome_zoom", "action": "in"}

YOUTUBE:
{"tool": "youtube_search", "query": "cats"}
{"tool": "youtube_control", "action": "pause"}

SYSTEM:
{"tool": "set_volume", "level": 50}
{"tool": "mute"}
{"tool": "take_screenshot"}
{"tool": "get_battery_status"}
{"tool": "run_command", "command": "ls"}

=== OUTPUT RULES ===
- For CONVERSATION → Reply naturally in text, NO JSON
- For ACTIONS → Output ONLY the JSON, nothing else
- NEVER use tools for casual conversation or questions"""


class JarvisGroqClient:
    """Client for Jarvis with intelligent conversation and system control."""
    
    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found!")
        
        self.client = Groq(api_key=GROQ_API_KEY)
        self.conversation_history: List[Dict[str, str]] = []
        self.system_prompt = SYSTEM_PROMPT
        self.web_tools = WebTools()
        self.usage_tracker = UsageTracker()
    
    def _build_messages(self, user_message: str) -> List[Dict[str, str]]:
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": user_message})
        return messages
    
    def _update_history(self, user_message: str, assistant_response: str):
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": assistant_response})
        
        if len(self.conversation_history) > MAX_HISTORY_LENGTH * 2:
            self.conversation_history = self.conversation_history[-(MAX_HISTORY_LENGTH * 2):]
    
    def _extract_tool_call(self, response: str) -> Optional[Dict]:
        """Extract tool call from response."""
        response = response.strip()
        
        # Try different patterns
        patterns = [
            r'```json\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```',
            r'(\{[^{}]*"tool"[^{}]*\})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1).strip())
                    if "tool" in data:
                        return data
                except json.JSONDecodeError:
                    continue
        
        # Direct parse
        try:
            data = json.loads(response)
            if "tool" in data:
                return data
        except:
            pass
        
        return None
    
    def _execute_tool_from_dict(self, tool_dict: Dict) -> str:
        """Execute a tool from dictionary."""
        tool_name = tool_dict.pop("tool", None)
        if not tool_name:
            return json.dumps({"error": "No tool specified"})
        
        # Local tool handling (Web & Usage)
        if tool_name == "search_internet":
            return json.dumps(self.web_tools.search_internet(tool_dict.get("query", "")))
        
        if tool_name == "read_url":
            return json.dumps(self.web_tools.read_url(tool_dict.get("url", "")))
        
        if tool_name == "get_api_usage":
            return json.dumps(self.usage_tracker.get_usage_summary())
        
        # System tool mapping
        tool_mapping = {
            "list_directory": lambda d: {"path": d.get("path", "~")},
            "find_folder": lambda d: {"folder_name": d.get("folder_name"), "search_path": d.get("search_path", "~")},
            "search_files": lambda d: {"pattern": d.get("pattern"), "search_path": d.get("search_path", "~")},
            "read_file": lambda d: {"file_path": d.get("file_path")},
            "get_file_info": lambda d: {"file_path": d.get("file_path")},
            "run_command": lambda d: {"command": d.get("command")},
            "get_system_info": lambda d: {},
            "open_application": lambda d: {"app_name": d.get("app_name")},
            "close_application": lambda d: {"app_name": d.get("app_name")},
            "list_running_apps": lambda d: {},
            "open_url": lambda d: {"url": d.get("url")},
            "open_urls": lambda d: {"urls": d.get("urls", [])},
            "list_chrome_tabs": lambda d: {},
            "close_chrome_tab": lambda d: {"tab": d.get("tab", "")},
            "close_chrome_tabs": lambda d: {"tabs": d.get("tabs", [])},
            "scroll_chrome": lambda d: {"direction": d.get("direction", "down"), "amount": d.get("amount", 300)},
            "chrome_navigate": lambda d: {"action": d.get("action", "")},
            "type_in_chrome": lambda d: {"text": d.get("text", "")},
            "chrome_keypress": lambda d: {"key": d.get("key", "enter")},
            "youtube_search": lambda d: {"query": d.get("query", "")},
            "youtube_control": lambda d: {"action": d.get("action", "toggle")},
            "chrome_zoom": lambda d: {"action": d.get("action", "in")},
            "open_file": lambda d: {"file_path": d.get("file_path")},
            "set_volume": lambda d: {"level": d.get("level", 50)},
            "get_volume": lambda d: {},
            "mute": lambda d: {},
            "unmute": lambda d: {},
            "take_screenshot": lambda d: {"filename": d.get("filename")},
            "get_battery_status": lambda d: {},
            "empty_trash": lambda d: {},
            "sleep_display": lambda d: {},
        }
        
        if tool_name not in tool_mapping:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})
        
        args = tool_mapping[tool_name](tool_dict)
        return execute_tool(tool_name, args)
    
    def chat_with_tools(self, user_message: str, tool_callback=None) -> str:
        """Chat with tool support."""
        messages = self._build_messages(user_message)
        
        models_to_try = [MODEL_NAME] + FALLBACK_MODELS
        completion = None
        last_error = None
        used_model = None

        for model in models_to_try:
            try:
                completion = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=TEMPERATURE,
                    max_completion_tokens=MAX_TOKENS,
                    top_p=TOP_P
                )
                used_model = model
                break  # Success!
            except Exception as e:
                last_error = e
                print(f"⚠️ Model {model} failed (likely rate limit). Switching to next model...")
                continue
        
        if not completion:
            error_str = str(last_error)
            # Extract wait time (e.g., "Please try again in 3m57.6s")
            wait_match = re.search(r"Please try again in\s+([0-9ms\.]+)", error_str)
            if wait_match:
                wait_time = wait_match.group(1)
                return f"I have hit my rate limit on all safe channels, Sir. I am sleeping for {wait_time} to recharge. Please stand by."
            
            return f"❌ Error: All models failed. Last error: {error_str}"
        
        # Track usage
        if used_model:
            usage = completion.usage
            tokens = (usage.prompt_tokens + usage.completion_tokens) if usage else 0
            self.usage_tracker.increment_usage(used_model, tokens)
        
        response = completion.choices[0].message.content or ""
        tool_call = self._extract_tool_call(response)
        
        if tool_call:
            tool_name = tool_call.get("tool", "unknown")
            
            if tool_callback:
                args = {k: v for k, v in tool_call.items() if k != "tool"}
                tool_callback(tool_name, args)
            
            result = self._execute_tool_from_dict(tool_call.copy())
            
            # Get natural response based on results
            messages.append({"role": "assistant", "content": response})
            messages.append({
                "role": "user", 
                "content": f"Result:\n{result}\n\nRespond naturally and briefly based on this result. Don't explain tools or processes."
            })
            
            second_completion = self.client.chat.completions.create(
                model=used_model or MODEL_NAME,
                messages=messages,
                temperature=TEMPERATURE,
                max_completion_tokens=MAX_TOKENS,
                top_p=TOP_P
            )
            
            # Track usage for second call
            if used_model:
                usage = second_completion.usage
                tokens = (usage.prompt_tokens + usage.completion_tokens) if usage else 0
                self.usage_tracker.increment_usage(used_model, tokens)
                
            final_response = second_completion.choices[0].message.content or ""
            self._update_history(user_message, final_response)
            return final_response
        
        self._update_history(user_message, response)
        return response
    
    def chat(self, user_message: str) -> str:
        """Simple chat."""
        return self.chat_with_tools(user_message)
    
    def clear_history(self):
        self.conversation_history = []
    
    def get_history(self) -> List[Dict[str, str]]:
        return self.conversation_history.copy()


# Singleton
jarvis_client: Optional[JarvisGroqClient] = None

def get_jarvis_client() -> JarvisGroqClient:
    global jarvis_client
    if jarvis_client is None:
        jarvis_client = JarvisGroqClient()
    return jarvis_client

