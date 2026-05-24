"""
Voice Module for Jarvis
=======================
Text-to-speech using Microsoft Edge TTS service.
High-quality, natural-sounding voices with streaming playback.
"""

import asyncio
import edge_tts
import subprocess
import os
import tempfile
from typing import Optional
import threading


class JarvisVoice:
    """
    Voice handler for Jarvis using Microsoft Edge TTS.
    Uses streaming for faster response times.
    """
    
    # Popular voice options:
    # en-US-GuyNeural - American male (great for Jarvis)
    # en-GB-RyanNeural - British male
    # en-IN-PrabhatNeural - Indian English male
    # en-AU-WilliamNeural - Australian male
    # en-US-AriaNeural - American female
    
    def __init__(self, voice: str = "en-US-ChristopherNeural"):
        """
        Initialize voice.
        
        Args:
            voice: Edge TTS voice name
        """
        self.voice = voice
        self.rate = "+0%"  # Normal speed
        self.pitch = "+0Hz"  # Pitch adjustment
        self.volume = "+0%"  # Volume adjustment
        self._is_speaking = False
        self._current_process: Optional[subprocess.Popen] = None
        self._stop_event = threading.Event()
    
    def speak(self, text: str, blocking: bool = True):
        """
        Convert text to speech and play it.
        
        Args:
            text: The text to speak
            blocking: If True, wait for speech to complete
        """
        if not text or not text.strip():
            return
        
        self._stop_event.clear()
        
        if blocking:
            self._speak_streaming(text)
        else:
            thread = threading.Thread(target=self._speak_streaming, args=(text,))
            thread.daemon = True
            thread.start()
    
    def _speak_streaming(self, text: str):
        """Stream audio directly to mpv/ffplay for minimal latency."""
        try:
            self._is_speaking = True
            text = text.strip()
            
            # Try streaming with mpv first (lowest latency)
            # Falls back to edge-playback or file-based approach
            if self._try_mpv_stream(text):
                return
            
            # Fallback to file-based approach
            self._speak_file_based(text)
                    
        except Exception as e:
            print(f"Voice error: {e}")
        finally:
            self._is_speaking = False
            self._current_process = None
    
    def _try_mpv_stream(self, text: str) -> bool:
        """Try streaming with mpv for lowest latency."""
        try:
            # Check if mpv is available
            result = subprocess.run(['which', 'mpv'], capture_output=True)
            if result.returncode != 0:
                return False
            
            # Use edge-tts to pipe directly to mpv
            edge_process = subprocess.Popen(
                [
                    'edge-tts',
                    '--voice', self.voice,
                    '--rate', self.rate,
                    '--pitch', self.pitch,
                    '--volume', self.volume,
                    '--text', text,
                    '--write-media', '-'  # Output to stdout
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )
            
            # Pipe to mpv with minimal buffering for fast start
            self._current_process = subprocess.Popen(
                ['mpv', '--no-video', '--really-quiet', '--no-terminal', '-'],
                stdin=edge_process.stdout,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            edge_process.stdout.close()
            self._current_process.wait()
            return True
            
        except Exception:
            return False
    
    def _speak_file_based(self, text: str):
        """Fallback: Generate file then play with afplay."""
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # Generate audio file
            result = subprocess.run(
                [
                    'edge-tts',
                    '--voice', self.voice,
                    '--rate', self.rate,
                    '--pitch', self.pitch,
                    '--volume', self.volume,
                    '--text', text,
                    '--write-media', tmp_path
                ],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"TTS Error: {result.stderr}")
                return
            
            if self._stop_event.is_set():
                return
            
            # Play with afplay (macOS)
            self._current_process = subprocess.Popen(
                ['afplay', tmp_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self._current_process.wait()
            
        finally:
            try:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            except:
                pass
    
    def stop(self):
        """Stop current speech."""
        self._stop_event.set()
        if self._current_process:
            try:
                self._current_process.terminate()
            except:
                pass
        # Kill any running audio processes
        try:
            subprocess.run(['killall', 'afplay'], capture_output=True)
            subprocess.run(['killall', 'mpv'], capture_output=True)
        except:
            pass
    
    def is_speaking(self) -> bool:
        """Check if currently speaking."""
        return self._is_speaking
    
    def set_voice(self, voice: str):
        """Change voice."""
        self.voice = voice
    
    def set_rate(self, rate_percent: int):
        """Set speech rate (-50 to +100)."""
        rate_percent = max(-50, min(100, rate_percent))
        self.rate = f"+{rate_percent}%" if rate_percent >= 0 else f"{rate_percent}%"
    
    def set_pitch(self, pitch_hz: int):
        """Set voice pitch in Hz."""
        self.pitch = f"+{pitch_hz}Hz" if pitch_hz >= 0 else f"{pitch_hz}Hz"
    
    def set_volume(self, volume_percent: int):
        """Set volume adjustment (-50 to +50)."""
        volume_percent = max(-50, min(50, volume_percent))
        self.volume = f"+{volume_percent}%" if volume_percent >= 0 else f"{volume_percent}%"


# Singleton instance
_voice_instance: Optional[JarvisVoice] = None


def get_voice() -> JarvisVoice:
    """Get or create the voice handler singleton."""
    global _voice_instance
    if _voice_instance is None:
        _voice_instance = JarvisVoice()
    return _voice_instance


def speak(text: str, blocking: bool = True):
    """Quick speak function."""
    get_voice().speak(text, blocking)


async def list_voices():
    """List all available Edge TTS voices."""
    voices = await edge_tts.list_voices()
    return voices
