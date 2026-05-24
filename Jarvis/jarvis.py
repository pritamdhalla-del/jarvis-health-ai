"""
🔵 JARVIS - Just A Rather Very Intelligent System
==================================================
Your personal AI assistant powered by Groq with system control and voice.

Usage:
    python jarvis.py           # Text mode
    python jarvis.py --voice   # Voice mode with TTS
"""

import sys
import argparse
from groq_client import get_jarvis_client, JarvisGroqClient
from commands import get_command_processor, CommandProcessor


# Terminal colors
class C:
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'


def banner():
    print(f"""
{C.BLUE}{C.BOLD}
    ╔═══════════════════════════════════════════════════════════════╗
    ║        ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗               ║
    ║        ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝               ║
    ║        ██║███████║██████╔╝██║   ██║██║███████╗               ║
    ║   ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║               ║
    ║   ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║               ║
    ║    ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝               ║
    ║                                                               ║
    ║         Just A Rather Very Intelligent System                 ║
    ╚═══════════════════════════════════════════════════════════════╝
{C.RESET}""")


def run_text_mode(client: JarvisGroqClient, processor: CommandProcessor):
    """Text-only mode."""
    processor.set_reset_callback(client.clear_history)
    
    print(f"\n{C.BLUE}🔵 JARVIS:{C.RESET} Good day, Sir. How may I help you?")
    
    while True:
        try:
            user_input = input(f"\n{C.GREEN}You:{C.RESET} ").strip()
            
            if not user_input:
                continue
            
            # Check commands
            is_cmd, cmd_response = processor.process(user_input)
            if is_cmd:
                if cmd_response:
                    print(f"\n{C.BLUE}🔵 JARVIS:{C.RESET} {cmd_response}")
                continue
            
            # Tool callback
            def on_tool(name, args):
                args_str = ", ".join(f"{k}={v}" for k, v in args.items())
                print(f"\n{C.MAGENTA}⚙️  {name}({args_str}){C.RESET}")
            
            # Get response
            response = client.chat_with_tools(user_input, on_tool)
            print(f"\n{C.BLUE}🔵 JARVIS:{C.RESET} {response}")
            
        except KeyboardInterrupt:
            print(f"\n\n{C.BLUE}🔵 JARVIS:{C.RESET} Goodbye, Sir.\n")
            break
        except Exception as e:
            print(f"\n{C.RED}Error: {e}{C.RESET}")


def run_voice_mode(client: JarvisGroqClient, processor: CommandProcessor):
    """Voice mode with TTS."""
    try:
        from voice import get_voice
        voice = get_voice()
    except Exception as e:
        print(f"{C.RED}Voice unavailable: {e}{C.RESET}")
        run_text_mode(client, processor)
        return
    
    processor.set_reset_callback(client.clear_history)
    
    greeting = "Good day, Sir. How may I help you?"
    print(f"\n{C.BLUE}🔵 JARVIS:{C.RESET} {greeting}")
    voice.speak(greeting)
    
    print(f"\n{C.CYAN}🎤 Voice mode active. Type or speak your commands.{C.RESET}")
    
    while True:
        try:
            user_input = input(f"\n{C.GREEN}You:{C.RESET} ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                goodbye = "Goodbye, Sir."
                print(f"\n{C.BLUE}🔵 JARVIS:{C.RESET} {goodbye}")
                voice.speak(goodbye)
                break
            
            # Tool callback
            def on_tool(name, args):
                args_str = ", ".join(f"{k}={v}" for k, v in args.items())
                print(f"\n{C.MAGENTA}⚙️  {name}({args_str}){C.RESET}")
            
            # Get response
            response = client.chat_with_tools(user_input, on_tool)
            print(f"\n{C.BLUE}🔵 JARVIS:{C.RESET} {response}")
            
            # Speak response
            voice.speak(response)
            
        except KeyboardInterrupt:
            print(f"\n\n{C.BLUE}🔵 JARVIS:{C.RESET} Goodbye, Sir.\n")
            break
        except Exception as e:
            print(f"\n{C.RED}Error: {e}{C.RESET}")


def main():
    parser = argparse.ArgumentParser(description='JARVIS AI Assistant')
    parser.add_argument('--no-voice', action='store_true', help='Disable voice output')
    args = parser.parse_args()
    
    banner()
    
    try:
        client = get_jarvis_client()
        processor = get_command_processor()
        
        if args.no_voice:
            run_text_mode(client, processor)
        else:
            run_voice_mode(client, processor)
            
    except ValueError as e:
        print(f"{C.RED}Config Error: {e}{C.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{C.RED}Error: {e}{C.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
