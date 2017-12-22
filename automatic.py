# Imports
import time
import webbrowser
import json
import threading
import pip
import importlib
import asyncio
from random import randint
commands = None
try:
    # Try and use msvcrt if possible - Windows only
    import msvcrt
    commands = "msv"
except ImportError:
    # msvcrt is not available
    msvcrt = None
    commands = "get"

    # an alternative for msvcrt - Unix only
    import sys
    import tty
    import termios

    def getch():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

# Packages not included in python by default
nondefault_packages = {"pytrade": "steam-trade", "Crypto.Cipher.DES": "pycrypto", "aiohttp": "aiohttp", "rsa": "rsa",
                       "steamid": "steamid", "bs4": "bs4"}

installed_package = False
for package in nondefault_packages:
    try:
        importlib.import_module(package)
    except (ModuleNotFoundError, ImportError):
        print("Package '" + package + "' not found, will attempt to install now.")
        pip.main(["install", nondefault_packages[package]])
        installed_package = True
        print("Package installed.")

if installed_package:
    input("Please restart the program now.")
    exit()

import requests
from pytrade import login, client
try:
    from Crypto.Cipher import DES
except ImportError:
    from crypto.Cipher import DES

# Version number. This is compared to the github version number later
version = "0.3.6"
print("unofficial backpack.tf automatic v2 version " + version)


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
        # Assume it's craftable
        craftable = True
        # Assume it's not unusual with no effecr
        effect = ""
        unusual = False
        if name.startswith("Unusual "):
            unusual = True
        if item.descriptions != list():
            for line in item.descriptions:
                if line["value"] == "( Not Usable in Crafting )":
                    craftable = False
                elif line["value"].startswith("★ Unusual Effect: ") and unusual:
                    name = name[8:]
                    effect = line["value"][18:]

        # Combine craftability and effect where applicable
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
        # Take off any unneccesary prefixes
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

        # Assume it's not unusual
        effect = False
        for _effect in effects:
            if name.startswith(_effect):
                effect = effects[_effect]
                name = name[len(_effect) + 1:]

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

        if effect:
            data["particle"] = effect

        while True:
            response = requests.get("https://backpack.tf/api/classifieds/search/v1", data=data).json()
            # Rate limited
            if "response" in response:
                # Try and get a request to go through - possible synchronisation in the future to speed this process
                # up?
                time.sleep(randint(0, 10))
            else:
                break

        return response

    # Process an input from a message - allows for future expansion with different input methods
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
                info.update("acceptgifts", not info.settings["acceptgifts"], toggle=True)
            elif command.startswith("accept_any_sell_order"):
                info.update("accept_any_sell_order", not info.settings["accept_any_sell_order"], toggle=True)
            elif command.startswith("currency_exchange"):
                info.update("currency_exchange", not info.settings["currency_exchange"], toggle=True)
            elif command.startswith("use_my_key_price"):
                info.update("use_my_key_price", not info.settings["use_my_key_price"], toggle=True)
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
        while not msvcrt.kbhit():
            pass
        letter = msvcrt.getche().decode("utf-8")
        if letter == "\x08":
            if len(chars) != 0:
                del chars[len(chars)-1]
        elif letter == "\r":
            word = "".join(chars)
            print("\n")
            GlobalFuncs.process_command(word)
            chars = []
        else:
            chars.append(letter)


# Listener for non-windows systems
def listener_unix():
    chars = []
    while True:
        letter = getch()
        back = False
        if letter == "\x7f":
            back = True
            if len(chars) != 0:
                del chars[len(chars)-1]
        if letter == "\r":
            word = "".join(chars)
            print("\n")
            GlobalFuncs.process_command(word)
            chars = []
        else:
            if not back:
                chars.append(letter)
            print("".join(chars))


