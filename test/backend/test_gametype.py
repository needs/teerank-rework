"""
Test operations on GameType.
"""

import pytest
from backend.database.gametype import get, id_none

@pytest.mark.parametrize(
    "name", [ 'gametype-test', '', None]
)
def test_gametype(name):
    """
    Test GameType creation.
    """

    assert get(name)['name'] == name


@pytest.mark.parametrize(
    "name", [ 'gametype-test', '', None]
)
def test_gametype_duplicate(name):
    """
    Test creation of two duplicate gametype.
    """

    assert get(name) == get(name)


def test_gametype_none():
    """
    Test the behavior of id_none().
    """

    assert get(None, 'id')['id'] == id_none()
