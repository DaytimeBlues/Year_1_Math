"""
core/protocols.py
Defines the strict contracts for the application services.
This allows for Dependency Injection and easy swapping of real/mock implementations.
"""

from typing import Protocol, List, Dict, Any, Optional
from enum import Enum, auto
from PySide6.QtCore import QObject

# =============================================================================
# DATA TYPES
# =============================================================================

class AudioChannel(Enum):
    VOICE = auto()      # High Priority (Tutor/Instructions)
    SFX = auto()        # Medium Priority (UI Interactions)
    MUSIC = auto()      # Low Priority (Background)

class TutorState(Enum):
    IDLE = auto()
    THINKING = auto()
    SPEAKING = auto()
    ERROR = auto()

# =============================================================================
# SERVICE PROTOCOLS
# =============================================================================

class IAudioService(Protocol):
    """
    Manages audio playback, caching, and channel priority (ducking).
    Adapts to application needs (TTS vs File).
    """
    async def speak(self, text: str, block: bool = True) -> None:
        """Generates and plays TTS on the VOICE channel."""
        ...
        
    def play_sfx(self, sfx_name: str) -> None:
        """Plays a sound effect on the SFX channel."""
        ...

    def stop_voice(self) -> None:
        """Immediately stops TTS playback (for interruptions)."""
        ...
        
    async def cleanup(self) -> None:
        """Lifecycle cleanup."""
        ...

class ITutorService(Protocol):
    """
    Interface for the AI Pedagogy Engine (Gemini/Mock).
    """
    async def analyze_canvas(self, stroke_data: List[Dict[str, Any]], bounding_box: Dict[str, float]) -> str:
        """
        Sends vector stroke data to the LLM for analysis.
        Returns a text hint or guidance string.
        """
        ...

    async def get_encouragement(self, context: str) -> str:
        """
        Requests a context-aware encouragement string.
        """
        ...

    def cancel_request(self) -> None:
        """Cancels any pending network requests."""
        ...

class IDatabaseService(Protocol):
    """
    Interface for persistent state management.
    """
    async def initialize(self) -> None:
        """Initialize DB connection."""
        ...
        
    async def get_eggs(self) -> int:
        """Get current egg balance."""
        ...
        
    async def add_eggs(self, amount: int) -> int:
        """Add eggs and return new balance."""
        ...
        
    async def unlock_level(self, level_id: int) -> None:
        """Unlock a level."""
        ...
        
    async def close(self) -> None:
        """Close connection."""
        ...
