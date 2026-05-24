# 🔵 JARVIS - Just A Rather Very Intelligent System

A personal AI assistant powered by the Groq API with the personality of Tony Stark's JARVIS.

## Features

- **Intelligent Conversations** - Powered by Llama 3.1 via Groq API
- **Conversation Memory** - Maintains context across your chat session
- **Streaming Responses** - Real-time character-by-character output
- **Voice Mode** - Optional speech recognition and text-to-speech
- **System Commands** - Built-in commands for common tasks
- **Beautiful Terminal UI** - Styled output with colors and formatting

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Jarvis

**Text Mode (default):**

```bash
python jarvis.py
```

**Voice Mode (requires microphone):**

```bash
python jarvis.py --voice
```

## Commands

| Command           | Description                 |
| ----------------- | --------------------------- |
| `/help`           | Show all available commands |
| `/clear`          | Clear the terminal screen   |
| `/reset`          | Clear conversation history  |
| `/time`           | Get current time            |
| `/date`           | Get current date            |
| `/open [url]`     | Open a URL in browser       |
| `/search [query]` | Search Google               |
| `/exit`           | Exit Jarvis                 |

## Project Structure

```
Jarvis/
├── jarvis.py        # Main application entry point
├── config.py        # Configuration and settings
├── groq_client.py   # Groq API client wrapper
├── commands.py      # Command processor
├── voice.py         # Voice I/O module
├── requirements.txt # Python dependencies
├── .env             # API key (not in git)
└── README.md        # This file
```

## Configuration

Edit `config.py` to customize:

- **MODEL_NAME** - The Groq model to use
- **TEMPERATURE** - Response creativity (0.0 - 1.0)
- **MAX_TOKENS** - Maximum response length
- **JARVIS_SYSTEM_PROMPT** - Jarvis's personality

## Voice Mode Notes

Voice mode requires:

- `pyttsx3` for text-to-speech
- `SpeechRecognition` for voice input
- `PyAudio` for microphone access

On macOS, you may need to install portaudio:

```bash
brew install portaudio
pip install pyaudio
```

## Powered By

- **Groq** - Ultra-fast LLM inference
- **Llama 3.1** - Meta's powerful open-source LLM
