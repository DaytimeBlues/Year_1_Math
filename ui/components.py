"""
Shared UI Components
"""
from PySide6.QtWidgets import QPushButton, QLabel, QWidget
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Property, Qt, Signal
from PySide6.QtGui import QFont

class JuicyButton(QPushButton):
    """
    A QPushButton with juice:
    - Sound effect triggers on press
    """
    def __init__(self, text="", audio_service=None, sfx_name="click"):
        super().__init__(text)
        self.audio = audio_service
        self.sfx_name = sfx_name
        self.pressed.connect(self._on_press)

    def _on_press(self):
        if self.audio:
            self.audio.play_sfx(self.sfx_name)

class JuicyLabel(QLabel):
    """
    A QLabel that can 'pop' (pulse animation) on updates.
    """
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._font_scale = 1.0
        self._base_size = 20
        # Initialize animation
        self.anim = QPropertyAnimation(self, b"font_scale")
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QEasingCurve.Type.OutQuad)

    def set_base_font_size(self, size):
        self._base_size = size
        self._update_font()

    @Property(float)
    def font_scale(self):
        return self._font_scale

    @font_scale.setter
    def font_scale(self, scale):
        self._font_scale = scale
        self._update_font()

    def _update_font(self):
        f = self.font()
        f.setPixelSize(int(self._base_size * self._font_scale))
        self.setFont(f)

    def pop(self):
        """Trigger a pulse animation (1.0 -> 1.5 -> 1.0)."""
        self.anim.stop()
        self.anim.setKeyValueAt(0, 1.0)
        self.anim.setKeyValueAt(0.5, 1.5)
        self.anim.setKeyValueAt(1, 1.0)
        self.anim.start()


class SkipOverlay(QWidget):
    """
    Transparent overlay that catches taps during TUTOR_SPEAKING/CELEBRATION.
    
    Z.ai Solution: Instead of using setEnabled(False) which blocks ALL input
    including "tap to skip", this overlay allows tap-to-skip while preventing
    interaction with underlying buttons.
    """
    
    clicked = Signal()
    
    def __init__(self, parent, director):
        super().__init__(parent)
        self.director = director
        
        # Transparent but catches events
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        
        # Cover entire parent
        self.resize(parent.size())
        self.hide()
        
        # Connect to director for skip
        self.clicked.connect(self._on_skip_requested)
    
    def _on_skip_requested(self):
        """Handle tap-to-skip."""
        self.director.force_skip()
        
        # Also stop any playing audio
        if hasattr(self.parent(), 'audio') and self.parent().audio:
            self.parent().audio.stop_voice()
    
    def mousePressEvent(self, event):
        """Catch all mouse presses and emit skip signal."""
        self.clicked.emit()
        event.accept()
    
    def resizeEvent(self, event):
        """Stay same size as parent."""
        if self.parent():
            self.resize(self.parent().size())
