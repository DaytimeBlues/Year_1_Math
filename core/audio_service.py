"""
Async Audio Service - Unified Channel Mixer & Cache Manager
v2 Architecture: QtMultimedia-only (No PowerShell), LRU Cache, Auto-Ducking.
"""
import os
import hashlib
import asyncio
from typing import Dict, Optional
from pathlib import Path

import edge_tts
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QSoundEffect
from PyQt6.QtCore import QUrl, QObject, pyqtSignal

from core.sfx import get_sfx_path

CACHE_DIR = Path("cache", "audio")
CACHE_CAP_MB = 100
CACHE_MAX_FILES = 200

class AudioCacheManager:
    """
    LRU Cache Eviction Policy.
    Ensures the audio cache doesn't grow indefinitely.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def get_path(self, text: str, voice: str) -> Path:
        """Deterministic path generation."""
        key = hashlib.md5(f"{text}{voice}".encode()).hexdigest()
        return self.base_dir / f"{key}.mp3"
        
    def enforce_limits(self):
        """
        Run eviction loop:
        1. List all files
        2. Sort by access time (oldest first)
        3. Delete until under limits (size & count)
        """
        try:
            files = sorted(
                self.base_dir.glob("*.mp3"),
                key=lambda f: f.stat().st_atime
            )
            
            # Check count limit
            while len(files) > CACHE_MAX_FILES:
                f = files.pop(0)
                try: f.unlink()
                except OSError: pass # File might be in use
            
            # Check size limit
            current_size = sum(f.stat().st_size for f in files)
            while current_size > CACHE_CAP_MB * 1024 * 1024 and files:
                f = files.pop(0)
                size = f.stat().st_size
                try: 
                    f.unlink()
                    current_size -= size
                except OSError: pass
                
        except Exception as e:
            print(f"[AudioCache] Eviction error: {e}")

class AudioService(QObject):
    """
    Unified Audio Mixer.
    Channels:
    - TTS (Priority 1): Voice prompts. Ducks other channels.
    - SFX (Priority 2): UI feedback (clicks, dings).
    - Music (Priority 3): Background ambience.
    """
    
    # Signal to notify when TTS finishes (for sequencing)
    tts_finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.cache = AudioCacheManager(CACHE_DIR)
        self.voice = "en-US-JennyNeural"
        
        # --- Channel Setup ---
        
        # 1. TTS Channel (MediaPlayer for long streaming audio)
        self.tts_player = QMediaPlayer()
        self.tts_output = QAudioOutput()
        self.tts_player.setAudioOutput(self.tts_output)
        self.tts_output.setVolume(1.0)
        
        # 2. SFX Channel (QSoundEffect for low-latency, short clips)
        # We keep a cache of loaded effects to avoid re-loading from disk
        self._loaded_sfx: Dict[str, QSoundEffect] = {}
        
        # 3. Music Channel (MediaPlayer)
        self.music_player = QMediaPlayer()
        self.music_output = QAudioOutput()
        self.music_player.setAudioOutput(self.music_output)
        self.music_output.setVolume(0.3) # Background level
        
        # --- Connections ---
        self.tts_player.mediaStatusChanged.connect(self._on_tts_status)
        
        # Run initial cleanup
        self.cache.enforce_limits()

    async def speak(self, text: str, block: bool = True):
        """
        Generate and play TTS.
        
        Args:
            text: Text to speak
            block: If True, waits for playback to finish before returning.
        """
        if not text: return
        
        # 1. Generate/Get File
        filepath = self.cache.get_path(text, self.voice)
        abs_path = str(filepath.absolute())
        
        if not filepath.exists():
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(abs_path)
            # Trigger eviction check occasionally (e.g., after new write)
            # Performing sync here is safe-ish for file ops on SSD, but could be threaded
            self.cache.enforce_limits()

        # 2. Auto-Duck (Lower volume of other channels)
        self._duck_others(True)
        
        # 3. Play
        self.tts_player.setSource(QUrl.fromLocalFile(abs_path))
        self.tts_player.play()
        
        # 4. Wait if blocking
        if block:
            # We create a future that resolves when media status changes to EndOfMedia
            loop = asyncio.get_event_loop()
            self._current_tts_future = loop.create_future()
            try:
                await self._current_tts_future
            except asyncio.CancelledError:
                self.stop_voice()

    def stop_voice(self):
        """Immediately stops TTS playback (for interruptions)."""
        self.tts_player.stop()
        self._duck_others(False)
        
        # Cancel any pending future
        if hasattr(self, '_current_tts_future') and not self._current_tts_future.done():
            self._current_tts_future.cancel()

    def play_sfx(self, sfx_name: str):
        """
        Fire-and-forget SFX playback.
        Uses QSoundEffect for lowest latency.
        """
        # Load if not ready
        if sfx_name not in self._loaded_sfx:
            path = get_sfx_path(sfx_name)
            if not path or not os.path.exists(path):
                # print(f"[Audio] Missing SFX: {sfx_name}")
                return
            
            effect = QSoundEffect()
            effect.setSource(QUrl.fromLocalFile(path))
            effect.setVolume(0.6) # Standard SFX volume
            self._loaded_sfx[sfx_name] = effect
        
        # Play
        self._loaded_sfx[sfx_name].play()

    def _duck_others(self, active: bool):
        """Lowers music volume when TTS is active."""
        target_vol = 0.1 if active else 0.3
        self.music_output.setVolume(target_vol)

    def _on_tts_status(self, status):
        """Handle TTS playback state changes."""
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self._duck_others(False) # Restore volume
            self.tts_finished.emit()
            
            # Resolve blocking future if exists
            if hasattr(self, '_current_tts_future') and not self._current_tts_future.done():
                try: self._current_tts_future.set_result(True)
                except: pass
        
        elif status == QMediaPlayer.MediaStatus.InvalidMedia:
             print("[Audio] Invalid Media Error")
             self._duck_others(False)
             if hasattr(self, '_current_tts_future') and not self._current_tts_future.done():
                try: self._current_tts_future.set_result(False)
                except: pass
    
    async def cleanup(self) -> None:
        """Lifecycle cleanup."""
        self.tts_player.stop()
        self.music_player.stop()
        for sfx in self._loaded_sfx.values():
            sfx.stop()
