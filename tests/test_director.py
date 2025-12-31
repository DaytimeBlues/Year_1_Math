# tests/test_director.py
"""Tests for the Director State Machine."""
import pytest
from unittest.mock import MagicMock
from core.director import Director, AppState
from core.container import ServiceContainer


@pytest.fixture
def container():
    """Create a minimal service container."""
    return ServiceContainer()


@pytest.fixture
def director(container):
    """Create a Director instance."""
    return Director(container)


def test_initial_state_is_idle(director: Director):
    """Director should start in IDLE state."""
    assert director.current_state == AppState.IDLE


def test_valid_transition_idle_to_tutor_speaking(director: Director):
    """Should allow IDLE -> TUTOR_SPEAKING."""
    director.set_state(AppState.TUTOR_SPEAKING)
    assert director.current_state == AppState.TUTOR_SPEAKING


def test_valid_transition_idle_to_input_active(director: Director):
    """Should allow IDLE -> INPUT_ACTIVE."""
    director.set_state(AppState.INPUT_ACTIVE)
    assert director.current_state == AppState.INPUT_ACTIVE


def test_valid_transition_input_to_evaluating(director: Director):
    """Should allow INPUT_ACTIVE -> EVALUATING."""
    director.set_state(AppState.INPUT_ACTIVE)
    director.set_state(AppState.EVALUATING)
    assert director.current_state == AppState.EVALUATING


def test_valid_transition_evaluating_to_celebration(director: Director):
    """Should allow EVALUATING -> CELEBRATION."""
    director.set_state(AppState.INPUT_ACTIVE)
    director.set_state(AppState.EVALUATING)
    director.set_state(AppState.CELEBRATION)
    assert director.current_state == AppState.CELEBRATION


def test_invalid_transition_is_blocked(director: Director):
    """Invalid transitions should be blocked."""
    # IDLE -> CELEBRATION is not valid
    director.set_state(AppState.CELEBRATION)
    assert director.current_state == AppState.IDLE  # Should stay in IDLE


def test_same_state_transition_is_noop(director: Director):
    """Setting same state should be a no-op."""
    director.set_state(AppState.INPUT_ACTIVE)
    director.set_state(AppState.INPUT_ACTIVE)
    assert director.current_state == AppState.INPUT_ACTIVE


def test_state_changed_signal_emitted(director: Director):
    """State changes should emit signal."""
    callback = MagicMock()
    director.state_changed.connect(callback)
    
    director.set_state(AppState.INPUT_ACTIVE)
    
    callback.assert_called_once_with(AppState.INPUT_ACTIVE)


def test_state_changed_not_emitted_on_invalid(director: Director):
    """Invalid transitions should not emit signal."""
    callback = MagicMock()
    director.state_changed.connect(callback)
    
    # Try invalid transition
    director.set_state(AppState.CELEBRATION)
    
    callback.assert_not_called()


def test_force_skip_from_tutor_speaking(director: Director):
    """force_skip should work from TUTOR_SPEAKING."""
    director.set_state(AppState.TUTOR_SPEAKING)
    director.force_skip()
    assert director.current_state == AppState.INPUT_ACTIVE


def test_force_skip_from_celebration(director: Director):
    """force_skip should work from CELEBRATION."""
    director.set_state(AppState.INPUT_ACTIVE)
    director.set_state(AppState.EVALUATING)
    director.set_state(AppState.CELEBRATION)
    director.force_skip()
    assert director.current_state == AppState.INPUT_ACTIVE


def test_force_skip_from_idle_is_noop(director: Director):
    """force_skip from IDLE should do nothing."""
    director.force_skip()
    assert director.current_state == AppState.IDLE


def test_full_game_loop_transitions(director: Director):
    """Test a complete game loop: IDLE -> play -> win -> IDLE."""
    assert director.current_state == AppState.IDLE
    
    # Start level
    director.set_state(AppState.TUTOR_SPEAKING)
    assert director.current_state == AppState.TUTOR_SPEAKING
    
    # Enable input
    director.set_state(AppState.INPUT_ACTIVE)
    assert director.current_state == AppState.INPUT_ACTIVE
    
    # Submit answer
    director.set_state(AppState.EVALUATING)
    assert director.current_state == AppState.EVALUATING
    
    # Celebrate
    director.set_state(AppState.CELEBRATION)
    assert director.current_state == AppState.CELEBRATION
    
    # Return to map
    director.set_state(AppState.IDLE)
    assert director.current_state == AppState.IDLE
