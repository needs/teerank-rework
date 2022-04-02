"""Configure tests."""

import pytest
from dgraph import Dgraph


@pytest.fixture
def dgraph():
    """Configure a Dgraph instance with the production schema."""
    return Dgraph()
