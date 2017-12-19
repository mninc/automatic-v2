# Imports
import time
import webbrowser
import requests
import json
import threading
import pip
import importlib
import asyncio
from random import randint
try:
    import msvcrt
    commands = True
except ImportError:
    commands = False
    print("Platform is not Windows, toggling will not work. This will be fixed in a future release.")
    msvcrt = None


nondefault_packages = {"pytrade": "steam-trade", "Crypto.Cipher.DES": "Crypto"}

for package in nondefault_packages:
    try:
        importlib.import_module(package)
    except (ModuleNotFoundError, ImportError):
        print("Package '" + package + "' not found, will attempt to install now.")
        pip.main(["install", nondefault_packages[package]])
        input("Please restart the program to continue.\n")
        exit()

from pytrade import login, client
from Crypto.Cipher import DES

# Version number. This is compared to the github version number later
version = "0.1.0"


# Functions to be used anywhere
class GlobalFuncs:
    # Basic function to ask for a yes or no answer. Returns True for yes, False for no
    @staticmethod
    def check(ask):
        while True:
            text = input(ask).lower()[:1]
            if text == "y":
                return True
            elif text == "n":
                return False
            else:
                print("Please enter yes or no.")

    # Basic function for guiding the user through the setup process by giving them a description of what to do and a
    # website to do it at. Returns what is being looked for
    @staticmethod
    def show(url, instructions, thing):
        ans = input("Please enter your " + thing + ". If you don't know where to find this enter 'help'.\n")
        if ans != "help":
            return ans
        else:
            print(instructions)
            input("Press enter to go to this page.\n")
            webbrowser.open(url, new=2, autoraise=True)
            return input("Please enter your " + thing + ".\n")

    # Parse the item object to form an agreeable name to use. Returns the name
    @staticmethod
    def name_item(item):
        name = item.market_name
        craftable = True
        effect = ""
        if item.descriptions != list():
            for line in item.descriptions:
                if line["value"] == "( Not Usable in Crafting )":
                    craftable = False
        if name[:8] == "Unusual ":
            name = name[8:]
            for line in item.descriptions:
                if line["value"].startswith("★ Unusual Effect: "):
                    effect = line["value"][18:]
        if not craftable and effect:
            name = "Non-Craftable " + effect + " " + name
        elif not craftable:
            name = "Non-Craftable " + name
        elif effect:
            name = effect + " " + name
        return name

    # Returns a classifieds search for the item specified
    @staticmethod
    def search(name, user):
        if name[:4] == "The ":
            name = name[4:]
        if name[:14] == "Non-Craftable ":
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

        data = {"key": info.settings["apikey"],
                "steamid": user,
                "item_names": True,
                "page_size": 30,
                "killstreak_tier": str(killstreak),
                "australium": str(australium),
                "quality": str(quality),
                "craftable": str(craftable),
                "item": name,
                "fold": 0}
        while True:
            response = requests.get("https://backpack.tf/api/classifieds/search/v1", data=data).json()
            if "response" in response:
                time.sleep(randint(5,10))
            else:
                break

        return response

    @staticmethod
    def process_command(command):
        if command.startswith("change"):
            # Change an item in the settings array
            command = command[7:]
            words = command.split(" ")
            if len(words) == 1:
                if words[0] in info.settings:
                    print(str(info.settings[words[0]]))
                else:
                    print("Unexpected setting")
            else:
                info.update(words[0], words[1][1:])
        elif command.startswith("toggle"):
            # Toggle a boolean in the settings array
            command = command[7:]
            if command.startswith("acceptgifts"):
                info.update("acceptgifts", not info.settings["acceptgifts"])
            elif command.startswith("accept_any_sell_order"):
                info.update("accept_any_sell_order", not info.settings["accept_any_sell_order"])
            elif command.startswith("currency_exchange"):
                info.update("currency_exchange", not info.settings["currency_exchange"])
            elif command.startswith("use_my_key_price"):
                info.update("use_my_key_price", not info.settings["use_my_key_price"])
        elif command.startswith("add"):
            # Add a variable to a list
            command = command[4:]
            if command.startswith("owners"):
                command = command[7:]
                info.settings["owners"].append(command)
                info.update("owners", info.settings["owners"])
        elif command.startswith("remove"):
            # Remove a variable from a list
            command = command[7:]
            if command.startswith("owners"):
                command = command[7:]
                if command in info.settings["owners"]:
                    info.settings["owners"].remove(command)
                    info.update("owners", info.settings["owners"])
                else:
                    print("This variable is not in that list")
        elif command.startswith("help"):
            print("Displaying the help page...")
            print("""
Commands:
    help - Displays this message
    change - Changes the setting specified to something else (eg 'change username newuser' would change your 
                                                              username to 'newuser')
             Leaving the value to change to will display the current value
             Settings to change - username
                                  password
                                  apikey - backpack.tf api key
                                  sapikey - steam api key
                                  token - backpack.tf user token
                                  identity_secret
                                  sid - your steam id64
    toggle - Switches the setting from true to false or vice versa
             To view the current value of the setting use the 'change' command
             Settings to change - acceptgifts - accept trades where you lose no items
                                  accept_any_sell_order - sell items from your inventory even if that specific item 
                                                          doesn't have a listing. Setting this to false will stop any 
                                                          possible bugs making you lose money when selling items
                                  currency_exchange - allow users to pay with ref when you ask for keys or vice versa. 
                                                      Uses the backpack.tf price by default
                                  use_my_key_price - uses the price on your sell or buy listings for keys. 
                                                     'currency_exchange' must be set to True for this to work
    add - Adds a variable to a list. Lists can be displayed with the 'change' command
          Settings to change - owners - a list of id64s whose offers will automatically be accepted
    remove - Removes a variable from a list. This item must already be in the list for this to work
             Settings to change - owners
    """)

        else:
            print("I'm unsure what you mean.")


