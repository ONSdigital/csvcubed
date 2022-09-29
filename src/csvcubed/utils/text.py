"""
Text Utilities
--------------

Utilities for text manipulation.
"""


def truncate(message: str, message_truncate_at: int) -> str:
    """Truncate a string to a given length. Adds an elipsis if truncation is performed."""
    if len(message) <= message_truncate_at:
        return message
    else:
        return message[:message_truncate_at] + "…"
