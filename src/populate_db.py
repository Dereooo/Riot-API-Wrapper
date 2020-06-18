# Main script for non stop fetching of information from Riot's API

import os
import json
import time
import threading

from tftools.riot_api import RiotApiWrapper

def match_grab_loop(api, tiers_to_fetch = [], regions_to_fetch = [], game_version = None):

    try:
        def handle_error(response):
            if isinstance(response, int):
                print(f'Rate limit exceeded. Sleeping for {response} seconds.')
                time.sleep(response)
            else:
                print('Error ', response)

        # For each tier and region given as params
        for region in regions_to_fetch:
            print(f'Starting region {region}.')

            # Change the server for the requests
            api.region = region

            for tier in tiers_to_fetch:
                print(f'Starting tier {tier} from {region}.')

                # Fetch league entry
                result, response = api.get_league(tier)

                if not result:
                    handle_error(response)
                    continue

                # High elo (m, gm, cl) has a different response format
                if tier.lower() != 'diamond':
                    response = response['entries']

                player_id_list = map(lambda x: x['summonerId'], response)

                # For each player on the list
                for player_id in player_id_list:
                    print(f'Starting {tier} player {player_id} from {region}.')

                    # Look for the player in the db
                    player_doc = db.players.find_one({ 'id': player_id })

                    # if not in our db, fetch their puuid
                    if not player_doc:

                        # Get player puuid
                        result, player_doc = api.get_summoner(summonerId = player_id)

                        if not result:
                            handle_error(response)
                            continue

                        player_doc['region'] = region
                        player_doc['tier'] =  tier

                        db.players.insert_one(player_doc)

                    player_puuid = player_doc['puuid']

                    # Get player match history (last 200)
                    result, response = api.get_match_history(player_puuid)

                    if not result:
                        handle_error(response)
                        continue

                    # Filter the matches that are not in the db
                    player_match_history = response

                    # For each match in the players match history
                    for match in player_match_history:

                        # If match is already in db, skip to the next one
                        match_document = db.matches.find_one( { 'metadata.match_id' : match } )

                        if match_document:
                            print(f'Match {match} is already in the database.')
                            continue

                        else:
                            print(f'Match {match} not in database. Fetching match information...')

                        # Fetch match information
                        result, response = api.get_match(match)

                        if not result:
                            handle_error(response)
                            continue

                        match_info = response

                        # If a game version was provided, move on to the next player once you reach a different version
                        if game_version:
                            match_version = match_info['info']['game_version']
                            if not match_version.lower().replace('version ','').startswith(game_version):
                                break

                        db.matches.insert_one(match_info)
                        print(f'Match {match} added')
    except:
        pass

    match_grab_loop(api,tiers_to_fetch, regions_to_fetch, game_version)


if __name__ == '__main__':
    
    # Set up your mongodb as db
    from pymongo import MongoClient
    client = MongoClient()
    db = client['tfstacticsDB']

    # Set your riot api key as an environment variable
    RIOT_API_KEY = os.environ['RIOT_API_KEY']

    # List of threads
    thread_list = []

    # Create and start a thread for each server
    for regions_list in RiotApiWrapper().servers.values():
        new_riot_api = RiotApiWrapper(RIOT_API_KEY)
        new_thread = threading.Thread(
            target=match_grab_loop,
            args=(new_riot_api, RiotApiWrapper().high_elo, regions_list, '10.12')
            )
        thread_list.append(new_thread)
        new_thread.start()