# Checks if this is the most recent version
if requests.get("https://raw.githubusercontent.com/mninc/automatic-v2/master/__version__.txt").text.strip() != version:
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
        # The UNIX timestamp the last heartbeat was sent - setting this to 0 means a heartbeat is sent straight away
        self.lasthb = 0
        # Settings array
        self.settings = {}
        # Key for decrypting the settings file
        self.key = None
        # Variables in the settings that need to be True or False
        self.bools = ["acceptgifts", "accept_any_sell_order", "currency_exchange", "use_my_key_price"]
        try:
            # Open an unencrypted file
            with open("settings.json", "r") as f:
                self.settings = json.load(f)
        except (json.decoder.JSONDecodeError, UnicodeDecodeError):  # File is encrypted
            with open("settings.json", "rb") as f:
                print("File is encrypted.")
                # Get the key
                while True:
                    self.key = input("Please enter the 8 characters to decrypt your data.\n")
                    if len(self.key) == 8:
                        break
                    else:
                        print("Key needs to be 8 characters.")
                # Decrypt the file
                des = DES.new(self.key.encode(), DES.MODE_ECB)
                x = des.decrypt(f.read())
                try:
                    x = x.decode().strip()
                except UnicodeDecodeError:  # File still could not be read
                    print("It appears you typed in your encryption key incorrectly or your settings file is corrupted.")
                    input("Press enter to exit. You can run the program again to try again.")
                    exit()
                self.settings = json.loads(x)
        except FileNotFoundError:  # File does not exist
            print("settings file not found!")
            if GlobalFuncs.check("want to make it?\ny/n\n"):
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
                                                           "it to be approved before continuing. ",
                                                           "backpack.tf api key")
                self.settings["sapikey"] = GlobalFuncs.show("https://steamcommunity.com/dev/apikey",
                                                            "If you already have an apikey, copy it. "
                                                            "If not, you'll need to create one. "
                                                            "The domain name doesn't matter for this."
                                                            "Once you have this, come back and paste "
                                                            "it in.",
                                                            "steam api key")
                self.settings["token"] = GlobalFuncs.show("https://backpack.tf/connections",
                                                          "Scroll down and click 'Show Token'. Copy this in.",
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
                                                        "steam id64")
                # Settings that are not set at the initialisation of the settings file
                self.settings["acceptgifts"] = False
                self.settings["owners"] = []
                self.settings["accept_any_sell_order"] = False
                self.settings["currency_exchange"] = False
                self.settings["use_my_key_price"] = False
                self.settings["decline_offers"] = False

                # Try to get an encryption key
                while True:
                    self.key = input(
                        "Please enter 8 characters to encrypt your data. You will have to enter this key every time "
                        "you start the bot. If you do not want to encrypt this data, leave this blank.\n")
                    if len(self.key) == 8 or len(self.key) == 0:
                        break
                    else:
                        print("Key needs to be 8 characters.")
                if len(self.key) == 0:  # File fill not be encrypted
                    with open("settings.json", "w") as f:
                        json.dump(self.settings, f)
                else:  # File will be encrypted
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

        for option in self.bools:
            if option not in self.settings:
                self.update(option, False, toggle=True)

    def update(self, var, newval, toggle=False):
        if var in self.settings:  # Check setting exists to be changed
            if var not in self.bools or toggle:
                # Checks we're not changing a boolean to something other than True or False
                self.settings[var] = newval
                if not self.key:  # File is not encrypted
                    with open("settings.json", "w") as f:
                        json.dump(self.settings, f)
                else:  # File is encrypted
                    with open("settings.json", "wb") as f:
                        _settings = json.dumps(self.settings)
                        while len(_settings) % 8 != 0:
                            _settings += " "
                        des = DES.new(self.key.encode(), DES.MODE_ECB)
                        x = des.encrypt(_settings.encode())
                        f.write(x)
                print("Successfully updated " + var + ".")
            else:
                # Trying to change a boolean to a string
                print("This option is toggleable and cannot be manually set. Please use 'toggle' " + var + " instead.")
        else:
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


# Initialise the settings
info = Settings()

# Value of metal
currencies = {"Refined Metal": 18, "Reclaimed Metal": 9, "Scrap Metal": 2}

# Load key price
response = requests.get("https://backpack.tf/api/IGetCurrencies/v1", data={"key": info.settings["apikey"]}).json()
if "currencies" not in response:
    keys = round(18 * response["response"]["currencies"]["keys"]["price"]["value"])
