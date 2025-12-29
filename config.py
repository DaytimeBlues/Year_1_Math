"""
Application Configuration - v2 Architecture
Contains all tunable parameters for the gamified learning platform.
"""

# =============================================================================
# ACCESSIBILITY CONSTANTS (HCI Research)
# =============================================================================
# Recommended 96px minimum for 5-year-olds (fat-finger rule)
MIN_TOUCH_TARGET = 96
BUTTON_GAP = 32              # Generous spacing
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
# VISUALS
# =============================================================================
COLORS = {
    "background": "#f5f5dc",      # Cream/Off-white
    "primary": "#3399e6",
    "accent": "#f5a623",
    "success": "#4cd964",
    "danger": "#ff3b30",
    "locked": "#d1d1d6",
}

FONT_FAMILY = "Lexend"      # Dyslexia-friendly (fallback: Comic Sans MS)
FONT_SIZE_BODY = 20
FONT_SIZE_HEADING = 28

# =============================================================================
# ECONOMY
# =============================================================================
REWARD_CORRECT = 10          # Eggs per correct answer
REWARD_COMPLETION = 50       # Bonus for completing a level
MAP_LEVELS_COUNT = 10        # Levels per map

# =============================================================================
# VOICE CONFIGURATION
# =============================================================================
VOICE_TYPE = 'edge-tts'
VOICE_NAME = 'en-US-JennyNeural'
