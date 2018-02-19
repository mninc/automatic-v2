# Imports
from time import time
import threading
import os
import asyncio
import pip
import logging
import importlib
commands = None
try:
    # Try and use msvcrt if possible - Windows only
    importlib.import_module("msvcrt")
    commands = "msv"
except ImportError:
    # msvcrt is not available
    commands = "get"


# Version number. This is compared to the github version number later
version = "2.0.9"
print("unofficial backpack.tf automatic v2 version " + version)

# Update the main file
install_updates = True

# Current location
directory = os.path.dirname(os.path.abspath(__file__))

# Packages to be checked for existence or version
nondefault_packages = {"pytrade": "steam-trade", "requests": "requests", "pytf2": "pytf2"}
force_version = {"steam-trade": "2.0.8", "pytf2": "1.2.4"}
our_modules = {"encryption": "1.0.0", "basic_functions": "1.0.0", "settings": "1.0.1", "listener": "1.0.1",
               "update_checker": "1.0.2"}


updated_self = False
try:
    import update_checker
except (ModuleNotFoundError, ImportError):
    try:
        import requests
    except (ModuleNotFoundError, ImportError):
        pip.main(["install", "requests"])
        import requests
    script = requests.get("https://raw.githubusercontent.com/mninc/automatic-v2/master/functions/update_checker.py")
    with open(directory + "/update_checker.py", "wb") as f:
        f.write(script.content)
    import update_checker

for _module, alt in nondefault_packages.items():
    update_checker.pypi(_module, alt)
for _module, _version in force_version.items():
    update_checker.check_version(_module, _version)
for _module, _version in our_modules.items():
    update_checker.check_our_package(_module, "https://raw.githubusercontent.com/mninc/automatic-v2/master/functions/",
                                     _version, directory)
if not update_checker.update_self(version, __file__,
                                  "https://raw.githubusercontent.com/mninc/automatic-v2/master/__version__.txt",
                                  "https://raw.githubusercontent.com/mninc/automatic-v2/master/automatic.py",
                                  install_updates):
    updated_self = True

if updated_self:
    input("Please restart the program to continue.")
    exit()

import requests
from pytrade import login, client, steam_enums
from pytf2 import item_data
import settings
import listener


# Set up logging
logging.basicConfig(filename=directory + "/automatic.log", level=logging.DEBUG,
                    format="%(asctime)s:%(levelname)s:%(message)s")
logging.info("Program started")
logging.info("version " + version)

# Displays any text that needs displaying. For future use if needed
display = requests.get("https://raw.githubusercontent.com/mninc/automatic-v2/master/print.txt").text
print(display)

# Load some prebuilt half-scrap items and effect name to number reference
halves = eval(requests.get("https://raw.githubusercontent.com/mninc/automatic-v2/master/data/halves.json").text)
effects = item_data.effects
qualities = item_data.qualities
killstreaks = item_data.killstreaks
logging.info("Initialised variables")

# Initialise the settings
info = settings.Settings(directory)
logging.info("Initialised settings")

# Value of metal
currencies = {"Refined Metal": 18, "Reclaimed Metal": 6, "Scrap Metal": 2}

# Load key price
try:
    keys = round(18 *
                 info.tf2_manager.bp_get_currencies(parse=False)["response"]["currencies"]["keys"]["price"]["value"])
except Exception as error:  # Api request failed - most likely because the api key is wrong
    print("Error loading currencies: " + str(error))
    print("If that message says something about the api key being wrong, check that you have got them the right way "
          "round or pasted them correctly.")
    change = input("Enter 'token' or 'apikey' to change one of them.\n")
    if change == "token":
        info.update("token", input("Please enter your backpack.tf user token.\n"))
    elif change == "apikey":
        info.update("apikey", input("Please enter your backpack.tf api key.\n"))
    input("Please restart the program now.")
    exit()
logging.info("Loaded currency info")

identity_secret = info.settings["identity_secret"]
while len(identity_secret) % 4 != 0:
    identity_secret += "="

if info.settings["shared_secret"]:  # If shared secret is set
    shared_secret = info.settings["shared_secret"]
    while len(shared_secret) % 4 != 0:
        shared_secret += "="
    steam_client = login.AsyncClient(info.settings["username"], info.settings["password"], shared_secret=shared_secret)
else:  # Shared secret is not set, use a one time code
    steam_client = login.AsyncClient(info.settings["username"], info.settings["password"],
                                     one_time_code=input("Please enter your steam guard one time code.\n"))

trade_manager = client.TradeManager(info.settings["sid"], key=info.settings["sapikey"],
                                    identity_secret=identity_secret, poll_delay=10)
