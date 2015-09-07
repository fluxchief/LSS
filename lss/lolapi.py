"""
LSS Lol API backend
"""
import urllib2
import json


class LolAPI(object):
    """Awesome LolAPI class"""
    def __init__(self, logger, api_host, area, api_key):
        super(LolAPI, self).__init__()
        self._logger = logger
        self._api_host = api_host
        self._api_key = api_key
        self._area = area

    def get_summoner_by_name(self, name):
        response = urllib2.urlopen(
            'https://%s/api/lol/euw/v1.4/summoner/by-name/%s?api_key=%s' % (
                self._api_host, name, self._api_key))
        return json.loads(response.read()).popitem()[1]

    def get_current_game(self, summoner_id):
        try:
            response = urllib2.urlopen(
                'https://%s/observer-mode/rest/consumer/getSpectatorGameInfo/'
                '%s/%d?api_key=%s' % (
                    self._api_host, self._area, summoner_id, self._api_key))
            return json.loads(response.read())
        except urllib2.HTTPError:
            return None

    def get_champions_by_id(self):
        response = urllib2.urlopen(
            'https://global.api.pvp.net/api/lol/static-data/euw/v1.2/champion?'
            'api_key=%s' % self._api_key)
        ch_data = json.loads(response.read())['data']

        # Format result so that we have a ID-to-champ association
        champs = {}
        for i_k in ch_data:
            i = ch_data[i_k]
            champs[i['id']] = i

        return champs
