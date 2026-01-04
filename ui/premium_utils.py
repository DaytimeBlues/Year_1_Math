"""
Premium UI Utilities - Dynamic Background & Animations

Provides QPainter-based rendering for premium visual effects.
"""

from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QPen
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup, QRect
from PyQt6.QtWidgets import QWidget


def draw_premium_background(widget: QWidget):
    """
    Draw a warm gradient background with subtle decorative shapes.
    
    Call this from your widget's paintEvent():
        def paintEvent(self, event):
            draw_premium_background(self)
            super().paintEvent(event)
    """
    painter = QPainter(widget)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # 1. Warm gradient (top to bottom)
    gradient = QLinearGradient(0, 0, 0, widget.height())
    gradient.setColorAt(0.0, QColor("#FFF9F0"))  # Warm Cloud
    gradient.setColorAt(1.0, QColor("#FFF0E1"))  # Peachier
    
    painter.fillRect(widget.rect(), gradient)
    
    # 2. Subtle decorative shapes (depth without distraction)
    painter.setPen(Qt.PenStyle.NoPen)
    
    # Big faint circle bottom left
    painter.setBrush(QColor(255, 220, 150, 40))  # Warm yellow, low opacity
    painter.drawEllipse(-50, widget.height() - 200, 300, 300)
    
    # Small faint circle top right
    painter.setBrush(QColor(72, 219, 251, 30))  # Sky blue, very low opacity
    painter.drawEllipse(widget.width() - 150, -50, 200, 200)
    
    painter.end()


def create_shake_animation(widget: QWidget, intensity: int = 10) -> QSequentialAnimationGroup:
    """
    Creates a juicy shake animation with elastic overshoot (Frontend Audit v3.0).
    
    Physics inspiration: Spring with high frequency, quick decay.
    """
    print(f"[premium_utils] ANIM: Creating elastic shake animation for {widget.objectName()}")
    
    original_x = widget.x()
    
    group = QSequentialAnimationGroup(widget)
    
    # Keyframe timings for organic feel
    # Pattern: Right -> Left -> Right(smaller) -> Left(smaller) -> Center
    # We use QPropertyAnimation segments to simulate the elastic settle manually 
    # OR we use a single OutElastic curve. 
    # The audit recommended "Custom Elastic Shake" using a sequence OR single curve.
    # The single curve approach is cleaner for maintenance.
    
    # However, QPropertyAnimation with OutElastic on 'geometry' can be tricky if the widget is in a layout.
    # But for "shake", we typically want visual displacement. 
    # Let's use the robust multi-keyframe approach from the audit for maximum control.
    
    keyframes = [
        (intensity * 1.0,  50,  QEasingCurve.Type.OutQuad),     # Snap right
        (-intensity * 0.8, 50,  QEasingCurve.Type.OutQuad),     # Snap left
        (intensity * 0.4,  40,  QEasingCurve.Type.OutCubic),    # Smaller right
        (-intensity * 0.2, 40,  QEasingCurve.Type.OutCubic),    # Smaller left
        (0,                60,  QEasingCurve.Type.OutElastic),  # Settle with bounce
    ]
    
    for offset, duration, easing in keyframes:
        anim = QPropertyAnimation(widget, b"pos") # Use 'pos' instead of 'x' for broader compatibility? Or 'geometry'?
        # 'pos' works well for widgets in relative positioning or windows. 
        # Inside layouts, 'geometry' is often fought over.
        # But for a quick shake, 'geometry' or 'pos' (via property proxy) is standard.
        # Let's stick to the audit's suggestion which implies 'x' property.
        
        anim = QPropertyAnimation(widget, b"geometry") # Stick to geometry for robustness
        anim.setDuration(duration)
        anim.setStartValue(widget.geometry())
        
        # Calculate target rect
        current_geo = widget.geometry()
        # Note: In a sequence, 'widget.geometry()' is evaluated at CREATION time, not runtime.
        # This is a common pitfall. We need to chain them properly.
        # But QSequentialAnimationGroup doesn't auto-chain start values unless configured.
        
        # Actually, simpler is better:
        # A single animation using key values?
        
        pass 
    
    # RETRY: The loop approach in the audit code requires offsets relative to *original* position.
    # We need to set start/end values relative to that.
    
    # Let's use the single-curve OutElastic approach recommended as "Alternative" in the audit 
    # because it is much less code and smoother to maintain.
    
    anim = QPropertyAnimation(widget, b"geometry")
    anim.setDuration(500) # Slightly longer to let the elastic settle
    
    curve = QEasingCurve(QEasingCurve.Type.OutElastic)
    curve.setAmplitude(1.2)   # Slightly exaggerated bounce
    curve.setPeriod(0.25)     # Faster oscillation
    anim.setEasingCurve(curve)
    
    # We want to shake "from" an offset "to" original.
    original_geo = widget.geometry()
    offset_geo = QRect(original_geo)
    offset_geo.moveLeft(original_geo.left() + intensity)
    
    anim.setStartValue(offset_geo)
    anim.setEndValue(original_geo)
    
    # Wrap in group to match return type signature expected by other code?
    # The existing signature returns QSequentialAnimationGroup.
    # We should wrap it to avoid breaking callers.
    
    wrapper_group = QSequentialAnimationGroup(widget)
    wrapper_group.addAnimation(anim)
    
    return wrapper_group


def create_pulse_animation(widget: QWidget, duration: int = 1000) -> QPropertyAnimation:
    """
    Create a pulsing animation for the current level indicator.
    
    Usage:
        anim = create_pulse_animation(button)
        anim.setLoopCount(-1)  # Infinite
        anim.start()
    """
    # Note: For true scale animation, you'd need QGraphicsView.
    # This is a simple geometry-based approximation.
    anim = QPropertyAnimation(widget, b"geometry")
    anim.setDuration(duration)
    
    original = widget.geometry()
    
    # Grow by 5px on each side
    grown = QRect(
        original.left() - 5,
        original.top() - 5,
        original.width() + 10,
        original.height() + 10
    )
    
    anim.setStartValue(original)
    anim.setKeyValueAt(0.5, grown)  # Midpoint: grown
    anim.setEndValue(original)      # End: back to original
    
    anim.setEasingCurve(QEasingCurve.Type.InOutSine)
    
    return anim
