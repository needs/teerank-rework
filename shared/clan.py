"""
Implement clan related functions.
"""

from gql import gql
from shared.database import graphql


_GQL_UPDATE_CLANS = gql(
    """
    mutation ($clans: [AddClanInput!]!) {
        addClan(input: $clans, upsert: true) {
            clan {
                name
            }
        }
    }
    """
)

def upsert(clans):
    """
    Add or update the given clans.
    """

    graphql.execute(
        _GQL_UPDATE_CLANS,
        variable_values = { 'clans': clans }
    )


_GQL_QUERY_CLANS_PLAYERS_COUNT = gql(
    """
    query ($clans: [String]!) {
        queryClan(filter: {name: {in: $clans}}) {
            name

            playersAggregate {
                count
            }
        }
    }
    """
)

def get_player_count(clans):
    """
    Return a dictionary where for each given clans is associated its player
    count.
    """

    if not clans:
        return {}

    clans = graphql.execute(
        _GQL_QUERY_CLANS_PLAYERS_COUNT,
        variable_values = { 'clans': clans }
    )['queryClan']

    return { clan['name']: clan['playersAggregate']['count'] for clan in clans }


_GQL_UPDATE_CLAN_PLAYERS_COUNT = gql(
    """
    mutation ($clan: String!, $count: Int) {
        updateClan(input: {filter: {name: {eq: $clan}}, set: {playersCount: $count}}) {
            clan {
                name
            }
        }
    }
    """
)

def set_player_count(clan, count):
    """
    Set player count for the given clan.
    """

    graphql.execute(
        _GQL_UPDATE_CLAN_PLAYERS_COUNT,
        variable_values = { 'clan': clan, 'count': count }
    )
