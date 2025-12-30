"""
Async Audio Service - Unified Channel Mixer & Cache Manager
v3 Architecture: Thread-safe with race condition fixes.

FIXES APPLIED (DeepSeek Review):
- Narrow lock scope to avoid UI freeze during TTS playback
- Qt.QueuedConnection for thread-safe _on_tts_status
- Proper future cleanup with done callbacks
- subprocess-based TTS generation (avoids nested event loops)
"""
import os
import hashlib
import asyncio
import subprocess
import shutil
from typing import Dict, Optional, Set
from pathlib import Path
from collections import OrderedDict

from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QSoundEffect
from PyQt6.QtCore import QUrl, QObject, pyqtSignal, pyqtSlot, Qt, QMetaObject

from core.sfx import get_sfx_path

CACHE_DIR = Path("cache", "audio")
CACHE_CAP_MB = 100
CACHE_MAX_FILES = 200
TTS_TIMEOUT_SECONDS = 15
SFX_CACHE_MAX = 20


class AudioCacheManager:
    """LRU Cache Eviction Policy."""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def get_path(self, text: str, voice: str) -> Path:
        key = hashlib.md5(f"{text}{voice}".encode()).hexdigest()
        return self.base_dir / f"{key}.mp3"
        
    async def enforce_limits_async(self):
        """Run eviction in thread to avoid blocking UI."""
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._enforce_limits_sync)
    
    def _enforce_limits_sync(self):
        """Safe file eviction with per-file error handling."""
        try:
            files = []
            for f in self.base_dir.glob("*.mp3"):
                try:
                    stat = f.stat()
                    files.append((f, stat.st_atime, stat.st_size))
                except (OSError, FileNotFoundError):
                    continue
            
            files.sort(key=lambda x: x[1])  # Sort by access time
            
            # Check count limit
            while len(files) > CACHE_MAX_FILES:
                f, _, _ = files.pop(0)
                try:
                    f.unlink()
                    print(f"[AudioCache] Evicted: {f.name}")
                except OSError as e:
                    print(f"[AudioCache] Eviction failed: {e}")
            
            # Check size limit
            current_size = sum(size for _, _, size in files)
            while current_size > CACHE_CAP_MB * 1024 * 1024 and files:
                f, _, size = files.pop(0)
                try:
                    f.unlink()
                    current_size -= size
                    print(f"[AudioCache] Evicted (size): {f.name}")
                except OSError as e:
                    print(f"[AudioCache] Eviction failed: {e}")
                    
        except Exception as e:
            print(f"[AudioCache] Eviction error: {e}")


class SFXCache:
    """LRU cache for SFX to prevent memory leaks."""
    
    def __init__(self, max_size: int = SFX_CACHE_MAX):
        self._cache: OrderedDict[str, QSoundEffect] = OrderedDict()
        self._max_size = max_size
    
    def get(self, name: str) -> Optional[QSoundEffect]:
        if name in self._cache:
            # Move to end (most recently used)
            effect = self._cache.pop(name)
            self._cache[name] = effect
            return effect
        
        # Load new effect
        path = get_sfx_path(name)
        if not path or not os.path.exists(path):
            return None
        
        effect = QSoundEffect()
        effect.setSource(QUrl.fromLocalFile(path))
        effect.setVolume(0.6)
        
        self._cache[name] = effect
        
        # Enforce size limit
        if len(self._cache) > self._max_size:
            _, old_effect = self._cache.popitem(last=False)
            old_effect.stop()
            old_effect.deleteLater()
        
        return effect


