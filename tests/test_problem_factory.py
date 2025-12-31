# tests/test_problem_factory.py
"""Tests for the Problem Factory."""
import pytest
from core.problem_factory import ProblemFactory


@pytest.fixture
def factory():
    return ProblemFactory()


def test_generate_returns_required_keys(factory: ProblemFactory):
    """Generated problems should have all required keys."""
    problem = factory.generate(0)
    
    required_keys = ['level', 'target', 'options', 'prompt', 'emoji', 'host']
    for key in required_keys:
        assert key in problem, f"Missing key: {key}"


def test_generate_target_in_options(factory: ProblemFactory):
    """The target answer should always be in the options."""
    for level in range(10):
        problem = factory.generate(level)
        assert problem['target'] in problem['options'], f"Target not in options at level {level}"


def test_generate_has_three_options(factory: ProblemFactory):
    """Should always generate exactly 3 options."""
    for level in range(10):
        problem = factory.generate(level)
        assert len(problem['options']) == 3


def test_generate_options_are_unique(factory: ProblemFactory):
    """All options should be unique."""
    for level in range(10):
        problem = factory.generate(level)
        assert len(problem['options']) == len(set(problem['options']))


def test_generate_target_is_positive(factory: ProblemFactory):
    """Target should always be >= 1."""
    for level in range(10):
        problem = factory.generate(level)
        assert problem['target'] >= 1


def test_generate_options_are_positive(factory: ProblemFactory):
    """All options should be >= 1."""
    for level in range(10):
        problem = factory.generate(level)
        for opt in problem['options']:
            assert opt >= 1, f"Option {opt} is not positive at level {level}"


def test_generate_difficulty_scaling(factory: ProblemFactory):
    """Higher levels should have larger max numbers (on average)."""
    # Generate many problems to check statistical trend
    level_0_targets = [factory.generate(0)['target'] for _ in range(50)]
    level_9_targets = [factory.generate(9)['target'] for _ in range(50)]
    
    avg_level_0 = sum(level_0_targets) / len(level_0_targets)
    avg_level_9 = sum(level_9_targets) / len(level_9_targets)
    
    # Level 9 should have higher average targets
    assert avg_level_9 > avg_level_0, "Higher levels should have larger numbers on average"


def test_generate_level_0_max_is_3(factory: ProblemFactory):
    """Level 0 should have max target of 3."""
    for _ in range(20):
        problem = factory.generate(0)
        assert problem['target'] <= 3, "Level 0 target should be <= 3"


def test_generate_level_is_correct(factory: ProblemFactory):
    """Level in output should match input + 1."""
    for level_idx in range(10):
        problem = factory.generate(level_idx)
        assert problem['level'] == level_idx + 1


def test_generate_emoji_is_string(factory: ProblemFactory):
    """Emoji should be a non-empty string."""
    problem = factory.generate(0)
    assert isinstance(problem['emoji'], str)
    assert len(problem['emoji']) > 0


def test_generate_prompt_contains_item_name(factory: ProblemFactory):
    """Prompt should ask about counting something."""
    problem = factory.generate(0)
    assert "How many" in problem['prompt']
