import re
import poeApi
from collections import defaultdict
from logger import appLogger
from poeApi import POEApi

fieldHandlers = {
    "sockets": lambda item, value: socketsHandler(item, value),
    "properties": lambda item, value: propertiesHandler(item, value),
    "requirements": lambda item, value: requirementsHandler(item, value),
    "frameType": lambda item, value: rarityHandler(item, value),
}

removeList = ["verified", "w", "h", "typeLine", "x", "y", "inventoryId"]

def socketsHandler(item, value):
    total = sum(1 for socket in value)
    item["sockets.number"] = total
    item["sockets.red"] = sum(1 for socket in value if socket["sColour"] == "R")
    item["sockets.green"] = sum(1 for socket in value if socket["sColour"] == "G")
    item["sockets.blue"] = sum(1 for socket in value if socket["sColour"] == "B")
    item["sockets.white"] = sum(1 for socket in value if socket["sColour"] == "W")
    item["links"] = total - max(value, key=lambda x: x["group"])["group"] + 1

def propertiesHandler(item, value):
    for prop in value:
        if prop["values"]:
            name = prop["name"]
            newKey = f"{re.sub(r'[^a-zA-Z]', '', name.lower().replace(' ', ''))}"
            item[newKey] = prop["values"][0][0]

def requirementsHandler(item, value):
    for prop in value:
        if prop["values"]:
            name = prop["name"]
            newKey = f"requirements.{re.sub(r'[^a-zA-Z]', '', name.lower().replace(' ', ''))}"
            item[newKey] = prop["values"][0][0]

def rarityHandler(item, value):
    if value == 0 :
        item["rarity"] = "normal"
    elif value == 1 :
        item["rarity"] = "magic"
    elif value == 2 :
        item["rarity"] = "rare"
    elif value == 3 :
        item["rarity"] = "unique"

def mapTabHandler(items):
    base_type_counts = defaultdict(int)
    for item in items:
        base_type = item.get("baseType")
        if base_type: base_type_counts[base_type] += 1

    # Store the first occurrence of each "baseType" and add the count as a new field
    unique_items = []
    for item in items:
        base_type = item.get("baseType")
        if base_type and base_type_counts[base_type] > 0:
            unique_item = item.copy()
            unique_item["stackSize"] = base_type_counts[base_type]
            unique_items.append(unique_item)
            base_type_counts[base_type] = 0
    return unique_items

def defaultHandler(item, key, value):
    if key not in removeList:
        item[key] = value
    return

def getFormattedStash(json, owner, league):
    api = POEApi()
    stash = json["stash"]
    children = stash.get("children")
    if children:
        appLogger.debug("Detected children, retrieving substashes")
        items = list()
        for child in children:
            appLogger.debug(f"Querying child {stash['id']}/{child['id']}")
            childStash = api.getStashTab(league, f"{stash['id']}/{child['id']}")
            items = items + childStash["stash"]["items"]
        if stash["type"] == "MapStash":
            items = mapTabHandler(items)
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
        formattedItems.append(formattedItem)
    stash["items"] = formattedItems
    return stash
