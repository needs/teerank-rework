"""Implement GQLClient class."""

import json


class GQLException(Exception):
    pass


class GQLClient:
    def __init__(self, connection, path: str = None):
        """Initialize GQLClient."""
        self.connection = connection
        self.path = path if path is not None else "/graphql"

    def execute(self, query: str, variables=None, operation_name=None):
        """Send the query to the GraphQL server and return the answer."""
        request = {
            "query": query,
        }

        if variables is not None:
            request["variables"] = variables

        if operation_name is not None:
            request["operationName"] = operation_name

        data = json.dumps(request)
        headers = {"Content-type": "application/json"}

        self.connection.request("POST", self.path, data, headers)
        response = json.loads(self.connection.getresponse().read())

        if "errors" in response:
            raise GQLException(response["errors"])

        return response["data"]
