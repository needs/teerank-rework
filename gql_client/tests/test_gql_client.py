"""Test GQLClient."""

from http.client import HTTPConnection

import pytest

from gql_client_dgraph import GQLClientDgraph  # isort:skip


@pytest.fixture(name="client")
def fixture_client():
    """Create a GQLClient with an empty database and a test schema."""
    client = GQLClientDgraph(HTTPConnection("graphql:8080"), "/graphql")

    client.drop_all()

    client.set_schema(
        """
        type Test {
            string: String @search(by: [hash])
        }
        """
    )

    return client


@pytest.mark.parametrize(
    "string", ["foo", "bar", "\x00", "\U000e0021", "\U000f0009", "\v", "\n", "null"]
)
def test_client_execute(client, string):
    """Test client.execute()."""
    queries = """
        mutation setTest($test: AddTestInput!) {
            addTest(input: [$test]) {
                test {
                    string
                }
            }
        }

        query getTest($string: String) {
            queryTest(filter: {string: {eq: $string}}) {
                string
            }
        }
    """

    assert (
        client.execute(queries, {"test": {"string": string}}, "setTest")["addTest"][
            "test"
        ][0]["string"]
        == string
    )

    assert (
        client.execute(queries, {"string": string}, "getTest")["queryTest"][0]["string"]
        == string
    )
