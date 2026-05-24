#!/usr/bin/osascript
tell application "Terminal"
    activate
    do script "cd /Users/anubhavchaturvedi/Documents/Jarvis && source .venv/bin/activate && python jarvis.py"
end tell
