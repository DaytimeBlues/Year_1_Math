"""
Application Configuration - v2.1 Premium Design System
"Functional prototype → Product" pivot.

DESIGN UPDATE (Premium UX):
- Warm, soft color palette (reduced cognitive load)
- Juicy 3D buttons with CSS-driven depth
- Dynamic gradient backgrounds via QPainter
- Touch-optimized accessibility
"""

# =============================================================================
# IMPORT DESIGN TOKENS (Single Source of Truth)
# =============================================================================
from ui.design_tokens import (
    COLORS, STYLES, PREMIUM_BG_GRADIENT,
    FONT_FAMILY, FONT_SIZE_BODY, FONT_SIZE_HEADING,
    MIN_TOUCH_TARGET, BUTTON_GAP
)

# =============================================================================
# ACCESSIBILITY CONSTANTS (HCI Research)
# =============================================================================
# Re-exporting from design_tokens if needed, or keeping local config logic
DEBOUNCE_DELAY_MS = 300      # Prevent rage clicks

# =============================================================================
# CONTENT ASSETS
# =============================================================================
CONCRETE_ITEMS = [
    {'name': 'apples', 'emoji': '🍎'},
    {'name': 'stars', 'emoji': '⭐'},
    {'name': 'cats', 'emoji': '🐱'},
    {'name': 'cars', 'emoji': '🚗'},
    {'name': 'ducks', 'emoji': '🦆'},
    {'name': 'fish', 'emoji': '🐟'},
    {'name': 'flowers', 'emoji': '🌸'},
    {'name': 'hearts', 'emoji': '❤️'},
]

# =============================================================================
# ECONOMY
# =============================================================================
REWARD_CORRECT = 10
REWARD_COMPLETION = 50
MAP_LEVELS_COUNT = 10

# =============================================================================
# AUDIO CONFIGURATION
# =============================================================================
VOLUME_SFX = 0.6
VOLUME_MUSIC = 0.3
VOLUME_MUSIC_DUCKED = 0.1
VOLUME_VOICE = 1.0
SFX_CACHE_MAX = 20


