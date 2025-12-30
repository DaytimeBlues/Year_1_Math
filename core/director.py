"""
The Director
Central State Machine for the application.
Controls the flow and locks/unlocks the UI to prevent race conditions.
"""
from enum import Enum, auto
import logging
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

class AppState(Enum):
    IDLE = auto()           # Waiting for navigation or setup
    INPUT_ACTIVE = auto()   # Child is drawing/interacting (Standard State)
    EVALUATING = auto()     # Validating answer (Short blocking)
    TUTOR_SPEAKING = auto() # TTS/AI Voice active (Strict Blocking + Ducking)
    CELEBRATION = auto()    # Particle effects/Rewards (Strict Blocking)

class Director(QObject):
    # Signal emitted whenever state changes.
    state_changed = pyqtSignal(AppState)

    def __init__(self, container):
        super().__init__()
        self.container = container
        self._current_state = AppState.IDLE
        self._logger = logging.getLogger("Director")

    @property
    def current_state(self) -> AppState:
        return self._current_state

    @pyqtSlot(AppState)
    def set_state(self, new_state: AppState):
        """
        Central gateway for all state transitions.
        """
        if self._current_state == new_state:
            return

        # self._logger.info(f"State Transition: {self._current_state.name} -> {new_state.name}")
        self._current_state = new_state
        
        # Broadcast change to all UI components
        self.state_changed.emit(new_state)

        # Handle specific side-effects of entering a state
        if new_state == AppState.TUTOR_SPEAKING:
            self._handle_tutor_start()
        elif new_state == AppState.INPUT_ACTIVE:
            self._handle_input_active()

    def _handle_tutor_start(self):
        """Logic when tutor starts speaking."""
        # Example: Duck audio (handled by AudioService mostly, but we could enforce it here)
        pass

    def _handle_input_active(self):
        """Logic when input becomes active."""
        # Ensure audio is unducked or stopped if we interrupted
        pass
