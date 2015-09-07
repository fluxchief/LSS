"""
League Summoner Stalk [LSS]
"""
import ConfigParser
import logging
import time

import lolapi
import pushover


def run_lss(config_file, summoner, on_detect=None, debug_level=logging.DEBUG):
    # Setup logging
    logger = logging.getLogger("LSS")
    logger.setLevel(debug_level)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Read config file
    parser = ConfigParser.ConfigParser()
    parser.read(config_file)

    # Load backends
    logger.debug("Loading backends")
    pushover_backend = pushover.PushoverBackend(
        logger,
        parser.getboolean('pushover', 'enabled'),
        parser.get('pushover', 'user_token'),
        parser.get('pushover', 'app_token')
    )

    lolapi_backend = lolapi.LolAPI(
        logger,
        parser.get('lol', 'api_host'),
        parser.get('lol', 'area'),
        parser.get('lol', 'api_key')
    )

    delay = parser.getint('general', 'delay')

    # Run LSS
    # Obtain user
    logger.debug("Loading summoner")
    try:
        summoner = lolapi_backend.get_summoner_by_name(summoner)
        logger.debug(
            "Summoner found, checking for: %s [level: %d]",
            summoner['name'],
            summoner['summonerLevel']
        )
    except:
        logger.exception(
            "Loading the summoner failed, API credetials invalid?")
        return

    # Obtain champions
    champs = lolapi_backend.get_champions_by_id()

    pushover_backend.send_message(
        title="LSS running",
        message="Checking for %s [level %d]" % (
            summoner['name'], summoner['summonerLevel']),
    )

    # Stores the game ID of all games already shown
    sent_games = set()
    while True:
        game = lolapi_backend.get_current_game(summoner['id'])
        if game and game['gameId'] not in sent_games:
            logger.info("Summoner plays a new game. ID: %d", game['gameId'])
            sent_games.add(game['gameId'])

            # Format message:
            bans = [
                champs[x['championId']]['name']
                for x in game['bannedChampions']]
            bans = ' '.join(bans)

            message = "Mode: %s (%s)\n" % (game['gameMode'], game['gameType'])
            if bans:
                message += bans + "\n"

            teams = {}
            for i in game['participants']:
                # Replace champion ID with the name
                i['champion'] = champs[i['championId']]['name']
                try:
                    teams[i["teamId"]].append(i)
                except KeyError:
                    teams[i["teamId"]] = [i]

            for team, players in teams.iteritems():
                message += "============================\n"
                message += "Team %s:\n" % team
                message += "============================\n"
                for player in players:
                    if player['summonerName'] == summoner['name']:
                        message += "<b>%s played by %s</b>\n" % (
                            player['champion'], player['summonerName'])
                    else:
                        message += "%s played by %s\n" % (
                            player['champion'], player['summonerName'])

            # Show message
            logger.info(message)
            pushover_backend.send_message(
                title="Game found",
                message=message,
                priority=0)

            if on_detect:
                on_detect()

        else:
            logger.info("No new game found")

        time.sleep(delay)
