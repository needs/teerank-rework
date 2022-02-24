"""
Implement rank() function.
"""

import logging
from itertools import combinations, product

from shared.player import Player

def _elo_delta(score1: int, elo1: int, score2: int, elo2: int) -> int:
    """
    Classic ELO formula for two players, return the ELO delta for both players.
    """

    k_factor = 25

    if score1 < score2:
        result = 0.0
    elif score1 == score2:
        result = 0.5
    else:
        result = 1.0

    delta = min(400.0, max(-400.0, elo1 - elo2))
    expected = 1.0 / (1.0 + pow(10.0, -delta / 400.0))

    return k_factor * (result - expected)


def rank(old: dict, new: dict) -> bool:
    """
    Rank players given the old and new server state.
    """

    # Both old and new must be valid to be able to compare them.

    if not old:
        return False

    # If game type is not rankable, or game type changed, or map changed, then
    # it makes no sens to rank players.

    if new['game_type'] not in ('CTF', 'DM', 'TDM') or \
        old['game_type'] != new['game_type'] or \
        old['map_name'] != new['map_name']:
        return False

    # Create a list of all players that are ingame in both old and new state.

    old_keys = { key for key, client in old['clients'].items() if client['ingame'] }
    new_keys = { key for key, client in new['clients'].items() if client['ingame'] }
    keys = list(old_keys.intersection(new_keys))

    if len(keys) <= 1:
        return False

    # Player score is the difference between its old score and new score.
    #
    # If the sum of all players scores in old state is bigger than the sum of
    # all players scores in new state, then we don't rank the game because there
    # is a high chance that a new game started.

    scores = [ new['clients'][key]['score'] - old['clients'][key]['score'] for key in keys ]

    if sum(scores) <= 0:
        return False

    # Now that all sanity checks have been done, compute players new ELO.
    #
    # New ELO is computed by matching all players against each other.  The
    # winner is the one with the highest score difference.  The average ELO
    # delta of all matches of a player is added to the player original ELO.
    #
    # We do this for each combination of game type and map name.

    for game_type, map_name in product((new['game_type'], None), (new['map_name'], None)):

        elos = [ Player.get_elo(key, game_type, map_name) for key in keys ]
        deltas = [0] * len(keys)

        for i, j in combinations(range(len(keys)), 2):
            delta = _elo_delta(scores[i], elos[i], scores[j], elos[j])
            deltas[i] += delta
            deltas[j] -= delta

        for i, key in enumerate(keys):
            new_elo = elos[i] + deltas[i] / (len(keys) - 1)
            Player.set_elo(key, game_type, map_name, new_elo)

            logging.info(
                'Gametype: %s: map %s: player %s: new_elo: %d -> %d',
                game_type, map_name, key, elos[i], new_elo
            )

    return True
