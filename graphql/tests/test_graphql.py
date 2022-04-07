"""Test various Dgraph stuff."""

import pytest
import requests
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportQueryError


@pytest.fixture(name="client_dgraph", scope="session")
def fixture_client_dgraph():
    """Create a GraphQL pointing directly to dgraph:8080."""
    return Client(transport=AIOHTTPTransport(url="http://dgraph:8080/graphql"))


@pytest.fixture(name="client_graphql", scope="session")
def fixture_client_graphql():
    """Create a GraphQL pointing directly to graphql:8080."""
    return Client(transport=AIOHTTPTransport(url="http://graphql:8080/graphql"))


@pytest.fixture(scope="session", autouse=True)
def fixture_reset_database():
    """
    Reset database to an empty state.

    Tests don't need the database to be empty, so emptying database is only done
    at the beginning of the test session.
    """
    schema = """
        type Test {
            string: String
        }
    """

    response = requests.post(f"http://dgraph:8080/alter", data='{"drop_all": true}')
    assert response.status_code == 200 and "errors" not in response.json()

    response = requests.post(f"http://dgraph:8080/admin/schema", data=schema)
    assert response.status_code == 200 and "errors" not in response.json()


def store_string(client, string):
    """Store the given string in the database."""
    query = gql(
        """
        mutation ($test: AddTestInput!) {
            addTest(input: [$test]) {
                test {
                    string
                }
            }
        }
        """
    )

    variables = {
        "test": {
            "string": string,
        }
    }

    return client.execute(query, variables)["addTest"]["test"][0]["string"]


pytestmark = pytest.mark.parametrize(
    "string",
    [
        "\x00",
        "\U000e0021",
        "\U000f0009",
        "\v",
    ],
)


def test_bug(client_dgraph, string):
    """
    Test Dgraph encoding bug is fixed.

    The bug happen when some escape sequences are given to the Dgraph lexer.  It
    then freak out and reject the query.  This is problematic for us because we
    send user data to Dgraph, therefor a malicious user can use those escape
    sequence to make some query fail.
    """
    with pytest.raises(TransportQueryError):
        store_string(client_dgraph, string)


def test_fix(client_graphql, string):
    """
    Test GraphQL gateway on the problematic string.
    """
    assert store_string(client_graphql, string) == string
