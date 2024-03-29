"""
Implement /search.
"""

import re

from flask import request, render_template, url_for
from shared.database.graphql import graphql, serialize_string, RawString

import frontend.components.paginator
import frontend.components.section_tabs
import frontend.components.top_tabs

MAX_SEARCH_RESULTS = 100

def search(template_name, section_tabs_active, operation_name, query_name):
    """
    Search for the given category.
    """

    query = request.args.get('q', default='', type = str)

    if query == '':
        # If nothing is done, an empty query will juste return all entries.
        # There is no real use case for such query so instead just return
        # nothing to avoid overcharging dgraph.

        counts = {
            'players': 0,
            'clans': 0,
            'servers': 0
        }

        results = []
    else:
        # Count the number of results for players, clans and servers.

        query_escaped = re.escape(serialize_string(query))

        counts_results = graphql("""
            query($regexp: String!) {
                aggregatePlayer(filter: { name: { regexp: $regexp }}) {
                    count
                }
                aggregateClan(filter: { name: { regexp: $regexp }}) {
                    count
                }
                aggregateGameServer(filter: { name: { regexp: $regexp }}) {
                    count
                }
            }
            """, {
                'regexp': RawString('/.*' + query_escaped + '.*/i')
            }
        )

        counts = {
            'players': counts_results['aggregatePlayer']['count'],
            'clans': counts_results['aggregateClan']['count'],
            'servers': counts_results['aggregateGameServer']['count']
        }

        # Build the various regexp that are going to be given to dgraph to perform
        # the actual search.

        regexps = (
            '/^' + query_escaped + '$/i',
            '/^' + query_escaped + '.+/i',
            '/.+' + query_escaped + '$/i',
            '/.+' + query_escaped + '.+/i'
        )

        results = []

        for regexp in regexps:
            if len(results) < MAX_SEARCH_RESULTS:
                results.extend(graphql("""
                    query searchPlayers(
                        $regexp: String!,
                        $first: Int!
                    ) {
                        queryPlayer(
                            filter: { name: { regexp: $regexp }},
                            first: $first
                        ) {
                            name
                            clan {
                                name
                            }
                        }
                    }

                    query searchClans(
                        $regexp: String!,
                        $first: Int!
                    ) {
                        queryClan(
                            filter: { name: { regexp: $regexp }},
                            first: $first,
                            order: { desc: playersCount }
                        ) {
                            name
                            playersCount
                        }
                    }

                    query searchServers(
                        $regexp: String!,
                        $first: Int!
                    ) {
                        queryGameServer(
                            filter: { name: { regexp: $regexp }},
                            first: $first,
                            order: { desc: numClients }
                        ) {
                            address
                            name
                            map {
                                name
                                gameType {
                                    name
                                }
                            }
                            numClients
                            maxClients
                        }
                    }
                    """, {
                        'regexp': RawString(regexp),
                        'first': MAX_SEARCH_RESULTS - len(results)
                    },
                    operation_name
                )[query_name])

    # Build the page.

    urls = {
        'players': url_for('players-search', q = query),
        'clans': url_for('clans-search', q = query),
        'servers': url_for('servers-search', q = query)
    }

    # If the number of results exceed the maximum number of results, add a small
    # '+' to indicate that too many results were found.

    for key, count in counts.items():
        if count > MAX_SEARCH_RESULTS:
            counts[key] = f'{MAX_SEARCH_RESULTS}+'

    section_tabs = frontend.components.section_tabs.init(
        section_tabs_active, counts, urls
    )

    return render_template(
        template_name,

        top_tabs = frontend.components.top_tabs.init({
            'type': 'custom',
            'links': [{
                'name': 'Search'
            }, {
                'name': query
            }]
        }),

        section_tabs = section_tabs,
        query = query,
        results = results,
    )


def route_players_search():
    """
    List of players matching the search query.
    """

    return search('search_players.html', 'players', 'searchPlayers', 'queryPlayer')


def route_clans_search():
    """
    List of clans matching the search query.
    """

    return search('search_clans.html', 'clans', 'searchClans', 'queryClan')


def route_servers_search():
    """
    List of servers matching the search query.
    """

    return search('search_servers.html', 'servers', 'searchServers', 'queryGameServer')
