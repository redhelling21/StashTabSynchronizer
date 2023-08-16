import re
from logger import appLogger
from poeApi import POEApi
from confighandler import config as cfg
from datetime import datetime

fieldHandlers = {
    "sockets": lambda item, value: sockets_handler(item, value),
    "properties": lambda item, value: nested_values_handler(item, value, "comparableProperties", "searchableProperties", handle_special_properties),
    "requirements": lambda item, value: nested_values_handler(
        item, value, "comparableRequirements", "searchableRequirements", handle_special_requirements
    ),
    "frameType": lambda item, value: rarity_handler(item, value),
    "additionalProperties": lambda item, value: nested_values_handler(
        item, value, "comparableProperties", "searchableProperties", handle_special_properties
    ),
    "enchantMods": lambda item, value: mod_values_handler(item, value, "comparableEnchantMods", "searchableEnchantMods"),
    "explicitMods": lambda item, value: mod_values_handler(item, value, "comparableExplicitMods", "searchableExplicitMods"),
    "implicitMods": lambda item, value: mod_values_handler(item, value, "comparableImplicitMods", "searchableImplicitMods"),
    "utilityMods": lambda item, value: mod_values_handler(item, value, "comparableUtilityMods", "searchableUtilityMods"),
    "craftedMods": lambda item, value: mod_values_handler(item, value, "comparableCraftedMods", "searchableCraftedMods"),
    "fracturedMods": lambda item, value: mod_values_handler(item, value, "comparableFracturedMods", "searchableFracturedMods"),
    "veiledMods": lambda item, value: mod_values_handler(item, value, "comparableVeiledMods", "searchableVeiledMods"),
}

removeList = [
    "id",
    "folder",
    "verified",
    "w",
    "h",
    "x",
    "y",
    "inventoryId",
    "socketedItems",
    "metadata",
    "artFilename",
    "nextLevelRequirements",
    "hybrid",
    "incubatedItem",
    "flavourTextParsed",
]


def sockets_handler(item, value):
    total = len(value)
    item["sockets"] = {}
    item["sockets"]["number"] = total
    item["sockets"]["red"] = sum(1 for socket in value if socket["sColour"] == "R")
    item["sockets"]["green"] = sum(1 for socket in value if socket["sColour"] == "G")
    item["sockets"]["blue"] = sum(1 for socket in value if socket["sColour"] == "B")
    item["sockets"]["white"] = sum(1 for socket in value if socket["sColour"] == "W")
    item["sockets"]["abyss"] = sum(1 for socket in value if socket["sColour"] == "A")
    item["links"] = total - max(value, key=lambda x: x["group"])["group"]


def name_handler(item):
    if item.get("name") and item["name"] == "":
        if item.get("typeLine"):
            item["name"] = item["typeLine"]
        elif item.get("baseType"):
            item["name"] = item["baseType"]
            item["typeLine"] = item["baseType"]


def handle_special_requirements(item, prop):
    return False


def handle_special_properties(item, prop):
    if prop["name"] == "Stack Size":
        return True
    elif prop["name"] == "Experience":
        return True
    else:
        return False


def nested_values_handler(item, value, comparableCatName, searchableCatName, handleSpecialCases):
    if item.get(comparableCatName) is None:
        item[comparableCatName] = list()
    if item.get(searchableCatName) is None:
        item[searchableCatName] = list()
    for prop in value:
        # Check proper format
        if isinstance(prop, dict) and prop.get("values") is not None:
            if handleSpecialCases(item, prop):
                continue
            newReq = {}
            newReq["name"], count = re.subn(r"{\d+}", "X", prop["name"])
            # Case where there is only zero/one value
            if count <= 1:
                if prop["values"]:
                    isNumber, parsedNumber = try_parse_string_value_as_number(prop["values"][0][0])
                    if isNumber:
                        newReq["value"] = parsedNumber
                        item[comparableCatName].append(newReq)
                    else:
                        newReq["value"] = prop["values"][0][0]
                        item[searchableCatName].append(newReq)
                # Case where there is zero value
                else:
                    newReq["value"] = "True"
                    item[searchableCatName].append(newReq)
            # Case where there is two values
            else:
                isFirstNumber, parsedFirstNumber = try_parse_string_value_as_number(prop["values"][0][0])
                isSecNumber, parsedSecNumber = try_parse_string_value_as_number(prop["values"][1][0])
                # TODO : handle the case with two numbers
                newReq["value"] = prop["values"][0][0] + " - " + prop["values"][1][0]
                item[searchableCatName].append(newReq)