else:  # Api request failed - most likely because the api key is wrong
    print("Error loading currencies: " + str(response["response"]))
    print("If that message says something about the api key being wrong, check that you have got them the right way "
          "round or pasted them correctly.")
    change = input("Enter 'token' or 'apikey' to change one of them.\n")
    if change == "token":
        info.update("token", input("Please enter your backpack.tf user token.\n"))
    elif change == "apikey":
        info.update("apikey", input("Please enter your backpack.tf api key.\n"))
    exit()

identity_secret = info.settings["identity_secret"]

while len(identity_secret) % 4 != 0:
    identity_secret += "="

steam_client = login.AsyncClient(info.settings["username"], info.settings["password"],
                                 one_time_code=input("Please enter your steam guard one time code.\n"))
manager = client.TradeManager(info.settings["sid"], key=info.settings["sapikey"],
                              identity_secret=identity_secret, poll_delay=10)

if commands == "msv":
    commandListener = threading.Thread(target=listener)
    commandListener.start()
elif commands == "get":
    commandListener = threading.Thread(target=listener_unix)
    commandListener.start()


@manager.on("logged_on")
async def logon():
    print("Logged in.")


@manager.on("end_poll")
async def poll_end():
    if time.time() - info.lasthb > 100:  # If it has been 100 seconds since sending the last heartbeat
        info.heartbeat()


@manager.on("error")
async def error(message):
    print("An error occured: " + str(message))


@manager.on("trade_accepted")
async def accepted_offer(trade):
    print("Trade " + trade.tradeofferid + " was accepted")


@manager.on("trade_declined")
async def accepted_offer(trade):
    print("Trade " + trade.tradeofferid + " was declined")