logging.info("Initialised manager and steam client")

if commands == "msv":
    commandListener = threading.Thread(target=listener.listener, args=(info,))
    commandListener.start()
    logging.info("Started windows listener")
elif commands == "get":
    commandListener = threading.Thread(target=listener.listener_unix, args=(info,))
    commandListener.start()
    logging.info("Started unix listener")


@trade_manager.on("logged_on")
async def logon():
    print("Logged in.")
    logging.info("Logged in")


@trade_manager.on("end_poll")
async def poll_end():
    if time() - info.lasthb > 100:  # If it has been 100 seconds since sending the last heartbeat
        try:
            bumped = info.tf2_manager.bp_send_heartbeat()
            logging.info("sent heartbeat")
            if bumped:
                print("Sent a heartbeat to backpack.tf. Bumped " + str(bumped) + " listings.")
            else:
                print("Sent a heartbeat to backpack.tf.")
        except Exception as e:
            print("Error sending heartbeat: " + str(e))
            logging.info("Error sending heartbeat: " + str(e))
        info.lasthb = time()


@trade_manager.on("poll_error")
async def poll_error(message):
    print("A poll error occured: " + str(message))
    print("Continuing as normal.")
    logging.warning("A poll error occured: " + str(message))


@trade_manager.on("error")
async def error(message):
    print("An error occured: " + str(message))
    logging.warning("Error picked up: " + str(message))


@trade_manager.on("trade_accepted")
async def accepted_offer(trade):
    print("Trade " + trade.tradeofferid + " was accepted")
    logging.debug("Accepted trade " + trade.tradeofferid)


@trade_manager.on("trade_declined")
async def declined_offer(trade):
    print("Trade " + trade.tradeofferid + " was declined")
    logging.debug("Declined trade " + trade.tradeofferid)


@trade_manager.on("trade_canceled")
async def cancelled_offer(trade):
    print("Trade " + trade.tradeofferid + " was cancelled")
    logging.debug("Cancelled trade " + trade.tradeofferid)


@trade_manager.on("trade_expired")
async def expired_trade(trade):
    print("Trade " + trade.tradeofferid + " expired")
    logging.debug("Expired trade " + trade.tradeofferid)


@trade_manager.on("trade_countered")
async def countered_trade(trade):
    print("Trade " + trade.tradeofferid + " was countered")
    logging.debug("Countered trade " + trade.tradeofferid)


@trade_manager.on("trade_state_changed")
async def changed_trade(trade):
    print("Trade " + trade.tradeofferid + " changed to an unexpected state")
    logging.debug("Unexpected state of trade " + trade.tradeofferid)


@trade_manager.on("new_conf")
async def new_conf(conf):
    if info.settings["confirm_all"] and conf.creator not in info.accepting_offers:
        response = await conf.confirm()
        if not response[0]:
            print("Error confirming trade: " + str(response[1]))
            logging.warning("Error confirming trade: " + str(response[1]))
        else:
            print("Confirmed trade " + str(conf.creator) + ".")
            logging.info("Confirmed trade " + str(conf.creator) + ".")


