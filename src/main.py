from auth import oauth, token
import systray
import sys
import poeApi
from confighandler import config as cfg
import time
from datetime import datetime
import json
import os
from logger import appLogger, subLogger

systrayHandler = None

def startup():
    systrayHandler = systray.run_systray()
    leagues = getLeagues()
    selectedLeague = cfg.loadConfig().get("league")
    if selectedLeague is not None and selectedLeague in leagues:
        stashIds = getStashIds(selectedLeague)
        loop(selectedLeague, stashIds)
    else:
        return

def loop(league, stashIds):
    while True:
        appLogger.info("Retrieving the stash tabs datas")
        for id in stashIds:
            stash = poeApi.getStashTab(league, id)
            stashName = stash["stash"]["name"]
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{stashName}_{timestamp}.json"
            with open(f"{os.path.dirname(sys.argv[0])}/data/{filename}", "w") as file:
                json.dump(stash, file)
            appLogger.info("Saved the '%s' tab data in %s", stashName, filename)
        appLogger.info("Sleeping for 600 seconds")
        time.sleep(600)


def getLeagues():
    leagues = set()
    appLogger.debug("Retrieving the leagues list")
    characters = poeApi.getCharacters().get("characters", [])
    for character in characters:
        league = character.get("league")
        if league:
            leagues.add(league)
    conf = cfg.loadConfig()
    conf["availableLeagues"] = list(leagues)
    cfg.dumpConfig(conf)
    appLogger.info("Retrieved the available leagues list : %s", str(leagues))
    return leagues

def getStashIds(league):
    appLogger.debug("Retrieving the stashes list for %s", league)
    stashes = poeApi.getStashTabsList(league).get("stashes", [])
    stashIds = set()
    for stash in stashes:
        id = stash.get("id")
        if id:
            stashIds.add(id)
    appLogger.info("Retrieved the available stashes list for %s : %s", str(league), str(stashIds))
    return stashIds

if __name__ == '__main__':
    if len(sys.argv) == 1:
        appLogger.info("Starting the tool")
        startup()
    else:
        subLogger.info("Got a callback from the auth server : %s", str(sys.argv[1]))
        oauth.send_callback_to_main_instance(sys.argv[1])
    sys.exit()