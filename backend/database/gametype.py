"""
Operations on type GameType.
"""

from shared.database.graphql import graphql


def ref(gametype_id):
    """Create a gametype reference from the given gametype ID."""
    return { 'id': gametype_id }


_ALL_FIELDS = "id, name"

def get(name: str, fields: str = None) -> dict:
    """
    Get GameType with the given name and the given fields.

    GameType is created if it does not exist yet.
    """

    if fields is None:
        fields = _ALL_FIELDS

    if fields == 'id' and name is None and get.id_none is not None:
        return get.id_none

    gametype = graphql("""
        query($name: String) {
            queryGameType(filter: { name: { eq: $name } }) {
                """ + fields + """
            }
        }
        """, {
            'name': name,
        }
    )['queryGameType']

    if not gametype:
        gametype = graphql("""
            mutation($gameType: AddGameTypeInput!) {
                addGameType(input: [$gameType]) {
                    gameType {
                        """ + fields + """
                    }
                }
            }
            """, {
                'gameType': {
                    'name': name
                },
            }
        )['addGameType']['gameType']

    if fields == 'id' and name is None:
        get.id_none = gametype[0]

    return gametype[0]

get.id_none = None


def id_none():
    """
    ID of the gametype with a None name.
    """
    return get(None, 'id')['id']
