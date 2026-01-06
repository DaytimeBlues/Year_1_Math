"""
Practice Dialog - Training Camp Configuration
Allows selection of specific practice modes without affecting level progression.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QIcon

from ui.design_tokens import (
    COLORS, STYLES, FONT_FAMILY, FONT_SIZE_HEADING, FONT_SIZE_BODY
)
from ui.premium_utils import draw_premium_background, add_soft_shadow

class PracticeDialog(QDialog):
    """
    Modal dialog to select a practice mode.
    Emits mode_selected(str) when user confirms.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Training Camp")
        self.setFixedSize(500, 450)
        
        # Remove default frame for custom rounded look if we wanted frameless,
        # but for simplicity/stability we keep standard frame and style content.
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint) # optional polish
        
        self.selected_mode = None
        self._init_ui()

    def paintEvent(self, event):
        """Draw premium gradient background."""
        draw_premium_background(self)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Header
        header = QLabel("Training Camp")
        header.setFont(QFont(FONT_FAMILY, FONT_SIZE_HEADING, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {COLORS['text']}; background: transparent;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        desc = QLabel("Choose a skill to practice.\nScores won't be saved.")
        desc.setFont(QFont(FONT_FAMILY, FONT_SIZE_BODY))
        desc.setStyleSheet(f"color: {COLORS['text_light']}; background: transparent;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        layout.addSpacing(10)
        
        # Mode Buttons
        self.modes = [
            ("Counting", "counting"),
            ("Addition (+)", "addition"),
            ("Subtraction (−)", "subtraction")
        ]
        
        for label, mode_key in self.modes:
            btn = QPushButton(label)
            btn.setStyleSheet(STYLES["secondary_button"]) # Blue for choices
            btn.setFixedHeight(60)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            add_soft_shadow(btn, blur=15, opacity=20)
            
            # Use lambda default arg capture to avoid scope issue
            btn.clicked.connect(lambda checked, m=mode_key: self._on_mode_clicked(m))
            
            layout.addWidget(btn)
            
        layout.addStretch()
        
        # Cancel Button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #636E72;
                font-weight: bold;
                font-size: 16px;
                border: 2px solid #BDC3C7;
                border-radius: 15px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #EEE;
                color: #2D3436;
            }
        """)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)

    def _on_mode_clicked(self, mode):
        print(f"[PracticeDialog] ACTION: User selected mode '{mode}'")
        self.selected_mode = mode
        self.accept()
