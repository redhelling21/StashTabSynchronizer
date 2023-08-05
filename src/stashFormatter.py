import re
from logger import appLogger
from poeApi import POEApi
from confighandler import config as cfg

fieldHandlers = {
    "sockets": lambda item, value: socketsHandler(item, value),
    "properties": lambda item, value: propertiesHandler(item, value),
    "requirements": lambda item, value: requirementsHandler(item, value),
    "frameType": lambda item, value: rarityHandler(item, value),
    "additionalProperties": lambda item, value: propertiesHandler(item, value),
}

removeList = ["verified", "w", "h", "x", "y", "inventoryId", "socketedItems"]


def socketsHandler(item, value):
    total = sum(1 for socket in value)
    item["sockets.number"] = total
    item["sockets.red"] = sum(1 for socket in value if socket["sColour"] == "R")
    item["sockets.green"] = sum(1 for socket in value if socket["sColour"] == "G")
    item["sockets.blue"] = sum(1 for socket in value if socket["sColour"] == "B")
    item["sockets.white"] = sum(1 for socket in value if socket["sColour"] == "W")
    item["links"] = total - max(value, key=lambda x: x["group"])["group"]


def nameHandler(item):
    if item.get("name") and item["name"] == "":
        if item.get("typeLine"):
            item["name"] = item["typeLine"]
        elif item.get("baseType"):
            item["name"] = item["baseType"]
            item["typeLine"] = item["baseType"]


def stackSizeHandler(item):
    if item.get("stackSize") is not None and item.get("properties.StackSize") is None:
        item["properties.StackSize"] = f"{item.get('stackSize')}/{item.get('maxStackSize')}"
    elif item.get("stackSize") is None and item.get("properties.StackSize") is not None:
        stackSizeDatas = item.get("properties.StackSize").split("/")
        item["stackSize"] = int(stackSizeDatas[0])
        item["maxStackSize"] = int(stackSizeDatas[1])


def propertiesHandler(item, value):
    for prop in value:
        if prop["values"]:
            name = prop["name"]
            newKey = f"{re.sub(r'[^a-zA-Z]', '', name.replace(' ', ''))}"
            item[f"properties.{newKey}"] = prop["values"][0][0]


def requirementsHandler(item, value):
    for prop in value:
        if prop["values"]:
            name = prop["name"]
            newKey = f"requirements.{re.sub(r'[^a-zA-Z]', '', name.lower().replace(' ', ''))}"
            item[newKey] = prop["values"][0][0]


def rarityHandler(item, value):
    if value == 0:
        item["rarity"] = "normal"
    elif value == 1:
        item["rarity"] = "magic"
    elif value == 2:
        item["rarity"] = "rare"
    elif value == 3:
        item["rarity"] = "unique"
    else:
        item["rarity"] = "special"


def mapStashHandler(league, stash, children):
    method = cfg.loadConfig().get("specialStashesHandling").get("map")
    items = list()
    if method is None or method == "partial":
        appLogger.debug("Handling map stash with partial data recovery")
        for child in children:
            item = {}
            metadata = child["metadata"]
            item["icon"] = metadata["map"]["image"]
            item["league"] = league
            item["baseType"] = metadata["map"]["name"]
            item["name"] = metadata["map"]["name"]
            item["properties.StackSize"] = f"{metadata['items']}/999"
            if metadata["map"].get("tier"):
                item["tier"] = metadata["map"]["tier"]
                item["properties.MapTier"] = metadata["map"]["tier"]
            else:
                item["tier"] = 16
                item["properties.MapTier"] = 16
            if metadata["map"]["section"] == "unique":
                item["rarity"] = "unique"
            elif metadata["map"]["section"] == "special":
                item["rarity"] = "special"
            else:
                item["rarity"] = "normal"
            items.append(item)
        return items
    elif method == "full":
        appLogger.info("Handling map stash with full data recovery is not supported, as it takes around 20 minutes by itself")
        return None
    elif method == "skip":
        appLogger.info("Skipping map tab")
        return None
    else:
        appLogger.error("specialStashesHandling.map has an unknown value")
        return None


def uniqueStashHandler(league, stash, children):
    method = cfg.loadConfig().get("specialStashesHandling").get("unique")
    api = POEApi()
    items = list()
    if method is None or method == "partial":
        appLogger.error("Partial mode not supported for unique stash tab")
        return None
    elif method == "full":
        appLogger.info("Handling unique stash with full data recovery")
        for child in children:
            appLogger.debug(f"Querying child {stash['id']}/{child['id']}")
            childStash = api.getStashTab(league, f"{stash['id']}/{child['id']}")
            items = items + childStash["stash"]["items"]
        return items
    elif method == "skip":
        appLogger.info("Skipping unique tab")
        return None
    else:
        appLogger.error("specialStashesHandling.unique has an unknown value")
        return None


def defaultHandler(item, key, value):
    if key not in removeList:
        item[key] = value
    return


def getFormattedStash(json, owner, league):
    api = POEApi()
    stash = json["stash"]
    items = list()
    children = stash.get("children")
    if children:
        if stash.get("type") == "MapStash":
            items = mapStashHandler(league, stash, children)
        elif stash.get("type") == "UniqueStash":
            items = uniqueStashHandler(league, stash, children)
        else:
            appLogger.debug("Detected children from an unknown stash type, retrieving substashes")
            for child in children:
                appLogger.debug(f"Querying child {stash['id']}/{child['id']}")
                childStash = api.getStashTab(league, f"{stash['id']}/{child['id']}")
                items = items + childStash["stash"]["items"]
        del stash["children"]
    else:
        items = stash["items"]
        del stash["items"]
    formattedItems = list()
    for item in items:
        formattedItem = {}
        formattedItem["stash.name"] = stash["name"]
        formattedItem["owner"] = owner
        for key in item:
            if key in fieldHandlers:
                fieldHandlers[key](formattedItem, item[key])
            else:
                defaultHandler(formattedItem, key, item[key])
        nameHandler(formattedItem)
        formattedItems.append(formattedItem)
    stash["items"] = formattedItems
    return stash
