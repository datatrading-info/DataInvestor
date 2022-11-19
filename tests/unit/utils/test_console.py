import pytest

from datainvestor.utils.console import GREEN, BLUE, CYAN, string_colour


@pytest.mark.parametrize(
    "text,colour,expected",
    [
        ('green colour', GREEN, "\x1b[1;32mgreen colour\x1b[0m"),
        ('blue colour', BLUE, "\x1b[1;34mblue colour\x1b[0m"),
        ('cyan colour', CYAN, "\x1b[1;36mcyan colour\x1b[0m"),
    ]
)
def test_string_colour(text, colour, expected):
    """
    """
    assert string_colour(text, colour=colour) == expected
