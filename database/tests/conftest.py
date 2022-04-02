"""Configure tests."""

import pytest
from dgraph import Dgraph


@pytest.fixture(name="dgraph")
def fixture_dgraph():
    """Configure a Dgraph instance with the production schema."""
    dgraph = Dgraph()
    dgraph.drop_all_data()
    return dgraph
