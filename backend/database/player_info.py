"""
Operations on PlayerInfo.
"""

from shared.database.graphql import graphql

import backend.database.player
import backend.database.map


def get(map_id: str, player_name: str) -> dict:
    """
    Get or create player info for the given player name on the given map ID.
    """

    player_info = graphql("""
        query($map_id: ID!, $player_name: String!) {
            getMap(id: $map_id) {
                playerInfos @cascade(fields: "player") {
                    id
                    player(filter: { name: { eq: $player_name } }) {
                        name
                    }
                    score
                    playtime
                    map {
                        id
                    }
                }
            }
        }
        """, {
            'map_id': map_id,
            'player_name': player_name,
        }
    )['getMap']['playerInfos']

    if not player_info:
        player_info = graphql("""
            mutation($player_info: AddPlayerInfoInput!) {
                addPlayerInfo(input: [$player_info]) {
                    playerInfo {
                        id
                        player {
                            name
                        }
                        score
                        playtime
                        map {
                            id
                        }
                    }
                }
            }
            """, {
                'player_info': {
                    'player': backend.database.player.ref(player_name),
                    'map': backend.database.map.ref(map_id),
                    'score': 0,
                    'playtime': 0
                }
            }
        )['addPlayerInfo']['playerInfo']

    return player_info[0]


def update(player_info: dict) -> None:
    """
    Save the given player_info.
    """

    copy = player_info.copy()
    copy.pop('id')

    graphql("""
        mutation ($input: UpdatePlayerInfoInput!) {
            updatePlayerInfo(input: $input) {
                numUids
            }
        }
        """, {
            'input': {
                'filter': {
                    'id': player_info['id']
                },
                'set': copy
            }
        }
    )


def get_many(maps_id: list[str], players_name: list[str]) -> list[dict]:
    """
    For all maps and players, get player info.
    """

    # Query all existing player info in one single query.

    players_info = []

    result = graphql("""
        query($maps_id: [ID!]!, $players_name: [String!]!) {
            queryMap(filter: { id: $maps_id }) {
                id
                playerInfos @cascade(fields: player) {
                    id
                    player(filter: { name: { in: $players_name }}) {
                        name
                    }
                    score
                    playtime
                }
            }
        }
        """, {
            'maps_id': maps_id,
            'players_name': players_name
        }
    )['queryMap']

    # List all player info found.

    found = set()

    for map_ in result:
        for player_info in map_['playerInfos']:
            found.add((map_['id'], player_info['player']['name']))
            player_info['map'] = backend.database.map.ref(map_['id'])
            players_info.append(player_info)

    # List all missing player info.

    missing = []

    for map_id in maps_id:
        for player_name in players_name:
            if (map_id, player_name) not in found:
                missing.append({
                    'player': backend.database.player.ref(player_name),
                    'map': backend.database.map.ref(map_id),
                    'score': 0,
                    'playtime': 0
                })

    # Add all missing player info in one single query.

    added = graphql("""
        mutation($players_info: [AddPlayerInfoInput!]!) {
            addPlayerInfo(input: $players_info) {
                playerInfo {
                    id
                    player {
                        name
                    }
                    map {
                        id
                    }
                }
            }
        }
        """, {
            'players_info': missing
        }
    )['addPlayerInfo']['playerInfo']

    # Merge the newly added player info to the list of existing player info.

    for player_info in added:
        player_info['score'] = 0
        player_info['playtime'] = 0
        players_info.append(player_info)

    return players_info


def set_many(players_info: list[dict]) -> None:
    """
    Set many player info at once.
    """

    for player_info in players_info:
        update(player_info)
