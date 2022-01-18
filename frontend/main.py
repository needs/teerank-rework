"""
Launch frontend application.
"""

from flask import Flask, render_template
from flask import request

import shared.player
from shared.database import key_to_string, key_from_string

app = Flask(__name__)

@app.route("/players")
def route_players():
    """
    List players for a specific game type and map.
    """

    game_type = request.args.get('gametype', default='CTF', type = str)
    map_name = request.args.get('map', default=None, type = str)

    game_type_key = key_from_string(game_type)
    map_name_key = key_from_string(map_name)

    main_game_types = (
        'CTF',
        'DM',
        'TDM'
    )

    players_count = shared.player.players_count(game_type_key, map_name_key)
    players_key_elo = shared.player.players_by_rank(game_type_key, map_name_key, 0, 100)
    players = []

    for rank, key_elo in enumerate(players_key_elo):
        key = key_elo[0].decode()
        elo = key_elo[1]

        players.append({
            'rank': rank,
            'name': key_to_string(key),
            'elo': int(elo)
        })

    return render_template(
        'base.html',
        game_type=game_type,
        map_name=map_name,
        players=players,
        players_count=players_count,
        main_game_types=main_game_types
    )


@app.route('/maps')
def route_maps():
    """
    List of maps for a given game type.
    """


@app.route('/gametypes')
def route_gametypes():
    """
    List of all game types.
    """
