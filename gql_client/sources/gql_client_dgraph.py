"""Implement Dgraph client."""


from gql_client import GQLClient


class GQLClientDgraph(GQLClient):
    def __init__(self, connection, path):
        """Initialize GQLClientDgraph."""
        super().__init__(connection, path)

    def _request(self, path, data):
        """Do an HTTP POST request to Dgraph and validate the response."""
        self.connection.request("POST", path, data)
        response = self.connection.getresponse()

        if response.status != 200:
            raise GQLException(response.reason)
        if "errors" in response:
            raise GQLException(response["errors"])

    def drop_all(self):
        """Drop all data and schema from the Dgraph database."""
        self._request("/alter", '{"drop_all": true}')

    def set_schema(self, schema):
        """Set Dgraph database schema."""
        self._request("/admin/schema", schema)
