"""
Test /about.
"""

def test_route_about(client):
    """
    Test /about.
    """
    assert client.get('/about').status_code == 200
