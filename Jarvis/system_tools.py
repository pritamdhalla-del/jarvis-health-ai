"""
System Tools Module for Jarvis
==============================
Provides advanced system control - file browsing, app control, system commands.
"""

import os
import subprocess
import platform
import shutil
import glob
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import json


class SystemTools:
    """System tools for complete Mac control."""
    
    def __init__(self):
        self.home_dir = Path.home()
        self.current_dir = self.home_dir
        self.apps_cache: Optional[List[str]] = None
        
    # ==================== Application Control ====================
    
    def get_installed_apps(self) -> List[str]:
        """Get list of all installed applications."""
        if self.apps_cache:
            return self.apps_cache
        
        apps = []
        app_dirs = [
            "/Applications",
            "/System/Applications",
            str(self.home_dir / "Applications"),
            "/System/Applications/Utilities"
        ]
        
        for app_dir in app_dirs:
            if os.path.exists(app_dir):
                for item in os.listdir(app_dir):
                    if item.endswith('.app'):
                        apps.append(item.replace('.app', ''))
        
        self.apps_cache = sorted(set(apps))
        return self.apps_cache
    
    def find_app(self, query: str) -> Optional[str]:
        """Find an app by partial name match."""
        apps = self.get_installed_apps()
        query_lower = query.lower()
        
        # Exact match first
        for app in apps:
            if app.lower() == query_lower:
                return app
        
        # Partial match
        for app in apps:
            if query_lower in app.lower():
                return app
        
        # Common aliases
        aliases = {
            'chrome': 'Google Chrome',
            'firefox': 'Firefox',
            'safari': 'Safari',
            'code': 'Visual Studio Code',
            'vscode': 'Visual Studio Code',
            'antigravity': 'Antigravity',
            'slack': 'Slack',
            'discord': 'Discord',
            'spotify': 'Spotify',
            'telegram': 'Telegram',
            'whatsapp': 'WhatsApp',
            'finder': 'Finder',
            'terminal': 'Terminal',
            'iterm': 'iTerm',
            'notes': 'Notes',
            'calendar': 'Calendar',
            'mail': 'Mail',
            'photos': 'Photos',
            'music': 'Music',
            'messages': 'Messages',
            'facetime': 'FaceTime',
            'settings': 'System Preferences',
            'preferences': 'System Preferences',
            'word': 'Microsoft Word',
            'excel': 'Microsoft Excel',
            'powerpoint': 'Microsoft PowerPoint',
            'photoshop': 'Adobe Photoshop',
            'premiere': 'Adobe Premiere Pro',
            'figma': 'Figma',
            'notion': 'Notion',
            'zoom': 'zoom.us',
            'teams': 'Microsoft Teams',
        }
        
        if query_lower in aliases:
            return aliases[query_lower]
        
        return None
    
    def open_application(self, app_name: str) -> Dict:
        """Open an application by name (smart matching)."""
        try:
            # Find the actual app name
            actual_app = self.find_app(app_name)
            
            if actual_app:
                result = subprocess.run(
                    ['open', '-a', actual_app],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return {"success": True, "opened": actual_app}
                else:
                    return {"success": False, "error": result.stderr}
            
            # Try direct open as fallback
            result = subprocess.run(
                ['open', '-a', app_name],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return {"success": True, "opened": app_name}
            
            # List similar apps
            apps = self.get_installed_apps()
            similar = [a for a in apps if app_name.lower() in a.lower()][:5]
            
            return {
                "success": False, 
                "error": f"App '{app_name}' not found",
                "similar_apps": similar
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def close_application(self, app_name: str) -> Dict:
        """Close an application."""
        try:
            actual_app = self.find_app(app_name) or app_name
            
            # Use AppleScript to quit gracefully
            script = f'tell application "{actual_app}" to quit'
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return {"success": True, "closed": actual_app}
            else:
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            return {"error": str(e)}
    
    def list_running_apps(self) -> Dict:
        """List currently running applications."""
        try:
            script = '''
            tell application "System Events"
                set appList to name of every process whose background only is false
            end tell
            return appList
            '''
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                apps = [a.strip() for a in result.stdout.strip().split(',')]
                return {"running_apps": apps, "count": len(apps)}
            else:
                return {"error": result.stderr}
                
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== System Controls ====================
    
    def set_volume(self, level: int) -> Dict:
        """Set system volume (0-100)."""
        try:
            level = max(0, min(100, level))
            # Convert to 0-7 scale for macOS
            mac_level = int(level * 7 / 100)
            
            subprocess.run(
                ['osascript', '-e', f'set volume output volume {level}'],
                capture_output=True
            )
            return {"success": True, "volume": level}
        except Exception as e:
            return {"error": str(e)}
    
    def get_volume(self) -> Dict:
        """Get current system volume."""
        try:
            result = subprocess.run(
                ['osascript', '-e', 'output volume of (get volume settings)'],
                capture_output=True,
                text=True
            )
            volume = int(result.stdout.strip())
            return {"volume": volume}
        except Exception as e:
            return {"error": str(e)}
    
    def mute(self) -> Dict:
        """Mute system audio."""
        try:
            subprocess.run(['osascript', '-e', 'set volume with output muted'], capture_output=True)
            return {"success": True, "muted": True}
        except Exception as e:
            return {"error": str(e)}
    
    def unmute(self) -> Dict:
        """Unmute system audio."""
        try:
            subprocess.run(['osascript', '-e', 'set volume without output muted'], capture_output=True)
            return {"success": True, "muted": False}
        except Exception as e:
            return {"error": str(e)}
    
    def take_screenshot(self, filename: str = None) -> Dict:
        """Take a screenshot."""
        try:
            if not filename:
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            filepath = str(self.home_dir / "Desktop" / filename)
            
            subprocess.run(['screencapture', '-x', filepath], capture_output=True)
            
            if os.path.exists(filepath):
                return {"success": True, "saved_to": filepath}
            else:
                return {"error": "Screenshot failed"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def sleep_display(self) -> Dict:
        """Put display to sleep."""
        try:
            subprocess.run(['pmset', 'displaysleepnow'], capture_output=True)
            return {"success": True, "message": "Display sleeping"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_battery_status(self) -> Dict:
        """Get battery status."""
        try:
            result = subprocess.run(
                ['pmset', '-g', 'batt'],
                capture_output=True,
                text=True
            )
            output = result.stdout
            
            # Parse battery percentage
            import re
            match = re.search(r'(\d+)%', output)
            percentage = int(match.group(1)) if match else None
            
            charging = 'charging' in output.lower() or 'ac power' in output.lower()
            
            return {
                "percentage": percentage,
                "charging": charging,
                "raw": output.strip()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def empty_trash(self) -> Dict:
        """Empty the trash."""
        try:
            script = '''
            tell application "Finder"
                empty trash
            end tell
            '''
            subprocess.run(['osascript', '-e', script], capture_output=True)
            return {"success": True, "message": "Trash emptied"}
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== File System Operations ====================
    
    def list_directory(self, path: str = ".") -> Dict:
        """List contents of a directory."""
        try:
            target_path = self._resolve_path(path)
            
            if not target_path.exists():
                return {"error": f"Path does not exist: {target_path}"}
            
            if not target_path.is_dir():
                return {"error": f"Not a directory: {target_path}"}
            
            files = []
            folders = []
            
            for item in sorted(target_path.iterdir()):
                if item.name.startswith('.'):
                    continue
                    
                if item.is_dir():
                    folders.append(item.name)
                else:
                    size = item.stat().st_size
                    files.append({"name": item.name, "size": self._format_size(size)})
            
            return {
                "path": str(target_path),
                "folders": folders,
                "files": files,
                "total_items": len(files) + len(folders)
            }
            
        except PermissionError:
            return {"error": f"Permission denied: {path}"}
        except Exception as e:
            return {"error": str(e)}
    
    def search_files(self, pattern: str, search_path: str = "~") -> Dict:
        """Search for files matching a pattern."""
        try:
            base_path = self._resolve_path(search_path)
            
            if "*" not in pattern:
                pattern = f"*{pattern}*"
            
            matches = []
            search_pattern = str(base_path / "**" / pattern)
            
            for match in glob.iglob(search_pattern, recursive=True):
                match_path = Path(match)
                if not any(part.startswith('.') for part in match_path.parts):
                    matches.append({
                        "path": str(match),
                        "name": match_path.name,
                        "type": "folder" if match_path.is_dir() else "file"
                    })
                
                if len(matches) >= 30:
                    break
            
            return {
                "pattern": pattern,
                "matches": matches,
                "count": len(matches)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def find_folder(self, folder_name: str, search_path: str = "~") -> Dict:
        """Find a specific folder by name."""
        try:
            base_path = self._resolve_path(search_path)
            found = []
            
            for root, dirs, files in os.walk(base_path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for d in dirs:
                    if folder_name.lower() in d.lower():
                        full_path = Path(root) / d
                        found.append({
                            "name": d,
                            "path": str(full_path),
                            "exact_match": d.lower() == folder_name.lower()
                        })
                
                if len(found) >= 10:
                    break
            
            return {"found": found, "count": len(found)}
            
        except Exception as e:
            return {"error": str(e)}
    
    def read_file(self, file_path: str, max_lines: int = 50) -> Dict:
        """Read contents of a file."""
        try:
            path = self._resolve_path(file_path)
            
            if not path.exists():
                return {"error": f"File does not exist: {path}"}
            
            if path.stat().st_size > 500 * 1024:  # 500KB limit
                return {"error": "File too large"}
            
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()[:max_lines]
                content = ''.join(lines)
            
            return {"content": content, "lines_read": len(lines)}
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_file_info(self, file_path: str) -> Dict:
        """Get info about a file or folder."""
        try:
            path = self._resolve_path(file_path)
            
            if not path.exists():
                return {"error": f"Path does not exist: {path}"}
            
            stat = path.stat()
            
            return {
                "name": path.name,
                "type": "folder" if path.is_dir() else "file",
                "size": self._format_size(stat.st_size),
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def run_command(self, command: str, timeout: int = 30) -> Dict:
        """Execute a shell command."""
        dangerous = ['rm -rf /', 'mkfs', ':(){:|:&};:']
        for d in dangerous:
            if d in command:
                return {"error": "Dangerous command blocked"}
        
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                timeout=timeout, cwd=str(self.current_dir)
            )
            
            return {
                "stdout": result.stdout[:3000] if result.stdout else "",
                "stderr": result.stderr[:500] if result.stderr else "",
                "success": result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_system_info(self) -> Dict:
        """Get system information."""
        return {
            "os": f"{platform.system()} {platform.mac_ver()[0]}",
            "machine": platform.machine(),
            "hostname": platform.node(),
            "home": str(self.home_dir)
        }
    
    def open_url(self, url: str) -> Dict:
        """Open a URL in the default browser."""
        import webbrowser
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            webbrowser.open(url)
            return {"success": True, "url": url}
        except Exception as e:
            return {"error": str(e)}
    
    def open_urls(self, urls: List[str]) -> Dict:
        """Open multiple URLs in Chrome tabs."""
        try:
            results = []
            for url in urls:
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                
                # Open in Chrome using AppleScript
                script = f'''
                tell application "Google Chrome"
                    activate
                    open location "{url}"
                end tell
                '''
                subprocess.run(['osascript', '-e', script], capture_output=True)
                results.append(url)
            
            return {"success": True, "opened": results, "count": len(results)}
        except Exception as e:
            return {"error": str(e)}
    
    def list_chrome_tabs(self) -> Dict:
        """List all open tabs in Chrome."""
        try:
            script = '''
            tell application "Google Chrome"
                set tabInfo to ""
                set windowCount to count of windows
                repeat with w from 1 to windowCount
                    set tabCount to count of tabs of window w
                    repeat with t from 1 to tabCount
                        set tabTitle to title of tab t of window w
                        set tabUrl to URL of tab t of window w
                        set tabInfo to tabInfo & w & ":::" & t & ":::" & tabTitle & ":::" & tabUrl & "
"
                    end repeat
                end repeat
                return tabInfo
            end tell
            '''
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {"error": result.stderr}
            
            tabs = []
            for line in result.stdout.strip().split('\n'):
                if line and ':::' in line:
                    parts = line.split(':::')
                    if len(parts) >= 4:
                        tabs.append({
                            "window": int(parts[0]),
                            "tab": int(parts[1]),
                            "title": parts[2],
                            "url": parts[3]
                        })
            
            return {"tabs": tabs, "count": len(tabs)}
            
        except Exception as e:
            return {"error": str(e)}
    
    def close_chrome_tab(self, tab_identifier: str) -> Dict:
        """Close a Chrome tab by title or URL match."""
        try:
            # First get all tabs
            tabs_result = self.list_chrome_tabs()
            if "error" in tabs_result:
                return tabs_result
            
            tabs = tabs_result.get("tabs", [])
            identifier_lower = tab_identifier.lower()
            
            # Find matching tab
            for tab in tabs:
                title_match = identifier_lower in tab["title"].lower()
                url_match = identifier_lower in tab["url"].lower()
                
                if title_match or url_match:
                    # Close this specific tab
                    script = f'''
                    tell application "Google Chrome"
                        close tab {tab["tab"]} of window {tab["window"]}
                    end tell
                    '''
                    result = subprocess.run(
                        ['osascript', '-e', script],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        return {"success": True, "closed": tab["title"], "url": tab["url"]}
                    else:
                        return {"success": False, "error": result.stderr}
            
            return {"success": False, "error": f"No tab found matching '{tab_identifier}'"}
            
        except Exception as e:
            return {"error": str(e)}
    
    def close_chrome_tabs(self, tabs: List[str]) -> Dict:
        """Close multiple Chrome tabs by title or URL match."""
        try:
            closed = []
            failed = []
            
            for tab_id in tabs:
                result = self.close_chrome_tab(tab_id)
                if result.get("success"):
                    closed.append(result.get("closed", tab_id))
                else:
                    failed.append(tab_id)
            
            return {
                "success": len(closed) > 0,
                "closed": closed,
                "failed": failed,
                "count": len(closed)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def scroll_chrome(self, direction: str = "down", amount: int = 300) -> Dict:
        """Scroll in Chrome. Direction: up, down, left, right, top, bottom."""
        try:
            scroll_map = {
                "up": f"window.scrollBy(0, -{amount})",
                "down": f"window.scrollBy(0, {amount})",
                "left": f"window.scrollBy(-{amount}, 0)",
                "right": f"window.scrollBy({amount}, 0)",
                "top": "window.scrollTo(0, 0)",
                "bottom": "window.scrollTo(0, document.body.scrollHeight)"
            }
            
            js_code = scroll_map.get(direction.lower(), scroll_map["down"])
            
            script = f'''
            tell application "Google Chrome"
                execute front window's active tab javascript "{js_code}"
            end tell
            '''
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            
            return {"success": result.returncode == 0, "scrolled": direction}
        except Exception as e:
            return {"error": str(e)}
    
    def chrome_navigate(self, action: str) -> Dict:
        """Navigate in Chrome: back, forward, refresh, or URL."""
        try:
            if action.lower() == "back":
                script = 'tell application "Google Chrome" to execute front window\'s active tab javascript "history.back()"'
            elif action.lower() == "forward":
                script = 'tell application "Google Chrome" to execute front window\'s active tab javascript "history.forward()"'
            elif action.lower() in ["refresh", "reload"]:
                script = 'tell application "Google Chrome" to reload active tab of front window'
            else:
                # Treat as URL
                url = action if action.startswith(('http://', 'https://')) else f'https://{action}'
                script = f'tell application "Google Chrome" to set URL of active tab of front window to "{url}"'
            
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            return {"success": result.returncode == 0, "action": action}
        except Exception as e:
            return {"error": str(e)}
    
    def type_in_chrome(self, text: str) -> Dict:
        """Type text into the active element in Chrome."""
        try:
            # Escape special characters for AppleScript
            escaped_text = text.replace('\\', '\\\\').replace('"', '\\"')
            
            script = f'''
            tell application "System Events"
                tell process "Google Chrome"
                    keystroke "{escaped_text}"
                end tell
            end tell
            '''
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            return {"success": result.returncode == 0, "typed": text}
        except Exception as e:
            return {"error": str(e)}
    
    def chrome_keypress(self, key: str) -> Dict:
        """Press a key in Chrome: enter, escape, tab, space, etc."""
        try:
            key_codes = {
                "enter": "return",
                "escape": "escape", 
                "esc": "escape",
                "tab": "tab",
                "space": "space",
                "delete": "delete",
                "backspace": "delete",
                "up": "up arrow",
                "down": "down arrow",
                "left": "left arrow",
                "right": "right arrow"
            }
            
            key_name = key_codes.get(key.lower(), key.lower())
            
            script = f'''
            tell application "System Events"
                tell process "Google Chrome"
                    key code {self._get_key_code(key_name)}
                end tell
            end tell
            '''
            
            # Alternative: use keystroke for simple keys
            if key_name in ["return", "escape", "tab", "space", "delete"]:
                script = f'''
                tell application "System Events"
                    tell process "Google Chrome"
                        keystroke {key_name}
                    end tell
                end tell
                '''
            
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            return {"success": result.returncode == 0, "key": key}
        except Exception as e:
            return {"error": str(e)}
    
    def _get_key_code(self, key: str) -> int:
        """Get macOS key code for a key."""
        codes = {
            "return": 36, "escape": 53, "tab": 48, "space": 49,
            "delete": 51, "up arrow": 126, "down arrow": 125,
            "left arrow": 123, "right arrow": 124
        }
        return codes.get(key, 36)
    
    def youtube_search(self, query: str) -> Dict:
        """Open YouTube and search for a query."""
        try:
            encoded_query = query.replace(' ', '+')
            url = f"https://www.youtube.com/results?search_query={encoded_query}"
            
            script = f'''
            tell application "Google Chrome"
                activate
                open location "{url}"
            end tell
            '''
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            return {"success": result.returncode == 0, "searched": query}
        except Exception as e:
            return {"error": str(e)}
    
    def youtube_control(self, action: str) -> Dict:
        """Control YouTube video: play, pause, mute, unmute, fullscreen, skip."""
        try:
            js_commands = {
                "play": "document.querySelector('video').play()",
                "pause": "document.querySelector('video').pause()",
                "toggle": "var v=document.querySelector('video'); v.paused ? v.play() : v.pause()",
                "mute": "document.querySelector('video').muted = true",
                "unmute": "document.querySelector('video').muted = false",
                "fullscreen": "document.querySelector('video').requestFullscreen()",
                "skip": "document.querySelector('video').currentTime += 10",
                "rewind": "document.querySelector('video').currentTime -= 10",
                "volumeup": "var v=document.querySelector('video'); v.volume = Math.min(1, v.volume + 0.1)",
                "volumedown": "var v=document.querySelector('video'); v.volume = Math.max(0, v.volume - 0.1)"
            }
            
            js_code = js_commands.get(action.lower().replace(" ", ""), js_commands.get("toggle"))
            
            script = f'''
            tell application "Google Chrome"
                execute front window's active tab javascript "{js_code}"
            end tell
            '''
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            return {"success": result.returncode == 0, "action": action}
        except Exception as e:
            return {"error": str(e)}
    
    def chrome_zoom(self, action: str) -> Dict:
        """Zoom in/out/reset in Chrome."""
        try:
            if action.lower() == "in":
                script = '''
                tell application "System Events"
                    tell process "Google Chrome"
                        keystroke "+" using command down
                    end tell
                end tell
                '''
            elif action.lower() == "out":
                script = '''
                tell application "System Events"
                    tell process "Google Chrome"
                        keystroke "-" using command down
                    end tell
                end tell
                '''
            else:  # reset
                script = '''
                tell application "System Events"
                    tell process "Google Chrome"
                        keystroke "0" using command down
                    end tell
                end tell
                '''
            
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            return {"success": result.returncode == 0, "zoom": action}
        except Exception as e:
            return {"error": str(e)}
    
    def open_file(self, file_path: str) -> Dict:
        """Open a file with the default application."""
        try:
            path = self._resolve_path(file_path)
            
            if not path.exists():
                return {"error": f"File not found: {path}"}
            
            subprocess.run(["open", str(path)])
            return {"success": True, "opened": str(path)}
            
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== Helpers ====================
    
    def _resolve_path(self, path: str) -> Path:
        path = os.path.expanduser(path)
        path_obj = Path(path)
        if not path_obj.is_absolute():
            path_obj = self.current_dir / path_obj
        return path_obj.resolve()
    
    def _format_size(self, size: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


# Singleton
_tools: Optional[SystemTools] = None

def get_system_tools() -> SystemTools:
    global _tools
    if _tools is None:
        _tools = SystemTools()
    return _tools


def execute_tool(tool_name: str, arguments: Dict) -> str:
    """Execute a tool and return JSON result."""
    tools = get_system_tools()
    
    tool_map = {
        "list_directory": lambda d: tools.list_directory(d.get("path", "~")),
        "find_folder": lambda d: tools.find_folder(d.get("folder_name", ""), d.get("search_path", "~")),
        "search_files": lambda d: tools.search_files(d.get("pattern", "*"), d.get("search_path", "~")),
        "read_file": lambda d: tools.read_file(d.get("file_path", "")),
        "get_file_info": lambda d: tools.get_file_info(d.get("file_path", "")),
        "run_command": lambda d: tools.run_command(d.get("command", "")),
        "get_system_info": lambda d: tools.get_system_info(),
        "open_application": lambda d: tools.open_application(d.get("app_name", "")),
        "close_application": lambda d: tools.close_application(d.get("app_name", "")),
        "list_running_apps": lambda d: tools.list_running_apps(),
        "open_url": lambda d: tools.open_url(d.get("url", "")),
        "open_urls": lambda d: tools.open_urls(d.get("urls", [])),
        "list_chrome_tabs": lambda d: tools.list_chrome_tabs(),
        "close_chrome_tab": lambda d: tools.close_chrome_tab(d.get("tab", "")),
        "close_chrome_tabs": lambda d: tools.close_chrome_tabs(d.get("tabs", [])),
        "scroll_chrome": lambda d: tools.scroll_chrome(d.get("direction", "down"), d.get("amount", 300)),
        "chrome_navigate": lambda d: tools.chrome_navigate(d.get("action", "")),
        "type_in_chrome": lambda d: tools.type_in_chrome(d.get("text", "")),
        "chrome_keypress": lambda d: tools.chrome_keypress(d.get("key", "enter")),
        "youtube_search": lambda d: tools.youtube_search(d.get("query", "")),
        "youtube_control": lambda d: tools.youtube_control(d.get("action", "toggle")),
        "chrome_zoom": lambda d: tools.chrome_zoom(d.get("action", "in")),
        "open_file": lambda d: tools.open_file(d.get("file_path", "")),
        "set_volume": lambda d: tools.set_volume(d.get("level", 50)),
        "get_volume": lambda d: tools.get_volume(),
        "mute": lambda d: tools.mute(),
        "unmute": lambda d: tools.unmute(),
        "take_screenshot": lambda d: tools.take_screenshot(d.get("filename")),
        "get_battery_status": lambda d: tools.get_battery_status(),
        "empty_trash": lambda d: tools.empty_trash(),
        "sleep_display": lambda d: tools.sleep_display(),
    }
    
    if tool_name not in tool_map:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
    
    result = tool_map[tool_name](arguments)
    return json.dumps(result, indent=2)
