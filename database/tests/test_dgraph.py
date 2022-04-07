"""Test various Dgraph stuff."""

import pytest
from dgraph import Dgraph


@pytest.fixture(name="dgraph")
def fixture_dgraph():
    """Create a Dgraph instance with a schema for tests."""
    dgraph = Dgraph(
        schema="""
        type Test {
            string: String
        }
        """,
    )
    dgraph.drop_all_data()
    return dgraph


@pytest.fixture(name="store")
def fixture_store(dgraph):
    """Create a function to store a Test."""

    def do(test):
        """Store the given test."""
        return dgraph.execute(
            """
            mutation ($test: AddTestInput!) {
                addTest(input: [$test]) {
                    test {
                        string
                    }
                }
            }
            """,
            {"test": test},
        )["addTest"]["test"][0]

    return do


@pytest.fixture(name="query")
def fixture_query(dgraph):
    """Create a function to query all Test."""

    def do():
        """Query all Tests."""
        return dgraph.execute(
            """
            query {
                queryTest {
                    string
                }
            }
            """
        )["queryTest"]

    return do


def test_bad_encoding(dgraph, store):
    """
    Test Dgraph encoding bug is fixed.

    The bug happen when some escape sequences are given to the Dgraph lexer.  It
    then freak out and reject the query.  This is problematic for us because we
    send user data to Dgraph, therefor a malicious user can use those escape
    sequence to make some query fail.
    """
    strings = ["\x00", "\U000e0021", "\U000f0009", "\v", "\n", "null"]

    for string in strings:
        test = {
            "string": string,
        }

        assert test == store(test)


def test_drop_all_data(dgraph, store, query):
    """Test drop_all_data()."""
    store({"string": "test"})
    assert query()

    dgraph.drop_all_data()
    assert not query()


def test_connection_failed(requests_mock):
    """Test Dgraph when connection failed."""

    def fail(_request, context):
        """Simulate a failure."""
        fail.count += 1

        if fail.count < 3:
            context.status_code = 404
            return '"errors"'
        else:
            context.status_code = 200
            return '"success"'

    fail.count = 0

    requests_mock.post(
        f"http://{Dgraph.DEFAULT_HOST}:{Dgraph.DEFAULT_PORT}/admin/schema",
        text=fail,
    )

    Dgraph(retry_delay=0)
    assert fail.count == 3