# Displays any text that needs displaying. For future use if needed
display = requests.get("https://raw.githubusercontent.com/mninc/automatic-v2/master/print.txt").text
print(display)


# Listens for keystrokes without disrupting the main thread. This toggles all the options
def listener():
    chars = []
    while True:
        letter = msvcrt.getwche()
        if letter == "\r":
            word = "".join(chars)
            print("\n")
            GlobalFuncs.process_command(word)
            chars = []
        else:
            chars.append(letter)


# Checks if this is the most recent version
if requests.get("https://raw.githubusercontent.com/mninc/automatic-v2/master/__version__").text[:-1] != version:
    print("You are not running the current version of the program.")
    print("You really should be. It's better. I promise.")
    if GlobalFuncs.check("Want me to download it for you?\ny/n\n"):
        # Downloads the new version
        new = requests.get("https://raw.githubusercontent.com/mninc/automatic-v2/master/automatic.py").text
        with open("automatic.py", "w") as f:
            f.write(new)
        print("Success!")
        input("You should restart the bot now.")
        exit()
    else:
        if GlobalFuncs.check("Want me to take you to the page so you can update it yourself?\ny/n\n"):
            # Leads the user to the page to download the new version
            input("I'll take you to the page when you press enter. Right-click the page, click Save As... and choose "
                  "the correct file location.")
            webbrowser.open("https://raw.githubusercontent.com/mninc/automatic-v2/master/automatic.py", new=2,
                            autoraise=True)
            input("Once you've done that you can restart the bot.")
            exit()
    input("You can press enter to continue running the bot with this version or close the program now.")

# Load some prebuilt half-scrap items and effect name to number reference
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


