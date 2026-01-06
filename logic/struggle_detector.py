"""
logic/struggle_detector.py
Implements the heuristic logic to distinguish between 'Playful Scribbling'
and 'Genuine Struggle'.

Heuristic Rules:
1. Struggle: High density of strokes in a small area (overwriting/erasing).
2. Play: High velocity strokes covering a large area (drawing pictures).
3. Idle: No input for X seconds.
"""

import time
import math
from typing import List
from PySide6.QtCore import QPointF, QRectF

class StruggleState:
    NORMAL = "normal"
    STRUGGLING = "struggling"   # Needs help
    PLAYING = "playing"         # Do not disturb
    IDLE = "idle"               # Needs prompt

class StruggleDetector:
    def __init__(self):
        # Configuration Thresholds (Tuned for ages 4-6)
        self.STROKE_COUNT_TRIGGER = 8       # Minimum strokes to analyze
        self.DENSITY_THRESHOLD = 0.6        # High density = Struggle
        self.AREA_COVERAGE_THRESHOLD = 0.3  # % of canvas covered. >0.3 = Play
        self.IDLE_TIMEOUT = 12.0            # Seconds before IDLE trigger
        
        # State
        self._last_interaction_time = time.time()
        self._eraser_use_count = 0

    def register_interaction(self, is_eraser: bool = False):
        """Call this on every pen down/move event."""
        self._last_interaction_time = time.time()
        if is_eraser:
            self._eraser_use_count += 1

    def analyze(self, strokes: List[List[QPointF]], canvas_rect: QRectF) -> str:
        """
        Main heuristic engine. Returns a StruggleState constant.
        Args:
            strokes: List of strokes, where each stroke is a list of QPointF.
            canvas_rect: The total available drawing area.
        """
        now = time.time()
        time_since_input = now - self._last_interaction_time
        stroke_count = len(strokes)

        # 1. Check IDLE
        if time_since_input > self.IDLE_TIMEOUT:
            # Only flag idle if they haven't done much yet (stuck at start)
            if stroke_count < 3:
                return StruggleState.IDLE
            return StruggleState.NORMAL

        # 2. Too few strokes to judge
        if stroke_count < self.STROKE_COUNT_TRIGGER:
            # Exception: Repeated erasing suggests struggle even with few strokes
            if self._eraser_use_count > 3:
                return StruggleState.STRUGGLING
            return StruggleState.NORMAL

        # 3. Calculate Bounding Box of all ink
        ink_rect = self._calculate_ink_bounds(strokes)
        if ink_rect.isEmpty():
            return StruggleState.NORMAL

        # 4. Calculate Heuristics
        # Ratio of ink bounding box to total canvas
        coverage_ratio = (ink_rect.width() * ink_rect.height()) / (canvas_rect.width() * canvas_rect.height())
        
        # Density: How much ink is packed into that bounding box?
        # A simple approximation: Total stroke length / Diagonal of bounding box
        total_length = sum(self._stroke_length(s) for s in strokes)
        diag = math.sqrt(ink_rect.width()**2 + ink_rect.height()**2)
        density_score = total_length / diag if diag > 0 else 0

        # 5. Determine State
        
        # Scenario A: Play/Drawing
        # Large coverage, high stroke count. Child is likely drawing a picture.
        if coverage_ratio > self.AREA_COVERAGE_THRESHOLD:
            return StruggleState.PLAYING

        # Scenario B: Struggle
        # Small area, high density (scribbling over same spot) OR high eraser use
        if density_score > 5.0 or self._eraser_use_count > 4:
            return StruggleState.STRUGGLING

        return StruggleState.NORMAL

    def _calculate_ink_bounds(self, strokes: List[List[QPointF]]) -> QRectF:
        """Returns the bounding rectangle of all strokes."""
        if not strokes:
            return QRectF()
            
        min_x, min_y = float('inf'), float('inf')
        max_x, max_y = float('-inf'), float('-inf')
        
        has_points = False
        for stroke in strokes:
            for point in stroke:
                has_points = True
                min_x = min(min_x, point.x())
                min_y = min(min_y, point.y())
                max_x = max(max_x, point.x())
                max_y = max(max_y, point.y())
                
        if not has_points:
            return QRectF()
            
        return QRectF(min_x, min_y, max_x - min_x, max_y - min_y)

    def _stroke_length(self, stroke: List[QPointF]) -> float:
        """Calculates total pixel length of a stroke."""
        length = 0.0
        for i in range(1, len(stroke)):
            p1 = stroke[i-1]
            p2 = stroke[i]
            dist = math.sqrt((p2.x() - p1.x())**2 + (p2.y() - p1.y())**2)
            length += dist
        return length

    def reset(self):
        """Call when clearing the canvas or starting new problem."""
        self._last_interaction_time = time.time()
        self._eraser_use_count = 0
