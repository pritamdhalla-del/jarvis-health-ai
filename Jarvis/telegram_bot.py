"""
🤖 Telegram Bot for Jarvis
==========================
Control Jarvis remotely via Telegram messages.
Run this alongside or instead of jarvis.py for remote control.
"""

import asyncio
import tempfile
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from groq_client import get_jarvis_client
from config import TELEGRAM_BOT_TOKEN


class TelegramJarvis:
    """Telegram bot interface for Jarvis."""
    
    def __init__(self):
        self.client = get_jarvis_client()
        self.voice_enabled = True
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        await update.message.reply_text(
            "🔵 *JARVIS Online*\n\n"
            "Good day, Sir. I'm now connected and ready to assist.\n\n"
            "Simply send me a message and I'll help you control your system.\n\n"
            "Commands:\n"
            "/voice - Toggle voice responses\n"
            "/clear - Clear conversation history",
            parse_mode="Markdown"
        )
    
    async def voice_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Toggle voice responses."""
        self.voice_enabled = not self.voice_enabled
        status = "enabled" if self.voice_enabled else "disabled"
        await update.message.reply_text(f"🔊 Voice responses {status}, Sir.")
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Clear conversation history."""
        self.client.clear_history()
        await update.message.reply_text("🔄 Conversation history cleared, Sir.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages."""
        user_message = update.message.text
        
        if not user_message:
            return
        
        # Show typing indicator
        await update.message.chat.send_action("typing")
        
        try:
            # Get response from Jarvis
            response = self.client.chat_with_tools(user_message)
            
            # Send text response
            await update.message.reply_text(f"🔵 {response}")
            
            # Send voice response if enabled
            if self.voice_enabled and response:
                await self._send_voice(update, response)
                
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def _send_voice(self, update: Update, text: str):
        """Generate and send voice message using edge-tts."""
        try:
            import edge_tts
            
            # Create temp file for audio
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                tmp_path = tmp.name
            
            # Generate audio
            communicate = edge_tts.Communicate(
                text,
                "en-US-ChristopherNeural",
                rate="+0%"
            )
            await communicate.save(tmp_path)
            
            # Send voice message
            with open(tmp_path, 'rb') as audio:
                await update.message.reply_voice(audio)
            
            # Cleanup
            os.unlink(tmp_path)
            
        except Exception as e:
            print(f"Voice error: {e}")


def main():
    """Run the Telegram bot."""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not found in .env file!")
        print("Add: TELEGRAM_BOT_TOKEN=your_token_here")
        return
    
    print("🤖 Starting Jarvis Telegram Bot...")
    
    # Create bot instance
    jarvis = TelegramJarvis()
    
    # Build application
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", jarvis.start_command))
    app.add_handler(CommandHandler("voice", jarvis.voice_command))
    app.add_handler(CommandHandler("clear", jarvis.clear_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, jarvis.handle_message))
    
    print("🔵 JARVIS Telegram Bot is online!")
    print("Send a message to your bot to get started.")
    
    # Run the bot
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
