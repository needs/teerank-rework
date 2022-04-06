"""Intercept all traffic to /graphql."""

import json


def _explore(value, on_string):
    """Explore value and call on_string on all instance of str."""
    if isinstance(value, dict):
        for key, val in value.items():
            value[key] = _explore(val, on_string)

    elif isinstance(value, list):
        for i, val in enumerate(value):
            value[i] = _explore(val, on_string)

    elif isinstance(value, str):
        value = on_string(value)

    return value


def _serialize_string(string):
    """Make all escape characters in value compatible with JSON."""
    return json.dumps(string)[1:-1]


def _unserialize_string(string):
    """Cancel the effect of serialize_string()."""
    return json.loads(f'"{string}"')


def request(flow):
    """Route all traffic to dgraph and serialize data sent to /graphql."""
    flow.request.host = "dgraph-alpha"

    if flow.request.path == "/graphql":
        content = json.loads(flow.request.content)
        if "variables" in content:
            content["variables"] = _explore(content["variables"], _serialize_string)
            flow.request.content = json.dumps(content).encode()


def response(flow):
    """Unserialize data sent back by /graphql."""
    if flow.request.path == "/graphql":
        content = json.loads(flow.response.content)
        if "data" in content:
            content["data"] = _explore(content["data"], _unserialize_string)
            flow.response.content = json.dumps(content).encode()
