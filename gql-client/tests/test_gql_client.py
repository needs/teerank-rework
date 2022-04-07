"""Test GraphQLClient."""

import http.client
import json

import pytest
from gql_client import GraphQLClient


@pytest.fixture(name="client")
def fixture_client():
    """Create a GraphQLClient with an empty database and a test schema."""
    schema = """
        type Test {
            string: String @search(by: [hash])
        }
    """

    connection = http.client.HTTPConnection("graphql:8080")

    connection.request("POST", "/alter", '{"drop_all": true}')
    response = connection.getresponse()
    assert response.status == 200 and "errors" not in json.loads(response.read())

    connection.request("POST", "/admin/schema", schema)
    response = connection.getresponse()
    assert response.status == 200 and "errors" not in json.loads(response.read())

    return GraphQLClient(connection, "/graphql")


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