@manager.on("new_trade")
async def new_offer(offer):
    # We haven't made a decision yet
    decline = False
    accept = False
    handled = False
    # The names of the items in the trade for display later
    names_receiving = []
    names_losing = []
    # Get their steamid64
    their_id = offer.steamid_other.toString()
    # See if they have any bans
    response = requests.get("https://backpack.tf/api/users/info/v1", json={"key": info.settings["apikey"],
                                                                           "steamids": their_id}).json()
    print("Received offer " + offer.tradeofferid + " from " + response["users"][their_id]["name"] + ".")
    if "bans" in response["users"][their_id]:
        user = response["users"][their_id]["bans"]
    else:
        user = []
    if their_id in info.settings["owners"]:  # Accept if the user is whitelisted
        print("Accepting Trade: Offer from owner")
        accept = True
        handled = True
    elif "steamrep_scammer" in user or "all" in user:  # Decline if the user is banned or a a steamrep scammer
        print("Declining Trade: User is a banned on steamrep or backpack.tf")
        decline = True
        handled = True
    elif not offer.items_to_give and info.settings["acceptgifts"]:
        # Accept if it is a gift offer and gift offers are enabled
        print("Accepting Trade: not losing any items.")
        accept = True
        handled = True
    else:  # Otherwise, check all of the items
        # No items checked yet
        lose_val = 0
        lose_valk = 0
        gain_val = 0
        gain_valk = 0
        # Check all the items we are receiving
        for item in offer.items_to_receive:
            name = item.market_name  # Grab a name to start with that is ok
            if name in currencies:  # If the item is metal
                names_receiving.append(name)
                gain_val += currencies[name]
            elif name == "Mann Co. Supply Crate Key":  # If the item is a key
                gain_valk += 1
                names_receiving.append(name)
            else:
                name = GlobalFuncs.name_item(item)  # Get a usable name
                names_receiving.append(name)
                response = GlobalFuncs.search(name, info.settings["sid"])  # Classified search for that item
                if response["buy"]["total"] > 0:  # If we have any listings
                    listing = response["buy"]["listings"][0]["currencies"]  # Grab the first one
                    if "metal" in listing:
                        gain_val += round(18 * listing["metal"])
                    if "keys" in listing:
                        gain_valk += listing["keys"]
                else:  # Decline - we're not buying this item
                    decline = True
        # Check all the items we are losing
        for item in offer.items_to_give:
            name = item.market_name  # Grab a name to start with that is ok
            if name in currencies:  # If the item is metal
                names_losing.append(name)
                lose_val += currencies[name]
            elif name == "Mann Co. Supply Crate Key":  # If the item is a key
                lose_valk += 1
                names_losing.append(name)
            else:
                name = GlobalFuncs.name_item(item)  # Get a usable name
                names_losing.append(name)
                response = GlobalFuncs.search(name, info.settings["sid"])  # Classified search for that item
                if response["sell"]["total"] > 0:  # If we have any listings
                    if info.settings["accept_any_sell_order"]:
                        # If we want to sell all items with that name not just specific items
                        listing = response["sell"]["listings"][0]["currencies"]  # Grab the first item
                        if "metal" in listing:
                            lose_val += round(18 * listing["metal"])
                        if "keys" in listing:
                            lose_valk += listing["keys"]
                    else:  # We only want to sell the items with listings
                        listings = response["sell"]["listings"]
                        # We have not found a listing for this item yet
                        found = False
                        for listing in listings:
                            if listing["item"]["id"] == item.id:  # This listing is a match
                                found = True
                                if "metal" in listing["currencies"]:
                                    lose_val += round(18 * listing["currencies"]["metal"])
                                if "keys" in listing["currencies"]:
                                    lose_valk += listing["currencies"]["keys"]
                        if not found:  # We are not selling this item
                            decline = True
                            handled = True
                else:  # We don't have any listings for this
                    handled = True
                    decline = True
        if handled:  # We've already decided what to do
            pass
        elif lose_val <= gain_val and lose_valk <= gain_valk:  # The value is good
            accept = True
            handled = True
        elif info.settings["currency_exchange"] and (lose_valk > gain_valk or gain_valk > lose_valk):
            # The value is not good, we'll try to move around some keys into ref and see if it matches (this option
            #                                                                                           is enabled)

            # We'll assume the offer is bad at this point
            handled = True
            decline = True

            # Grab the suggested key price
            key_s = keys
            key_b = keys
            if info.settings["use_my_key_price"]:  # If we want to use our listing
                response = GlobalFuncs.search("Mann Co. Supply Crate Key", info.settings["sid"])  # Search for our keys
                if response["sell"]["total"] > 0:
                    key_s = round(18 * response["sell"]["listings"][0]["currencies"]["metal"])
                if response["buy"]["total"] > 0:
                    key_b = round(18 * response["buy"]["listings"][0]["currencies"]["metal"])
            if lose_valk > gain_valk:  # See if changing our keys into ref works
                while lose_valk > 0:
                    lose_valk -= 1
                    lose_val += key_s
                    if lose_val <= gain_val and lose_valk <= gain_valk:  # It matches up
                        accept = True
                        handled = True
                        break
            elif gain_valk > lose_valk:  # See if changing their keys into ref works
                while gain_valk > 0:
                    gain_valk -= 1
                    gain_val += key_b
                    if lose_val <= gain_val and lose_valk <= gain_valk:  # It matches up
                        accept = True
                        handled = True
    if handled:  # We've made a decision
        # Count how many of each item
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
        # Build a string for displaying
        receivel = []
        losel = []
        for name, amount in receiving.items():
            receivel.append(name + " x" + str(amount))
        for name, amount in losing.items():
            losel.append(name + " x" + str(amount))
        text = "Receiving: " + ", ".join(receivel) + "; Losing: " + ", ".join(losel)
        if accept:  # If we're accepting the offer
            if await offer.accept():  # If the offer was accepted correctly
                print("Offer Accepted: " + text)
            else:  # The offer failed to be accepted for whatever reason
                print("Failed to accept offer: " + text)
        elif decline and info.settings["decline_offers"]:  # If we're declining the offer
            await offer.decline()
            print("Offer Declined: " + text)
        else:  # If the offer should have been declined
            print("Offer was invalid, leaving:" + text)
    else:  # This should never happen
        print("For some reason the offer was not accepted.")
        print("Please create an issue on github: https://github.com/mninc/automatic-v2/issues")

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.ensure_future(manager.login(steam_client)))
while True:
    try:
        manager.run_forever()
    except:
        pass




