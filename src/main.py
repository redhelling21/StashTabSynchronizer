from auth import oauth
import systray
import sys
from poeApi import POEApi
from confighandler import config as cfg
import time
from datetime import datetime
import json
import os
from logger import appLogger, subLogger
import stashFormatter

systrayHandler = None


def startup():
    systrayHandler = systray.run_systray()
    profile = getProfile()
    leagues = getLeagues()
    selectedLeague = cfg.loadConfig().get("league")
    if selectedLeague is not None and selectedLeague in leagues:
        stashIds = getStashIds(selectedLeague)
        loop(selectedLeague, stashIds, profile["name"])
    else:
        return


def loop(league, stashIds, owner):
    api = POEApi()
    while True:
        appLogger.info("Retrieving the stash tabs datas")
        for id in stashIds:
            stash = api.getStashTab(league, id)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{stashIds[id]}_{timestamp}.json"
            with open(f"{os.path.dirname(sys.argv[0])}/data/{filename}", "w") as file:
                json.dump(stashFormatter.getFormattedStash(stash, owner, league), file)
            appLogger.info("Saved the '%s' tab data in %s", stashIds[id], filename)
        appLogger.info("Sleeping for 600 seconds")
        time.sleep(600)


def getProfile():
    api = POEApi()
    appLogger.debug("Retrieving the profile")
    return api.getProfile()


def getLeagues():
    api = POEApi()
    leagues = set()
    appLogger.debug("Retrieving the leagues list")
    characters = api.getCharacters().get("characters", [])
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
    api = POEApi()
    appLogger.debug("Retrieving the stashes list for %s", league)
    stashes = api.getStashTabsList(league).get("stashes", [])
    stashIds = {}
    for stash in stashes:
        children = stash.get("children")
        if children:  # Handle stash folders
            for child in children:
                id = child.get("id")
                if id:
                    stashIds[id] = f"{stash.get('name')}.{child.get('name')}"
        else:
            id = stash.get("id")
            if id:
                stashIds[id] = stash.get("name")
    appLogger.info("Retrieved the available stashes list for %s : %s", str(league), str(stashIds))
    return stashIds


if __name__ == "__main__":
    if len(sys.argv) == 1:
        appLogger.info("Starting the tool")
        startup()
    else:
        subLogger.info("Got a callback from the auth server : %s", str(sys.argv[1]))
        oauth.send_callback_to_main_instance(sys.argv[1])
    sys.exit()
