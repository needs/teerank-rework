"""Helper functions to use our Dgraph database."""

import json
import logging
from time import sleep

import graphql.language.ast
import requests
from gql import Client as gql_connect
from gql import gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.aiohttp import log as aiohttp_logger


class Dgraph:
    """Handle operations on a Dgraph endpoint."""

    _queries: dict[str, graphql.language.ast.DocumentNode]
    DEFAULT_HOST = "graphql"
    DEFAULT_PORT = 8080

    def __init__(
        self,
        host: str = None,
        port: int = None,
        schema: str = None,
        retry_delay: int = 10,
    ) -> None:
        """Connect to Dgraph and optionally set database schema."""
        if host is None:
            host = Dgraph.DEFAULT_HOST

        if port is None:
            port = Dgraph.DEFAULT_PORT

        if schema is None:
            with open("sources/schema.graphql", "r", encoding="utf-8") as file:
                schema = file.read()

        self._host = host
        self._port = port

        self._dgraph = gql_connect(
            transport=AIOHTTPTransport(url=f"http://{host}:{port}/graphql")
        )

        # Reset query cache.
        self._queries = {}

        # By default gql is very verbose, limit logs to only warnings and above.
        aiohttp_logger.setLevel(logging.WARNING)

        # Setting GraphQL schema in dgraph requires a specially crafted HTTP
        # request to /admin/schema.  It can fail for many reasons, most of the
        # time dgraph is not ready or our IP is not whitelisted.

        while True:
            response = requests.post(f"http://{host}:{port}/admin/schema", data=schema)

            if response.status_code == 200 and "errors" not in response.json():
                break

            logging.warning(response.text)
            sleep(retry_delay)

    def drop_all_data(self) -> None:
        """Drop all data stored in dgraph."""
        requests.post(
            f"http://{self._host}:{self._port}/alter", data='{"drop_op": "DATA"}'
        )

    class RawString(str):
        """
        Raw string in query variables.

        This class is used by serialize_string() and unserialize_string().  When a
        string is an instance of this class, then it will not be
        serialized/unserialized.

        This is especially useful for sending regular expressions to dgraph.  For
        instance a regular expression that contains an escaped user string will not
        work as expected because the escaping that was done will be serialized a
        second time and that will change the escaped value.
        """

    @staticmethod
    def _deep_copy(value, copy):
        """
        Return a copy of the given value.

        Callback copy() is called on non-dict and non-list values.
        """
        if isinstance(value, dict):
            value = {key: Dgraph._deep_copy(val, copy) for key, val in value.items()}

        elif isinstance(value, list):
            value = [Dgraph._deep_copy(val, copy) for val in value]

        else:
            value = copy(value)

        return value

    @staticmethod
    def serialize_string(value):
        """Make all escape characters in value compatible with JSON."""
        if isinstance(value, str) and not isinstance(value, Dgraph.RawString):
            value = json.dumps(value)[1:-1]

        return value

    @staticmethod
    def unserialize_string(value):
        """Cancel the effect of serialize_string()."""
        if isinstance(value, str) and not isinstance(value, Dgraph.RawString):
            value = json.loads(f'"{value}"')

        return value

    def execute(self, query, variables=None, operation=None):
        """Execute the given query and return the results."""
        # Cache GQL'ed queries for faster performances.
        query = self._queries.setdefault(query, gql(query))

        # Serialize variables.
        variables = Dgraph._deep_copy(variables, Dgraph.serialize_string)

        result = self._dgraph.execute(
            query, variable_values=variables, operation_name=operation
        )

        # Unserialize variables.
        return Dgraph._deep_copy(result, Dgraph.unserialize_string)
