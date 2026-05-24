"""
Command Processor for Jarvis
============================
Handles special commands and system operations.
"""

import os
import sys
import webbrowser
import subprocess
from typing import Callable, Dict, Optional, Tuple
from datetime import datetime


class CommandProcessor:
    """
    Processes special commands for Jarvis.
    Commands are prefixed with '/' or triggered by keywords.
    """
    
    def __init__(self):
        """Initialize the command processor with available commands."""
        self.commands: Dict[str, Callable] = {
            'help': self.cmd_help,
            'clear': self.cmd_clear,
            'reset': self.cmd_reset,
            'time': self.cmd_time,
            'date': self.cmd_date,
            'open': self.cmd_open,
            'search': self.cmd_search,
            'exit': self.cmd_exit,
            'quit': self.cmd_exit,
        }
        
        self.reset_callback: Optional[Callable] = None
    
    def set_reset_callback(self, callback: Callable):
        """Set the callback for resetting conversation history."""
        self.reset_callback = callback
    
    def is_command(self, text: str) -> bool:
        """Check if the input is a command."""
        return text.strip().startswith('/')
    
    def process(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Process a command.
        
        Args:
            text: The command text (with or without '/' prefix)
            
        Returns:
            Tuple of (was_command, response)
        """
        text = text.strip()
        
        # Remove '/' prefix if present
        if text.startswith('/'):
            text = text[1:]
        
        parts = text.split(maxsplit=1)
        if not parts:
            return False, None
        
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd in self.commands:
            return True, self.commands[cmd](args)
        
        return False, None
    
    def cmd_help(self, args: str) -> str:
        """Display available commands."""
        help_text = """
╔══════════════════════════════════════════════════════════════╗
║                    JARVIS COMMAND CENTER                      ║
╠══════════════════════════════════════════════════════════════╣
║  /help          - Display this help message                  ║
║  /clear         - Clear the terminal screen                  ║
║  /reset         - Reset conversation history                 ║
║  /time          - Get current time                           ║
║  /date          - Get current date                           ║
║  /open [url]    - Open a URL in browser                      ║
║  /search [query]- Search Google for a query                  ║
║  /exit or /quit - Exit Jarvis                                ║
╚══════════════════════════════════════════════════════════════╝
"""
        return help_text
    
    def cmd_clear(self, args: str) -> str:
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        return "Terminal cleared, Sir."
    
    def cmd_reset(self, args: str) -> str:
        """Reset the conversation history."""
        if self.reset_callback:
            self.reset_callback()
        return "Conversation history has been reset, Sir. Starting fresh."
    
    def cmd_time(self, args: str) -> str:
        """Get the current time."""
        now = datetime.now()
        return f"The current time is {now.strftime('%I:%M %p')}, Sir."
    
    def cmd_date(self, args: str) -> str:
        """Get the current date."""
        now = datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')}, Sir."
    
    def cmd_open(self, args: str) -> str:
        """Open a URL in the browser."""
        if not args:
            return "Please specify a URL to open, Sir."
        
        url = args.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            webbrowser.open(url)
            return f"Opening {url} in your browser, Sir."
        except Exception as e:
            return f"I apologize, Sir. I couldn't open that URL: {e}"
    
    def cmd_search(self, args: str) -> str:
        """Search Google for a query."""
        if not args:
            return "Please provide a search query, Sir."
        
        query = args.strip().replace(' ', '+')
        url = f"https://www.google.com/search?q={query}"
        
        try:
            webbrowser.open(url)
            return f"Searching Google for '{args.strip()}', Sir."
        except Exception as e:
            return f"I apologize, Sir. Search failed: {e}"
    
    def cmd_exit(self, args: str) -> str:
        """Exit Jarvis."""
        print("\n🔵 Goodbye, Sir. JARVIS signing off.\n")
        sys.exit(0)


# Singleton instance
_processor: Optional[CommandProcessor] = None


def get_command_processor() -> CommandProcessor:
    """Get or create the command processor singleton."""
    global _processor
    if _processor is None:
        _processor = CommandProcessor()
    return _processor
