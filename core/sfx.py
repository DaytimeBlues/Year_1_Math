"""
Standard Sound Effects Library
Defines key UI sounds to ensure consistency across the application.
"""
import os

# Define relative paths to assets
# In a real production build, these would be bundled resources.
# For this phase, we map semantic names to filenames.
SFX_ASSETS_DIR = os.path.join("assets", "sfx")

class SFX:
    """
    Semantic names for application sound effects.
    """
    CLICK = "click"
    SUCCESS = "success" 
    ERROR = "error"
    LEVEL_COMPLETE = "level_complete"
    
    # Map semantic names to filenames (to be implemented/generated)
    # Using synth/generated fallbacks if files don't exist is a good future step
    FILENAMES = {
        CLICK: "click.wav",
        SUCCESS: "correct.wav",
        ERROR: "wrong.wav",
        LEVEL_COMPLETE: "win.wav"
    }

def get_sfx_path(sfx_name: str) -> str:
    """Resolve absolute path for a sound effect."""
    filename = SFX.FILENAMES.get(sfx_name)
    if not filename:
        return ""
    return os.path.abspath(os.path.join(SFX_ASSETS_DIR, filename))
