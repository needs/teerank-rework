"""
Implement /players.
"""

from flask import request, render_template
from shared.database.graphql import graphql

import frontend.components.paginator
import frontend.components.section_tabs
import frontend.components.top_tabs


def route_players():
    """
    List players for a specific game type and map.
    """

    game_type = request.args.get('gametype', default=None, type = str)
    map_name = request.args.get('map', default=None, type = str)

    section_tabs = frontend.components.section_tabs.init('players')
    paginator = frontend.components.paginator.init(section_tabs['players']['count'])

    players = graphql("""
        query($first: Int!, $offset: Int!) {
            queryPlayer(first: $first, offset: $offset) {
                name
                clan {
                    name
                }
            }
        }
        """, {
            'offset': paginator['offset'],
            'first': paginator['first']
        }
    )['queryPlayer']

    for i, player in enumerate(players):
        player['rank'] = paginator['offset'] + i + 1

    return render_template(
        'players.html',

        top_tabs = frontend.components.top_tabs.init({
            'type': 'gametype',
            'gametype': game_type,
            'map': map_name
        }),

        section_tabs = section_tabs,
        paginator = paginator,

        game_type=game_type,
        map_name=map_name,
        players = players,
    )