class Settings:
    def __init__(self):
        self.lasthb = 0
        self.settings = {}
        self.key = None
        self.bools = ["acceptgifts", "accept_any_sell_order", "currency_exchange", "use_my_key_price"]
        try:
            with open("settings.json", "r") as f:
                self.settings = json.load(f)
        except (json.decoder.JSONDecodeError, UnicodeDecodeError):
            with open("settings.json", "rb") as f:
                print("File is encrypted.")
                while True:
                    self.key = input("Please enter the 8 characters to decrypt your data.\n")
                    if len(self.key) == 8:
                        break
                    else:
                        print("Key needs to be 8 characters.")
                des = DES.new(self.key.encode(), DES.MODE_ECB)
                x = des.decrypt(f.read())
                x = x.decode().strip()
                self.settings = json.loads(x)
        except FileNotFoundError:
            print("settings file not found!")
            if GlobalFuncs.check("want to make it?\ny/n\n"):
                self.settings = dict()
                self.settings["username"] = input("Please enter the username to log into the account.\n")
                self.settings["password"] = input("Please enter the password.\n")
                self.settings["apikey"] = GlobalFuncs.show("https://backpack.tf/developer/apikey/view",
                                                           "If you already have an apikey, copy it."
                                                           " If not, you'll need to create one. "
                                                           "You can leave out the site url and "
                                                           "under comments you should write that "
                                                           "this is for a trading bot. "
                                                           "You will need elevated access to use "
                                                           "this bot - request this and wait for "
                                                           "it to be approved before continuing "
                                                           "to use this bot. If it's taking a "
                                                           "while to be processed go ping Teeny "
                                                           "in the backpack.tf discord :^)",
                                                           "backpack.tf api key")
                self.settings["sapikey"] = GlobalFuncs.show("https://steamcommunity.com/dev/apikey",
                                                            "If you already have an apikey, copy it. "
                                                            "If not, you'll need to create one. "
                                                            "The domain name doesn't matter for this."
                                                            "Once you have this, come back and paste "
                                                            "it in.",
                                                            "steam api key")
                self.settings["token"] = GlobalFuncs.show("https://backpack.tf/connections",
                                                          "Scroll down and click 'Show Token'. Copy this "
                                                          "in.",
                                                          "backpack.tf user token")
                self.settings["identity_secret"] = GlobalFuncs.show("identity_secret url",
                                                                    "This is difficult - you can follow the "
                                                                    "instructions "
                                                                    "on this page to get this, but it's likely you "
                                                                    "won't. Leave this blank if you can't get it. If "
                                                                    "you don't enter this, trades will not be confirmed"
                                                                    " automatically.",
                                                                    "identity secret")
                self.settings["sid"] = GlobalFuncs.show("https://steamid.io/",
                                                        "Enter the profile URL of the account and copy the 'steamID64'.",
                                                        "steam id")
                self.settings["acceptgifts"] = False
                self.settings["owners"] = []
                self.settings["accept_any_sell_order"] = False
                self.settings["currency_exchange"] = False
                self.settings["use_my_key_price"] = False

                while True:
                    self.key = input(
                        "Please enter 8 characters to encrypt your data. You will have to enter this key every time "
                        "you start the bot. If you do not want to encrypt this data, leave this blank.\n")
                    if len(self.key) == 8 or len(self.key) == 0:
                        break
                    else:
                        print("Key needs to be 8 characters.")
                if len(self.key) == 0:
                    with open("settings.json", "w") as f:
                        json.dump(self.settings, f)
                else:
                    with open("settings.json", "wb") as f:
                        _settings = json.dumps(self.settings)
                        while len(_settings) % 8 != 0:
                            _settings += " "
                        des = DES.new(self.key.encode(), DES.MODE_ECB)
                        x = des.encrypt(_settings.encode())
                        f.write(x)
        if not self.settings:
            input("Settings not present. Exiting program...")
            exit()

    def update(self, var, newval):
        if var in self.settings:
            if var not in self.bools:
                self.settings[var] = newval
                if not self.key:
                    with open("settings.json", "w") as f:
                        json.dump(self.settings, f)
                else:
                    with open("settings.json", "wb") as f:
                        _settings = json.dumps(self.settings)
                        while len(_settings) % 8 != 0:
                            _settings += " "
                        des = DES.new(self.key.encode(), DES.MODE_ECB)
                        x = des.encrypt(_settings.encode())
                        print(x)
                        f.write(x)
                print("Successfully updated " + var + ".")
            else:
                # Trying to change a boolean to a string
                print("This option is toggleable and cannot be manually set. Please use 'toggle' " + var + " instead.")
        else:
            # Trying to change an option not in the settings array
            print("That is not an option that can be changed.")

    def heartbeat(self):
        response = requests.post("https://backpack.tf/api/aux/heartbeat/v1", data={"token": self.settings["token"]})\
            .json()
        if "bumped" in response:
            if int(response["bumped"]) != 0:
                print("Sent a heartbeat to backpack.tf. Bumped " + str(response["bumped"]) + " listings.")
            else:
                print("Sent a heartbeat to backpack.tf.")
        else:
            print("Error sending heartbeat: " + json.dumps(response))
        self.lasthb = time.time()


info = Settings()

currencies = {"Refined Metal": 18, "Reclaimed Metal": 9, "Scrap Metal": 2}
response = requests.get("https://backpack.tf/api/IGetCurrencies/v1", data={"key": info.settings["apikey"]}).json()
keys = response["response"]["currencies"]["keys"]["price"]["value"]

if commands:
    commandListener = threading.Thread(target=listener)
    commandListener.start()

steam_client = login.AsyncClient(info.settings["username"], info.settings["password"])
manager = client.TradeManager(info.settings["sid"], key=info.settings["sapikey"],
                                      identity_secret=info.settings["identity_secret"], poll_delay=10)


@manager.on("logged_on")
async def logon():
    print("Logged in.")


@manager.on("end_poll")
async def poll_end():
    if time.time() - info.lasthb > 100:
        # If it has been 100 seconds since sending the last heartbeat
        info.heartbeat()


