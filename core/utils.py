import re

_ANSI_ESCAPE_RE = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')


def strip_ansi(text: str) -> str:
    """Return text with ANSI escape codes removed."""
    return _ANSI_ESCAPE_RE.sub('', text)


def format_border(width: int) -> str:
    """Return a decorative border line of specified width: 'O===...===O'."""
    return f'O{"=" * max(0, width - 2)}O'
