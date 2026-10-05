import re


def strip_ansi_escape_codes(text):
    """Remove ANSI SGR sequences before text is written to a log."""
    return re.sub(r'\x1b\[[0-9;]*m', '', text)


def tx_line_ending(index):
    return {
        0: '\n',
        1: '\r',
        2: '\r\n',
    }.get(index, '')