@manager.on("new_trade")
async def new_offer(offer):
    decline = False
    accept = False
    handled = False
    names_receiving = []
    names_losing = []
    their_id = offer.steamid_other.toString()
    response = requests.get("https://backpack.tf/api/users/info/v1", json={"key": info.settings["apikey"],
                                                                           "steamids": their_id}).json()
    print("Received offer " + offer.tradeofferid + " from " + response["users"][their_id]["name"] + ".")
    if "bans" in response["users"][their_id]:
        user = response["users"][their_id]["bans"]
    else:
        user = []
    if their_id in info.settings["owners"]:
        print("Accepting Trade: Offer from owner")
        accept = True
        handled = True
    elif "steamrep_scammer" in user or "all" in user:
        print("Declining Trade: User is a banned on steamrep or backpack.tf")
        decline = True
        handled = True
    elif not offer.items_to_give and info.settings["acceptgifts"]:
        print("Accepting Trade: not losing any items.")
        accept = True
        handled = True
    else:
        lose_val = 0
        lose_valk = 0
        gain_val = 0
        gain_valk = 0
        for item in offer.items_to_receive:
            name = item.market_name
            if name in currencies:
                names_receiving.append(name)
                gain_val += currencies[name]
            else:
                name = GlobalFuncs.name_item(item)
                names_receiving.append(name)
                response = GlobalFuncs.search(name, info.settings["sid"])
                if response["buy"]["total"] > 0:
                    listing = response["buy"]["listings"][0]["currencies"]
                    if "metal" in listing:
                        gain_val += listing["metal"]
                    if "keys" in listing:
                        gain_valk += listing["keys"]
        for item in offer.items_to_give:
            name = item.market_name
            if name in currencies:
                names_losing.append(name)
                gain_val += currencies[name]
            else:
                name = GlobalFuncs.name_item(item)
                names_losing.append(name)
                response = GlobalFuncs.search(name, info.settings["sid"])
                if response["sell"]["total"] > 0:
                    if info.settings["accept_any_sell_order"]:
                        listing = response["sell"]["listings"][0]["currencies"]
                        if "metal" in listing:
                            lose_val += listing["metal"]
                        if "keys" in listing:
                            lose_valk += listing["keys"]
                    else:
                        listings = response["sell"]["listings"]
                        for listing in listings:
                            if listing["item"]["id"] == item.assetid:
                                if "metal" in listing["currencies"]:
                                    lose_val += listing["currencies"]["metal"]
                                if "keys" in listing["currencies"]:
                                    lose_valk += listing["currencies"]["keys"]
        if lose_val <= gain_val and lose_valk <= gain_valk:
            accept = True
            handled = True
        elif info.settings["currency_exchange"] and (lose_valk > gain_valk or gain_valk > lose_valk):
            key_s = keys
            key_b = keys
            if info.settings["use_my_key_price"]:
                response = GlobalFuncs.search("Mann Co. Supply Crate Key", info.settings["sid"])
                if response["sell"]["total"] > 0:
                    key_s = response["sell"]["listings"][0]["currencies"]["metal"]
                if response["buy"]["total"] > 0:
                    key_b = response["buy"]["listings"][0]["currencies"]["metal"]
            if lose_valk > gain_valk:
                while lose_valk > 0:
                    lose_valk -= 1
                    lose_val += key_s
                    if lose_val <= gain_val and lose_valk <= gain_valk:
                        accept = True
                        handled = True
                        break
            elif gain_valk > lose_valk:
                while gain_valk > 0:
                    gain_valk -= 1
                    gain_val += key_b
                    if lose_val <= gain_val and lose_valk <= gain_valk:
                        accept = True
                        handled = True
    if handled:
        receiving = {}
        losing = {}
        for name in names_receiving:
            if name not in receiving:
                receiving[name] = 1
            else:
                receiving[name] += 1
        for name in names_losing:
            if name not in losing:
                losing[name] = 1
            else:
                losing[name] += 1
        receivel = []
        losel = []
        for name, amount in receiving.items():
            receivel.append(name + " x" + str(amount))
        for name, amount in losing.items():
            losel.append(name + " x" + str(amount))
        text = "Receiving: " + ", ".join(receivel) + "; Losing: " + ", ".join(losel)
        if accept:
            if await offer.accept():
                print("Offer Accepted: " + text)
            else:
                print("Failed to accept offer: " + text)
        elif decline and info.settings["decline_offers"]:
            await offer.decline()
            print("Offer Declined: " + text)
        else:
            print("Offer was invalid, leaving:" + text)

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.ensure_future(manager.login(steam_client)))
while True:
    try:
        manager.run_forever()
    except:
        pass




