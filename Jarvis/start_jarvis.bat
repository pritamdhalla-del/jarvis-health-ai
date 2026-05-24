@echo off

echo Starting JARVIS AI SYSTEM...

REM START BACKEND AI
start cmd /k "cd /d C:\Users\pande\Downloads\Jarvis\Jarvis && python -m uvicorn backend:app --reload"

timeout /t 3

REM START VISION AI
start cmd /k "cd /d C:\Users\pande\Downloads\Jarvis\Jarvis && python -m uvicorn vision_api:app --reload --port 8001"

timeout /t 3

REM START REACT UI
start cmd /k "cd /d C:\Users\pande\Downloads\Jarvis\jarvis-ui && npm run dev"

timeout /t 10

REM OPEN BROWSER
start http://localhost:3000

echo JARVIS SYSTEM ONLINE