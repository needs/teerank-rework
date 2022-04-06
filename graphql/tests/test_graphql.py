"""Test various Dgraph stuff."""

import pytest
import requests
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport


@pytest.fixture(name="client")
def fixture_client():
    """Create a GraphQL client."""
    address = "graphql:8080"

    schema = """
        type Test {
            string: String
        }
    """

    requests.post(f"http://{address}/alter", data='{"drop_all": true}')
    requests.post(f"http://{address}/admin/schema", data=schema)
    return Client(transport=AIOHTTPTransport(url=f"http://{address}/graphql"))


@pytest.fixture(name="store")
def fixture_store(client):
    """Create a function to store a Test."""

    def do(test):
        """Store the given test."""
        return client.execute(
            gql(
                """
                mutation ($test: AddTestInput!) {
                    addTest(input: [$test]) {
                        test {
                            string
                        }
                    }
                }
                """
            ),
            {"test": test},
        )["addTest"]["test"][0]

    return do


@pytest.fixture(name="query")
def fixture_query(client):
    """Create a function to query all Test."""

    def do():
        """Query all Tests."""
        return client.execute(
            gql(
                """
                query {
                    queryTest {
                        string
                    }
                }
                """
            )
        )["queryTest"]

    return do


def test_bad_encoding(store):
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