def mod_values_handler(item, value, comparableCatName, searchableCatName):
    if item.get(comparableCatName) is None:
        item[comparableCatName] = list()
    if item.get(searchableCatName) is None:
        item[searchableCatName] = list()
    for prop in value:
        # Check proper format
        newMod = {}
        pattern = r"\b\d+\b"
        # Find all matches of the pattern in the input string
        numbers = re.findall(pattern, prop)
        newProp = prop
        for number in numbers:
            newProp = newProp.replace(number, "X", 1)
        newMod["name"] = newProp
        if len(numbers) == 0:
            newMod["value"] = "True"
            item[searchableCatName].append(newMod)
        elif len(numbers) == 1:
            if is_number(numbers[0]):
                newMod["value"] = float(numbers[0])
                item[comparableCatName].append(newMod)
            else:
                newMod["value"] = numbers[0]
                item[searchableCatName].append(newMod)
        else:
            separator = " - "
            newMod["value"] = separator.join(numbers)
            item[searchableCatName].append(newMod)


def try_parse_string_value_as_number(value):
    if is_number(value):
        return True, float(value)
    substrings_to_remove = [" sec", " Mana", "%"]
    cleanedValue = remove_substrings(value, substrings_to_remove)
    if is_number(cleanedValue):
        return True, float(cleanedValue)
    splitValue = cleanedValue.split("-")
    if len(splitValue) == 2 and is_number(splitValue[0]) and is_number(splitValue[1]):
        return True, (float(splitValue[0]) + float(splitValue[1])) / 2
    return False, None


def rarity_handler(item, value):
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


def map_stash_handler(league, stash, children):
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
            if item.get("comparableProperties") is None:
                item["comparableProperties"] = list()
            if item.get("searchableProperties") is None:
                item["searchableProperties"] = list()
            item["stackSize"] = int(metadata["items"])
            item["maxStackSize"] = 999
            if metadata["map"].get("tier"):
                item["tier"] = metadata["map"]["tier"]
                item["comparableProperties"].append({"name": "Map Tier", "value": int(metadata["map"]["tier"])})
            else:
                item["tier"] = 16
                item["comparableProperties"].append({"name": "Map Tier", "value": 16})
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


def unique_stash_handler(league, stash, children):
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


def empty_fields_handler(item):
    toDelete = list()
    for key in item:
        if isinstance(item[key], str) and item[key] == "":
            toDelete.append(key)
        elif isinstance(item[key], dict) and item[key] == {}:
            toDelete.append(key)
        elif isinstance(item[key], list) and item[key] == []:
            toDelete.append(key)
    for key in toDelete:
        del item[key]


def default_handler(item, key, value):
    if key not in removeList:
        item[key] = value
    return


def getFormattedStash(json, owner, league):
    api = POEApi()
    stash = json["stash"]
    items = list()
    children = stash.get("children")
    # Case where the stash has children
    if children:
        if stash.get("type") == "MapStash":
            items = map_stash_handler(league, stash, children)
        elif stash.get("type") == "UniqueStash":
            items = unique_stash_handler(league, stash, children)
        else:
            appLogger.debug("Detected children from an unknown stash type, reading substashes")
            for child in children:
                appLogger.debug(f"Querying child {stash['id']}/{child['id']}")
                childStash = api.getStashTab(league, f"{stash['id']}/{child['id']}")
                items = items + childStash["stash"]["items"]
        del stash["children"]
    # Case where the stash has items
    elif stash.get("items") is not None:
        items = stash["items"]
        del stash["items"]
    else:
        return None
    timestamp = datetime.now().strftime("%Y-%m-%dT%H%M%S")
    formattedItems = list()
    for item in items:
        try:
            formattedItem = {}
            formattedItem["timestamp"] = timestamp
            formattedItem["stash"] = {}
            formattedItem["stash"]["name"] = stash["name"]
            formattedItem["stash"]["id"] = stash["id"]
            formattedItem["stash"]["owner"] = owner
            for key in item:
                if key in fieldHandlers:
                    fieldHandlers[key](formattedItem, item[key])
                else:
                    default_handler(formattedItem, key, item[key])
            name_handler(formattedItem)
            empty_fields_handler(formattedItem)
            formattedItems.append(formattedItem)
        except Exception as e:
            appLogger.exception("An exception occurred while formatting item %s : %s", item, str(e))
    return formattedItems


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def remove_substrings(text, substrings):
    pattern = "|".join(map(re.escape, substrings))
    return re.sub(pattern, "", text)