@trade_manager.on("new_trade")
async def new_offer(offer):
    # We haven't made a decision yet
    decline = False
    accept = False
    handled = False  # We know what to do with the trade

    # The names of the items in the trade for display later
    names_receiving = []
    names_losing = []

    # Get their steamid64
    their_id = offer.steamid_other.toString()

    print("Received offer " + offer.tradeofferid + " from " + info.tf2_manager.bp_user_name(their_id) + ".")
    logging.info("Received " + offer.tradeofferid)

    if their_id in info.settings["owners"]:  # Accept if the user is whitelisted
        print("Accepting Trade: Offer from owner")
        accept = True
        handled = True
        logging.info("Accepting: User is owner")
    elif not info.tf2_manager.bp_can_trade(their_id):  # Decline if the user is banned or a a steamrep scammer
        print("Declining Trade: User is a banned on steamrep or backpack.tf")
        decline = True
        handled = True
        logging.info("Declining: User is scammer")
    elif not offer.items_to_give and info.settings["acceptgifts"]:
        # Accept if it is a gift offer and gift offers are enabled
        print("Accepting Trade: not losing any items.")
        accept = True
        handled = True
        logging.info("Accepting: gift offer")
    elif not offer.items_to_give:  # Offer is gift offer: we don't accept these
        print("Declining Trade: Offer appears to be a gift")
        handled = True
        decline = True
        logging.info("Declining: gift offer")
    else:  # Otherwise, check all of the items
        # No items checked yet
        lose_val = 0
        lose_valk = 0
        gain_val = 0
        gain_valk = 0

        # Check all the items we are receiving
        logging.info("checking receiving items...")
        for item in offer.items_to_receive:
            name = item.market_name  # Grab a name to start with that is ok
            if name in currencies:  # If the item is metal
                names_receiving.append(name)
                gain_val += currencies[name]
                logging.info(name + ": currency")
            elif name == "Mann Co. Supply Crate Key":  # If the item is a key
                gain_valk += 1
                names_receiving.append(name)
                logging.info(name + ": key")
            else:
                name = info.tf2_manager.st_item_to_str(item)  # Get a usable name
                names_receiving.append(name)
                response = info.search(name)  # Classified search for that item
                if response["buy"]["total"] > 0:  # If we have any listings
                    if not name.endswith("Kit") and not name.endswith(tuple(item_data.wear_brackets)):
                        listing = response["buy"]["listings"][0]["currencies"]  # Grab the first one
                        if "metal" in listing:
                            gain_val += round(18 * listing["metal"])
                        if "keys" in listing:
                            gain_valk += listing["keys"]
                        logging.info(name + ": value added")
                    else:
                        found = False
                        for listing in response["buy"]["listings"]:
                            if listing["item"]["name"] == name:
                                listing = listing["currencies"]
                                if "metal" in listing:
                                    gain_val += round(18 * listing["metal"])
                                if "keys" in listing:
                                    gain_valk += listing["keys"]
                                found = True
                                logging.info(name + ": kit value added")
                                break
                        if not found:
                            handled = True
                            decline = True
                            logging.info(name + ": kit has no listing")
                else:  # There is no listing for this item
                    # Check if we can find a buy listing for this unusual (not this specific effect)
                    unusual = False
                    elevated = False
                    for _effect in effects:
                        if name.startswith(_effect):
                            unusual = True
                            name = name[len(_effect) + 1:]  # Take off effect for search
                        elif name.startswith("Strange " + _effect):
                            unusual = True
                            name = name[len(_effect) + 9:]  # Take off effect and strange for search
                            elevated = qualities["Strange"]
                    if unusual:
                        response = info.search(name, unusual=True, set_elevated=elevated)
                        if response["buy"]["total"] > 0:  # If we have any listings
                            listing = response["buy"]["listings"][0]["currencies"]  # Grab the first one
                            if "metal" in listing:
                                gain_val += round(18 * listing["metal"])
                            if "keys" in listing:
                                gain_valk += listing["keys"]

                            logging.info(name + ": added value from generic unusual listing")
                        else:
                            handled = True
                            decline = True
                            logging.info(name + ": no generic listing")
                    else:
                        if name.startswith("The "):
                            name = name[4:]
                        if name in halves and info.settings["half_scraps"]:
                            gain_val += 1
                            logging.info(name + ": half-scrap")
                        else:
                            handled = True
                            decline = True
                            logging.info(name + ": no listing")

        # Check all the items we are losing
        logging.info("checking losing items...")
        for item in offer.items_to_give:
            name = item.market_name  # Grab a name to start with that is ok
            if name in currencies:  # If the item is metal
                names_losing.append(name)
                lose_val += currencies[name]
                logging.info(name + ": currency")
            elif name == "Mann Co. Supply Crate Key":  # If the item is a key
                lose_valk += 1
                names_losing.append(name)
                logging.info(name + ": currency")
            else:
                name = info.tf2_manager.st_item_to_str(item)  # Get a usable name
                names_losing.append(name)
                response = info.search(name)  # Classified search for that item
                if response["sell"]["total"] > 0:  # If we have any listings
                    if info.settings["accept_any_sell_order"]:
                        # If we want to sell all items with that name not just specific items
                        if not name.endswith("Kit") and not name.endswith(tuple(item_data.wear_brackets)):
                            listing = response["sell"]["listings"][0]["currencies"]  # Grab the first item
                            if "metal" in listing:
                                lose_val += round(18 * listing["metal"])
                            if "keys" in listing:
                                lose_valk += listing["keys"]

                            logging.info(name + ": added value")
                        else:
                            found = False
                            for listing in response["sell"]["listings"]:
                                if listing["item"]["name"] == name:
                                    listing = listing["currencies"]
                                    if "metal" in listing:
                                        lose_val += round(18 * listing["metal"])
                                    if "keys" in listing:
                                        lose_valk += listing["keys"]
                                    found = True
                                    logging.info(name + ": kit value added")
                                    break
                            if not found:
                                handled = True
                                decline = True
                                logging.info(name + ": kit has no listing")
                    else:  # We only want to sell the items with listings
                        listings = response["sell"]["listings"]
                        # We have not found a listing for this item yet
                        found = False
                        for listing in listings:
                            if int(listing["item"]["id"]) == int(item.assetid):  # This listing is a match
                                found = True
                                if "metal" in listing["currencies"]:
                                    lose_val += round(18 * listing["currencies"]["metal"])
                                if "keys" in listing["currencies"]:
                                    lose_valk += listing["currencies"]["keys"]

                                logging.info(name + ": added value")
                                break
                        if not found:  # We are not selling this item
                            if name.startswith("The "):
                                name = name[4:]
                            if name in halves:
                                lose_val += 1
                            else:
                                handled = True
                                decline = True
                            logging.info(name + ": no listing (specific)")
                else:  # We don't have any listings for this
                    if name.startswith("The "):
                        name = name[4:]
                    if name in halves and info.settings["half_scraps"]:
                        lose_val += 1
                        logging.info(name + ": half-scrap")
                    else:
                        handled = True
                        decline = True
                        logging.info(name + ": no listing")

        if handled:  # We've already decided what to do
            pass
        elif lose_val <= gain_val and lose_valk <= gain_valk:  # The value is good
            accept = True
            handled = True
            logging.info("value is good")
        elif info.settings["currency_exchange"] and (lose_valk > gain_valk or gain_valk > lose_valk):
            # The value is not good, we'll try to move around some keys into ref and see if it matches (this option
            #                                                                                           is enabled)
            logging.info("moving keys")

            # We'll assume the offer is bad at this point
            handled = True
            decline = True

            # Grab the suggested key price
            key_s = keys
            key_b = keys
            if info.settings["use_my_key_price"]:  # If we want to use our listing
                response = info.search("Mann Co. Supply Crate Key")  # Search for our keys
                if response["sell"]["total"] > 0:
                    key_s = round(18 * response["sell"]["listings"][0]["currencies"]["metal"])
                if response["buy"]["total"] > 0:
                    key_b = round(18 * response["buy"]["listings"][0]["currencies"]["metal"])
                logging.info("got custom key price")

            if lose_valk > gain_valk:  # See if changing our keys into ref works
                while lose_valk > 0:
                    lose_valk -= 1
                    lose_val += key_s
                    if lose_val <= gain_val and lose_valk <= gain_valk:  # It matches up
                        accept = True
                        handled = True
                        logging.info("moving keys worked, 1")
                        break
            elif gain_valk > lose_valk:  # See if changing their keys into ref works
                while gain_valk > 0:
                    gain_valk -= 1
                    gain_val += key_b
                    if lose_val <= gain_val and lose_valk <= gain_valk:  # It matches up
                        accept = True
                        handled = True
                        logging.info("moving keys worked, 2")
                        break
        else:  # Offer is incorrect
            handled = True
            decline = True
            logging.info("got to the end")
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
            info.accepting_offers.append(offer.tradeofferid)
            _offer = await offer.accept()
            if _offer[0]:  # If the offer was accepted correctly
                print("Offer Accepted: " + text)
                logging.info("Offer Accepted: " + text)
            else:  # The offer failed to be accepted for whatever reason
                print("Failed to accept offer: " + text)
                logging.warning("Failed to accept offer: " + text + "\n" + _offer[1])
                await offer.update()  # Reload trade
                if offer.trade_offer_state == steam_enums.ETradeOfferState.Active:  # Offer is still active
                    print("Trying to accept offer again...")
                    logging.info("Trying again...")
                    _offer = await offer.accept()
                    if _offer[0]:  # Accepting was successful
                        print("Offer Accepted: " + text)
                        logging.info("Offer Accepted: " + text)
                    else:  # Failed to accept again
                        print("Failed to accept offer again. Giving up.")
                        print("Feel free to go and process the offer yourself.")
                        logging.warning("giving up\n" + _offer[1])
        elif decline and info.settings["decline_offers"]:  # If we're declining the offer
            await offer.decline()
            print("Offer Declined: " + text)
            logging.info("Offer Declined: " + text)
        else:  # If the offer should have been declined
            print("Offer should be declined, leaving: " + text)
            print("Feel free to accept or decline this offer yourself.")
            logging.info("Offer was invalid, leaving:" + text)
    else:  # This should never happen
        print("For some reason the offer was not handled.")
        print("Please create an issue on github: https://github.com/mninc/automatic-v2/issues")
        logging.warning("offer missed")

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.ensure_future(trade_manager.login(steam_client)))
while True:
    try:
        logging.info("running manager")
        trade_manager.run_forever()
    except Exception as manager_error:
        logging.error("manager failed")
        print("Received an error: " + str(manager_error))
        print("Continuing...")
