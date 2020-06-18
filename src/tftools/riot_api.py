import os
import requests
import json

class RiotApiWrapper():

    def __init__(self, api_key='', region='br1'):
        self.api_key = api_key
        self.region = region

    # Fetch the players from a given tier and division
    def get_league(self, tier='challenger', division='I', page = 1, *args, **kwargs):
        if (self.api_key == ''):
            return (False, 'Set a Riot Api Key before making a request')

        # High elo endpoint
        if (tier.lower() in ['challenger', 'grandmaster', 'master']):
            endpoint = f'''https://{self.region}.api.riotgames.com/tft/league/v1/{tier.lower()}'''

        # Low elo endpoint
        elif (tier.lower() in ['diamond', 'platinum', 'gold', 'silver', 'bronze', 'iron']):
            endpoint = f'''https://{self.region}.api.riotgames.com/tft/league/v1/entries/{tier.upper()}/{division.upper()}'''

        # Tier given does not exist
        else:
            return (False, 'Invalid Tier. Options are: challenger, grandmaster, master, gold, silver, bronze and iron.')

        return self.make_request(endpoint, { 'page': page })

    # Fetch a player profile information
    # Params you can use to fetch the profile: summonerId, accountId, name, puuid
    def get_summoner(self, *args, **kwargs):

        if ('puuid' in kwargs):
            endpoint = f'''https://{self.region}.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/{kwargs['puuid']}'''

        elif ('name' in kwargs):
            endpoint = f'''https://{self.region}.api.riotgames.com/tft/summoner/v1/summoners/by-name/{kwargs['name']}'''

        elif ('accountId' in kwargs):
            endpoint = f'''https://{self.region}.api.riotgames.com/tft/summoner/v1/summoners/by-account/{kwargs['accountId']}'''

        elif ('summonerId' in kwargs):
            endpoint = f'''https://{self.region}.api.riotgames.com/tft/summoner/v1/summoners/{kwargs['summonerId']}'''

        else:
            return (False, 'Invalid player identification. Options are: summonerId, accountId, name and puuid.')

        return self.make_request(endpoint)

    # Fetch details from a given match
    def get_match(self, matchId = None, *args, **kwargs):

        #If a match id was not given return an error
        if (not isinstance(matchId, str)): return (False, 'You must provide a match id.')

        #Otherwise, request match details
        endpoint = f'''https://{self.server}.api.riotgames.com/tft/match/v1/matches/{matchId}'''

        return self.make_request(endpoint)

    # Fetch match history from a given player
    def get_match_history(self, puuid = None, count = 200, *args, **kwargs):

        #If a match id was not given return an error
        if (not isinstance(puuid, str)): return (False, 'You must provide a player id.')

        #Otherwise, request match details
        endpoint = f'''https://{self.server}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids'''

        params = { 'count': count }

        return self.make_request(endpoint, params)

    # Returns the routing server for current region
    @property
    def server(self):

        for i,v in self.servers.items():
            if self.region.upper() in v:
                return i

        return self.region

    # Returns the dictionary with server routing
    @property
    def servers(self):
        return {
        'americas': ['NA1', 'BR1', 'LA1', 'LA2', 'OC1'],
        'asia': ['KR', 'JP1'],
        'europe': ['RU', 'TR1', 'EUN1', 'EUW1']
        }

    # Returns the list of high elo tiers
    @property
    def high_elo(self):
        return ['challenger', 'grandmaster', 'master', 'diamond']

    # Make a request using a given endpoint and params (optional)
    def make_request(self, endpoint, params={}, *args, **kwargs):

        # Request parameters
        query_params = {
            'api_key': self.api_key
        }

        # Include params given
        for i, v in params.items():
            query_params[i] = v

        response = requests.get(endpoint, params=query_params)

        # If the status code is not 200, there was an error
        if response.status_code != 200:

            # In case rate limit was exceeded, return only the Retry-after parameter
            if response.status_code == 429:
                return (False, int((response.headers)['Retry-After']))

            return (False, f'Got error code {response.status_code} at {endpoint} with params {query_params}.')

        # Resquest successful, return response in json format
        else:
            return (True, response.json())
