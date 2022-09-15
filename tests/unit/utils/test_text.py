import pytest

from csvcubed.utils.text import truncate


def test_truncating_text():
    """Ensure that text truncation works."""
    truncated_message = truncate("This message is over 10 chars long", 10)
    assert len(truncated_message) == 11  # We expect an extra char for the ellipsis
    assert truncated_message == "This messa…"


def test_text_not_needing_truncation():
    """Ensure that text truncation doesn't affect a message shorter than the limit."""
    truncated_message = truncate("A short message", 20)
    assert len(truncated_message) == len("A short message")
    assert truncated_message == "A short message"


if __name__ == "__main__":
    pytest.main()
