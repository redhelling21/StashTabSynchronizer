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
import requests

systrayHandler = None


def startup():
    # systrayHandler = systray.run_systray() # to handle systray icon
    profile = get_profile()
    leagues = get_leagues()
    selectedLeague = cfg.loadConfig().get("league")
    if selectedLeague is not None and selectedLeague in leagues:
        appLogger.info("Running with league : " + selectedLeague)
        stashIds = get_stash_ids(selectedLeague)
        appLogger.info(f"Found {len(stashIds)} stashes")
        loop(selectedLeague, stashIds, profile["name"])
    else:
        appLogger.info("No selected league. Exiting...")
        return


def loop(league, stashIds, owner):
    api = POEApi()
    conf = cfg.loadConfig()
    if conf["export"]["mode"] == "local":
        stashExport = write_stash_to_file
    elif conf["export"]["mode"] == "server":
        stashExport = send_stash_to_server
    else:
        appLogger.info("Invalid export mode. Exiting...")
        return
    while True:
        appLogger.info(f"Reading datas from {len(stashIds)} stash tabs")
        count = 1
        for id in stashIds:
            appLogger.info(f"Reading tab {count}/{len(stashIds)} ({stashIds[id]})...")
            appLogger.debug("Reading tab %s, with id %s", stashIds[id], id)
            stash = api.getStashTab(league, id)
            try:
                formattedStash = stashFormatter.getFormattedStash(stash, owner, league)
            except Exception as e:
                appLogger.exception("An exception occurred while formatting stash: %s", str(e))
                formattedStash = None
            if formattedStash:
                stashExport(formattedStash)
            else:
                appLogger.info("Stash '%s' was empty, skipping", stashIds[id])
            count += 1
        appLogger.info("*********************************************************")
        appLogger.info(f"Export finished. Sleeping for {conf['exportInterval']} seconds")
        appLogger.info("*********************************************************")
        time.sleep(conf["exportInterval"])


def get_profile():
    api = POEApi()
    appLogger.debug("Reading the profile")
    return api.getProfile()


def get_leagues():
    api = POEApi()
    leagues = set()
    appLogger.debug("Reading the leagues list")
    characters = api.getCharacters().get("characters", [])
    for character in characters:
        league = character.get("league")
        if league:
            leagues.add(league)
    conf = cfg.loadConfig()
    conf["availableLeagues"] = list(leagues)
    cfg.dumpConfig(conf)
    appLogger.info("Got the available leagues list : %s", str(leagues))
    return leagues


def get_stash_ids(league):
    api = POEApi()
    appLogger.debug("Getting the stashes list for %s", league)
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
    return stashIds


def write_stash_to_file(stash):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{stash[0]['stash']['id']}_{timestamp}.json"
    with open(f"{os.path.dirname(sys.argv[0])}/data/{filename}", "w") as file:
        json.dump(stash, file)
    appLogger.info("Saved the '%s' tab data in %s", stash[0]["stash"]["id"], filename)


def send_stash_to_server(stash):
    conf = cfg.loadConfig()
    mainEndpoint = conf["export"]["endpoint"]
    response = requests.post(f"{mainEndpoint}/api/Stashs/UpdateCompleteStashContent/{stash[0]['stash']['id']}", json=stash, verify=False)
    if response.status_code >= 300:
        appLogger.error("POST request failed with status code:", response.status_code)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        appLogger.info("Starting the tool")
        startup()
    else:
        subLogger.info("Got a callback from the auth server : %s", str(sys.argv[1]))
        oauth.send_callback_to_main_instance(sys.argv[1])
    sys.exit()