class AudioService(QObject):
    """
    Thread-safe audio service with proper race condition handling.
    
    FIXES (DeepSeek Review):
    1. Lock only covers critical setup, not playback
    2. Qt.QueuedConnection for thread-safe signal handling
    3. Subprocess-based TTS generation (no nested event loops)
    4. LRU cache for SFX to prevent memory leaks
    """
    
    tts_finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cache = AudioCacheManager(CACHE_DIR)
        self.voice = "en-US-JennyNeural"
        
        # Race condition protection
        self._speak_lock = asyncio.Lock()
        self._current_tts_future: Optional[asyncio.Future] = None
        self._tts_futures: Set[asyncio.Future] = set()
        
        # TTS Channel
        self.tts_player = QMediaPlayer()
        self.tts_output = QAudioOutput()
        self.tts_player.setAudioOutput(self.tts_output)
        self.tts_output.setVolume(1.0)
        
        # SFX Channel (LRU cached)
        self._sfx_cache = SFXCache()
        
        # Music Channel
        self.music_player = QMediaPlayer()
        self.music_output = QAudioOutput()
        self.music_player.setAudioOutput(self.music_output)
        self.music_output.setVolume(0.3)
        
        # Thread-safe signal connection (DeepSeek fix)
        self.tts_player.mediaStatusChanged.connect(
            self._on_tts_status, Qt.ConnectionType.QueuedConnection
        )
        
        # Initial cleanup (non-blocking)
        asyncio.get_event_loop().call_soon(
            lambda: asyncio.create_task(self.cache.enforce_limits_async())
        )

    async def speak(self, text: str, block: bool = True):
        """
        Speak text with proper race condition protection.
        
        CRITICAL FIX (DeepSeek): Lock only covers setup, not playback.
        This prevents UI freeze during TTS.
        """
        if not text:
            return
        
        future = None
        
        # LOCK: Only for critical setup section
        async with self._speak_lock:
            # Cancel any ongoing speech
            if self._current_tts_future and not self._current_tts_future.done():
                self._current_tts_future.cancel()
            
            # Get or generate TTS file
            filepath = self.cache.get_path(text, self.voice)
            abs_path = str(filepath.absolute())
            
            if not filepath.exists():
                success = await self._generate_tts_safe(text, abs_path)
                if not success:
                    print(f"[Audio] TTS generation failed: {text[:30]}...")
                    return
            
            # Setup player
            self.tts_player.setSource(QUrl.fromLocalFile(abs_path))
            
            # Create and track future
            loop = asyncio.get_running_loop()
            future = loop.create_future()
            self._current_tts_future = future
            self._tts_futures.add(future)
            
            # Auto-cleanup on done
            future.add_done_callback(lambda f: self._tts_futures.discard(f))
        
        # RELEASE LOCK before playing (DeepSeek fix)
        self._duck_others(True)
        self.tts_player.play()
        
        if block and future:
            try:
                await asyncio.wait_for(future, timeout=TTS_TIMEOUT_SECONDS)
            except asyncio.TimeoutError:
                print("[Audio] TTS playback timeout")
                self.tts_player.stop()
            except asyncio.CancelledError:
                pass  # Expected on stop_voice()
            finally:
                self._duck_others(False)
                if self._current_tts_future is future:
                    self._current_tts_future = None

    async def _generate_tts_safe(self, text: str, target_path: str) -> bool:
        """
        Generate TTS using subprocess (DeepSeek fix).
        Avoids nested event loop issues with asyncio.run().
        """
        loop = asyncio.get_running_loop()
        
        def generate_sync():
            try:
                # Use edge-tts CLI (more stable than async API in thread)
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                    tmp_path = tmp.name
                
                cmd = [
                    'edge-tts',
                    '--text', text,
                    '--voice', self.voice,
                    '--write-media', tmp_path
                ]
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    timeout=TTS_TIMEOUT_SECONDS - 2
                )
                
                if result.returncode == 0 and Path(tmp_path).exists():
                    shutil.move(tmp_path, target_path)
                    return True
                else:
                    print(f"[Audio] edge-tts error: {result.stderr.decode()[:100]}")
                    return False
                    
            except subprocess.TimeoutExpired:
                print(f"[Audio] TTS subprocess timeout: {text[:30]}...")
                return False
            except Exception as e:
                print(f"[Audio] TTS generation error: {e}")
                return False
        
        try:
            success = await asyncio.wait_for(
                loop.run_in_executor(None, generate_sync),
                timeout=TTS_TIMEOUT_SECONDS
            )
            
            if success:
                # Schedule cache cleanup (non-blocking)
                asyncio.create_task(self.cache.enforce_limits_async())
            
            return success
            
        except asyncio.TimeoutError:
            print(f"[Audio] TTS executor timeout: {text[:30]}...")
            return False

    @pyqtSlot(QMediaPlayer.MediaStatus)
    def _on_tts_status(self, status):
        """
        Thread-safe status handler (DeepSeek fix).
        Uses QueuedConnection to ensure main thread execution.
        """
        if status in [QMediaPlayer.MediaStatus.EndOfMedia,
                      QMediaPlayer.MediaStatus.InvalidMedia]:
            
            self._duck_others(False)
            self.tts_finished.emit()
            
            # Complete future on main thread
            QMetaObject.invokeMethod(
                self,
                "_complete_current_future",
                Qt.ConnectionType.QueuedConnection
            )
    
    @pyqtSlot()
    def _complete_current_future(self):
        """Complete current future safely on main thread."""
        if self._current_tts_future and not self._current_tts_future.done():
            try:
                self._current_tts_future.set_result(True)
            except (asyncio.InvalidStateError, RuntimeError):
                pass  # Future already cancelled

    def stop_voice(self):
        """Stop TTS immediately."""
        self.tts_player.stop()
        self._duck_others(False)
        
        if self._current_tts_future and not self._current_tts_future.done():
            self._current_tts_future.cancel()
        
        # Clean up any lingering futures
        for future in list(self._tts_futures):
            if not future.done():
                future.cancel()

    def play_sfx(self, sfx_name: str):
        """Fire-and-forget SFX playback with LRU cache."""
        effect = self._sfx_cache.get(sfx_name)
        if effect:
            effect.play()

    def _duck_others(self, active: bool):
        """Lowers music volume when TTS is active."""
        target_vol = 0.1 if active else 0.3
        self.music_output.setVolume(target_vol)

    async def cleanup(self) -> None:
        """Lifecycle cleanup."""
        self.stop_voice()
        self.music_player.stop()
