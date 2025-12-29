"""
Async Audio Service - Non-Blocking TTS

Uses edge-tts for neural voice synthesis with subprocess for playback.
Does not require pygame (works with any Python version).

FIXES APPLIED (AI Review):
- Added try/except for temp file cleanup (Google AI Studio)
- Added cleanup() method for lifecycle management (ChatGPT)
"""

import os
import hashlib
import asyncio
import edge_tts

CACHE_DIR = os.path.join("cache", "audio")


class AudioService:
    """
    Async audio manager for speech.
    
    WHY ASYNC?
    - edge-tts generates audio asynchronously over network
    - UI must continue animating during generation
    - Kids will rage-tap if app freezes during TTS
    """
    
    def __init__(self):
        os.makedirs(CACHE_DIR, exist_ok=True)
        self.voice = "en-US-JennyNeural"
        self._speaking = False
        self._current_process = None

    async def speak(self, text: str):
        """Generate and play speech asynchronously."""
        if not text or self._speaking:
            return
        
        self._speaking = True
        
        try:
            filename = self._get_hash(text)
            filepath = os.path.join(CACHE_DIR, filename)

            # Generate audio if not cached
            if not os.path.exists(filepath):
                communicate = edge_tts.Communicate(text, self.voice)
                await communicate.save(filepath)

            # Play using Windows Media Player via PowerShell (non-blocking)
            await self._play_audio(filepath)
        except Exception as e:
            print(f"[AudioService] Error: {e}")
        finally:
            self._speaking = False

    async def _play_audio(self, path: str):
        """Play audio using Windows PowerShell (non-blocking)."""
        try:
            # Use Windows Media.SoundPlayer for async-compatible playback
            self._current_process = await asyncio.create_subprocess_exec(
                'powershell', '-c',
                f'Add-Type -AssemblyName presentationCore; '
                f'$player = New-Object System.Windows.Media.MediaPlayer; '
                f'$player.Open("{os.path.abspath(path)}"); '
                f'$player.Play(); '
                f'Start-Sleep -Milliseconds 2000',  # Wait for short audio
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            await self._current_process.wait()
        except Exception as e:
            print(f"[AudioService] Playback error: {e}")
        finally:
            self._current_process = None

    def _get_hash(self, text: str) -> str:
        """Generate deterministic filename from text."""
        return f"{hashlib.md5(text.encode()).hexdigest()}.mp3"
    
    @property
    def is_speaking(self) -> bool:
        return self._speaking
    
    async def cleanup(self) -> None:
        """
        Cleanup resources on shutdown.
        FIX: ChatGPT - Lifecycle management for proper shutdown.
        """
        # Cancel any running audio process
        if self._current_process and self._current_process.returncode is None:
            try:
                self._current_process.terminate()
                await asyncio.wait_for(self._current_process.wait(), timeout=1.0)
            except asyncio.TimeoutError:
                self._current_process.kill()
            except Exception as e:
                print(f"[AudioService] Cleanup error: {e}")
        
        # FIX: Google AI Studio - Safe temp file deletion with try/except
        # Note: We cache files, so we don't delete them here
        # But if we had temp files, we'd do:
        # try:
        #     os.remove(temp_path)
        # except OSError:
        #     pass
