# tests/test_hint_engine.py
import pytest

from core.hint_engine import RuleBasedHintEngine, Hint, HINT_LIBRARY


@pytest.fixture()
def engine() -> RuleBasedHintEngine:
    return RuleBasedHintEngine()


def test_get_hint_returns_none_when_attempt_count_less_than_1(engine: RuleBasedHintEngine):
    assert engine.get_hint("counting", 0) is None
    assert engine.get_hint("counting", -1) is None


@pytest.mark.parametrize(
    "attempt_count, expected_hint",
    [
        (1, HINT_LIBRARY["counting"][0]),
        (2, HINT_LIBRARY["counting"][1]),
        (3, HINT_LIBRARY["counting"][2]),
    ],
)
def test_get_hint_returns_correct_hint_for_attempts_1_2_3(
    engine: RuleBasedHintEngine, attempt_count: int, expected_hint: Hint
):
    hint = engine.get_hint("counting", attempt_count)
    assert hint == expected_hint
    assert isinstance(hint, Hint)


def test_get_hint_caps_at_last_hint_for_high_attempt_counts(engine: RuleBasedHintEngine):
    last = HINT_LIBRARY["counting"][-1]
    assert engine.get_hint("counting", 999) == last
    assert engine.get_hint("counting", 4) == last


def test_get_hint_uses_generic_for_unknown_activity_types(engine: RuleBasedHintEngine):
    generic_hints = HINT_LIBRARY["generic"]

    assert engine.get_hint("unknown_activity_type", 1) == generic_hints[0]
    assert engine.get_hint("unknown_activity_type", 2) == generic_hints[1]
    assert engine.get_hint("unknown_activity_type", 999) == generic_hints[-1]


def test_get_random_encouragement_returns_valid_hint(engine: RuleBasedHintEngine):
    hint = engine.get_random_encouragement()

    assert isinstance(hint, Hint)
    assert hint.hint_type == "audio"
    assert hint.name in {"you_got_this", "keep_trying", "almost_there"}
    assert hint.message in {"You've got this!", "Keep trying!", "Almost there!"}


def test_reset_for_activity_clears_history(engine: RuleBasedHintEngine):
    # Seed internal history directly (there is no public writer in the provided class)
    engine._hint_history["activity_123"] = 2
    engine._hint_history["other_activity"] = 1

    engine.reset_for_activity("activity_123")

    assert "activity_123" not in engine._hint_history
    assert "other_activity" in engine._hint_history


def test_reset_for_activity_noop_when_missing(engine: RuleBasedHintEngine):
    # Should not raise if activity_id doesn't exist
    engine.reset_for_activity("missing_activity")
    assert engine._hint_history == {}
