import requests
halves = eval(requests.get("https://raw.githubusercontent.com/mninc/automatic-v2/master/halves.json").text)
effects = requests.get("https://raw.githubusercontent.com/mninc/automatic-v2/master/effects.json").json()
qualities = {"Genuine": 1,
             "Self-Made": 9,
             "Strange": 11,
             "Unique": 6,
             "Unusual": 5,
             "Vintage": 3,
             "Haunted": 13,
             "Collector's": 14}
killstreaks = {"None": 0,
               "Killstreak": 1,
               "Specialized Killstreak": 2,
               "Professional Killstreak": 3}
def search(name, user, key):
    if name[:4] == "The ":
        name = name[4:]
    if name [:14] == "Non-Craftable ":
        name = name[14:]
        craftable = -1
    else:
        craftable = 1
    if name[:4] == "The ":
        name = name[4:]

    # Assume it's unique
    quality = 6
    for _quality in qualities:
        if name.startswith(_quality):
            quality = qualities[_quality]
            name = name[len(_quality) + 1:]

    # Assume it has no killstreak
    killstreak = 0
    for _killstreak in killstreaks:
        if name.startswith(_killstreak):
            killstreak = killstreaks[_killstreak]
            name = name[len(_killstreak) + 1:]

    # Assume it's not australium
    australium = -1
    if name.startswith("Australium"):
        australium = 1
        name = name[11:]

    data = {"key": key,
            "steamid": user,
            "item_names": True,
            "page_size": 30,
            "killstreak_tier": str(killstreak),
            "australium": str(australium),
            "quality": str(quality),
            "craftable": str(craftable),
            "item": name}
    return requests.get("https://backpack.tf/api/classifieds/search/v1", data=data).json()

print(search("Strange Specialized Killstreak Australium Rocket Launcher","76561198438349516", "59f49df4cf6c754c660e1bba"))