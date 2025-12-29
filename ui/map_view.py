"""
Map View - Level Selection UI

Displays the game map with unlockable level nodes.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from config import (
    MIN_TOUCH_TARGET, BUTTON_GAP, MAP_LEVELS_COUNT,
    FONT_FAMILY, FONT_SIZE_BODY, FONT_SIZE_HEADING, COLORS
)


class MapView(QWidget):
    """
    Level selection map with progress tracking.
    
    DESIGN PRINCIPLES:
    - 96px level buttons for easy tapping
    - Green = unlocked, Gray = locked
    - Egg counter visible at all times
    """
    
    # Signals
    level_selected = pyqtSignal(int)
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self._level_buttons = []
        self._build_ui()
    
    def _build_ui(self):
        """Construct the map UI."""
        self.setStyleSheet(f"background-color: {COLORS['background']};")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Header
        header = QHBoxLayout()
        
        title = QLabel("🗺️ Counting Adventure")
        title.setFont(QFont(FONT_FAMILY, FONT_SIZE_HEADING, QFont.Weight.Bold))
        header.addWidget(title)
        
        header.addStretch()
        
        self.egg_label = QLabel("🥚 0 eggs")
        self.egg_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_BODY))
        header.addWidget(self.egg_label)
        
        layout.addLayout(header)
        
        # Instructions
        instructions = QLabel("Tap a level to start counting!")
        instructions.setFont(QFont(FONT_FAMILY, FONT_SIZE_BODY))
        instructions.setStyleSheet("color: #555555;")
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instructions)
        
        # Level buttons
        levels_layout = QHBoxLayout()
        levels_layout.setSpacing(BUTTON_GAP)
        
        for i in range(1, MAP_LEVELS_COUNT + 1):
            btn = QPushButton(str(i))
            btn.setFixedSize(MIN_TOUCH_TARGET, MIN_TOUCH_TARGET)
            btn.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Bold))
            btn.setStyleSheet(self._locked_style())
            btn.setEnabled(False)
            btn.clicked.connect(lambda checked, level=i: self.level_selected.emit(level))
            self._level_buttons.append(btn)
            levels_layout.addWidget(btn)
        
        levels_layout.addStretch()
        layout.addLayout(levels_layout)
        layout.addStretch()
    
    def _available_style(self) -> str:
        """Style for unlocked/available levels."""
        return f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white;
                border-radius: 48px;
                border: 3px solid #388E3C;
            }}
            QPushButton:hover {{
                background-color: #66BB6A;
            }}
            QPushButton:pressed {{
                background-color: #388E3C;
            }}
        """
    
    def _locked_style(self) -> str:
        """Style for locked levels."""
        return f"""
            QPushButton {{
                background-color: {COLORS['locked']};
                color: #757575;
                border-radius: 48px;
                border: 3px solid #9E9E9E;
            }}
        """
    
    async def refresh(self, egg_count: int):
        """Update the map with current progress."""
        self.egg_label.setText(f"🥚 {egg_count} eggs")
        
        # Get unlocked level from DB
        unlocked = await self.db.get_unlocked_level()
        
        for idx, btn in enumerate(self._level_buttons, start=1):
            if idx <= unlocked:
                btn.setStyleSheet(self._available_style())
                btn.setEnabled(True)
            else:
                btn.setStyleSheet(self._locked_style())
                btn.setEnabled(False)
