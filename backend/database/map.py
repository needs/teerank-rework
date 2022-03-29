"""
Operations on type Map.
"""

from shared.database.graphql import graphql

from backend.database.gametype import id_none as gametype_id_none, ref as gametype_ref


def ref(map_id):
    """Create a map reference from the given map ID."""
    return { 'id': map_id }


_ALL_FIELDS = "id, name, gameType { id }"

def get(gametype_id: str, name: str, fields: str = None) -> dict:
    """
    Get Map fields with the given name for the given gametype ID.

    Create the map if it does not exist yet.
    """

    if fields is None:
        fields = _ALL_FIELDS

    if fields == 'id' \
        and gametype_id == gametype_id_none() \
        and name is None \
        and get.id_none is not None:
        return get.id_none

    value = graphql("""
        query($gametype_id: ID!, $map_name: String) {
            getGameType(id: $gametype_id) {
                maps(filter: { name: {eq: $map_name }}) {
                    """ + fields + """
                }
            }
        }
        """, {
            'gametype_id': gametype_id,
            'map_name': name,
        }
    )['getGameType']['maps']

    if not value:
        value = graphql("""
            mutation($map: AddMapInput!) {
                addMap(input: [$map]) {
                    map {
                        """ + fields + """
                    }
                }
            }
            """, {
                'map': {
                    'name': name,
                    'gameType': gametype_ref(gametype_id)
                },
            }
        )['addMap']['map']

    if fields == 'id' \
        and gametype_id == gametype_id_none() \
        and name is None:
        get.id_none = value[0]

    return value[0]

get.id_none = None


def query(map_id: str, fields: str = None) -> str:
    """
    Query map info.
    """

    if fields is None:
        fields = _ALL_FIELDS

    return graphql("""
        query($map_id: ID!) {
            getMap(id: $map_id) {
                """ + fields + """
            }
        }
        """, {
            'map_id': map_id
        }
    )['getMap']
