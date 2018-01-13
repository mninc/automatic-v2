import json
import logging
import encryption
import basic_functions
import time
from random import randint
from pytf2 import manager

version = "1.0.1"


class Settings:
    def __init__(self, directory):
        self.settings_path = directory + "/settings.json"
        # Trade offers we're accepting - used to know which confirmations we're not confirming manually when the option
        # is set
        self.accepting_offers = []
        # The UNIX timestamp the last heartbeat was sent - setting this to 0 means a heartbeat is sent straight away
        self.lasthb = 0
        # Settings array
        self.settings = {}
        # Key for decrypting the settings file
        self.key = None
        # Default value of variables (for when the bot updates adding new options)
        self.defaults = {"username": "",
                         "password": "",
                         "apikey": "",
                         "sapikey": "",
                         "token": "",
                         "identity_secret": "",
                         "shared_secret": None,
                         "sid": "",
                         "acceptgifts": False,
                         "owners": [],
                         "accept_any_sell_order": False,
                         "currency_exchange": False,
                         "use_my_key_price": False,
                         "decline_offers": False,
                         "half_scraps": False,
                         "confirm_all": False}
        self.bools = []
        for option, value in self.defaults.items():
            if type(value) is bool:
                self.bools.append(option)
        try:
            # Open an unencrypted file
            with open(self.settings_path, "r") as f:
                self.settings = json.load(f)
                logging.info("Loaded unencrypted file")
        except (json.decoder.JSONDecodeError, UnicodeDecodeError):  # File is encrypted
            with open(self.settings_path, "r") as f:
                string = f.read()
                try:
                    self.key = input("Please enter your encryption key.\n")
                    self.settings = json.loads(encryption.decrypt(self.key, string))
                    logging.info("Loaded encrypted file")
                except json.decoder.JSONDecodeError:
                    print("Could not decrypt settings file.")
                    logging.warning("Could not open settings file")
                    input("Please press enter to quit.")
                    exit()

        except FileNotFoundError:  # File does not exist
            print("Settings file not found!")
            print("""Please note - on 09/01/2018 the location of the settings file was moved to where it should have
been all along. If the settings file was found before then, please find the 'settings.json' file and copy it into
the directory this script is in. It may be in a weird place (system directories etc). If you are just running this bot,
continue as normal.""")
            logging.info("Creating settings file")
            if basic_functions.check("want to make it?\ny/n\n"):
                self.settings["username"] = input("Please enter the username to log into the account.\n")
                self.settings["password"] = input("Please enter the password.\n")
                self.settings["apikey"] = basic_functions.show("https://backpack.tf/developer/apikey/view",
                                                               "If you already have an apikey, copy it."
                                                               " If not, you'll need to create one. "
                                                               "You can leave out the site url and "
                                                               "under comments you should write that "
                                                               "this is for a trading bot. "
                                                               "You will need elevated access to use "
                                                               "this bot - request this and wait for "
                                                               "it to be approved before continuing. ",
                                                               "backpack.tf api key")
                self.settings["sapikey"] = basic_functions.show("https://steamcommunity.com/dev/apikey",
                                                                "If you already have an apikey, copy it. "
                                                                "If not, you'll need to create one. "
                                                                "The domain name doesn't matter for this."
                                                                "Once you have this, come back and paste "
                                                                "it in.",
                                                                "steam api key")
                self.settings["token"] = basic_functions.show("https://backpack.tf/connections",
                                                              "Scroll down and click 'Show Token'. Copy this in.",
                                                              "backpack.tf user token")
                self.settings["identity_secret"] = basic_functions.show("identity_secret url",
                                                                        "This is difficult - you can follow the "
                                                                        "instructions "
                                                                        "on this page to get this, but it's likely you "
                                                                        "won't. Leave this blank if you can't get it. "
                                                                        "If you don't enter this, trades will not be "
                                                                        "confirmed automatically.",
                                                                        "identity secret")
                self.settings["sid"] = basic_functions.show("https://steamid.io/",
                                                            "Enter the profile URL of the account and copy the "
                                                            "'steamID64'.",
                                                            "steam id64")
                # Settings that are not set at the initialisation of the settings file
                self.settings["shared_secret"] = None
                self.settings["acceptgifts"] = False
                self.settings["owners"] = []
                self.settings["accept_any_sell_order"] = False
                self.settings["currency_exchange"] = False
                self.settings["use_my_key_price"] = False
                self.settings["decline_offers"] = False
                self.settings["half_scraps"] = False

                # Get an encryption key
                self.key = input("Please enter an encryption key to encrypt your data. You will have to enter this "
                                 "every time you start the bot. If you do not want to encrypt this data, "
                                 "leave this blank.\n")

                logging.info("Created settings file")
                if not self.key:  # File fill not be encrypted
                    logging.info("Saved settings file unencrypted")
                    with open(self.settings_path, "w") as f:
                        json.dump(self.settings, f)
                else:  # File will be encrypted
                    logging.info("Saved settings file encrypted")
                    with open(self.settings_path, "w") as f:
                        _settings = json.dumps(self.settings)
                        f.write(encryption.encrypt(self.key, _settings))
        if not self.settings:
            input("Settings not present. Exiting program...")
            exit()

        for option in self.defaults:
            if option not in self.settings:
                self.update(option, self.defaults[option], toggle=True, admin=True)

        self.tf2_manager = manager.Manager(bp_api_key=self.settings["apikey"])

    def update(self, var, newval, toggle=False, admin=False):
        if var in self.settings or admin:  # Check setting exists to be changed
            if var not in self.bools or toggle:
                # Checks we're not changing a boolean to something other than True or False
                self.settings[var] = newval
                if not self.key:  # File is not encrypted
                    with open(self.settings_path, "w") as f:
                        json.dump(self.settings, f)
                else:  # File is encrypted
                    with open(self.settings_path, "w") as f:
                        _settings = json.dumps(self.settings)
                        f.write(encryption.encrypt(self.key, _settings))
                if not admin:  # Don't display the update if this was a command initiated by the program
                    print("Successfully updated " + var + ".")
                logging.info("Updated " + var)
            else:
                # Trying to change a boolean to a string
                print("This option is toggleable and cannot be manually set. Please use 'toggle' " + var + " instead.")
        else:
            print("That is not an option that can be changed.")

    def search(self, name, unusual=False, set_elevated=False):
        while True:
            try:
                return self.tf2_manager.bp_classifieds_search(
                            self.tf2_manager.bp_classified_make_data(name, user=self.settings["sid"],
                                                                     unusual=unusual,
                                                                     set_elevated=set_elevated,
                                                                     fold=0,
                                                                     page_size=30), parse=False)
            except Exception as e:
                logging.warning("search: " + str(e))
                time.sleep(randint(0, 5))

    def process_command(self, command):
        if command.startswith("change"):
            # Change an item in the settings array
            command = command[7:]
            words = command.split(" ")
            if len(words) == 1:
                if words[0] in self.settings:
                    print(str(self.settings[words[0]]))
                else:
                    print("Unexpected setting")
            else:
                self.update(words[0], words[1])
        elif command.startswith("toggle"):
            # Toggle a boolean in the settings array
            command = command[7:]
            for option in self.bools:
                if command.startswith(option):
                    self.update(option, not self.settings[option], toggle=True)
        elif command.startswith("add"):
            # Add a variable to a list
            command = command[4:]
            if command.startswith("owners"):
                command = command[7:]
                self.settings["owners"].append(command)
                self.update("owners", self.settings["owners"])
        elif command.startswith("remove"):
            # Remove a variable from a list
            command = command[7:]
            if command.startswith("owners"):
                command = command[7:]
                if command in self.settings["owners"]:
                    self.settings["owners"].remove(command)
                    self.update("owners", self.settings["owners"])
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
                                  shared_secret 
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
                                  half_scraps - count craftable weapons as half a scrap - a list of these weapons is
                                                available at 
                                                https://github.com/mninc/automatic-v2/blob/master/halves.json
                                                for viewing and curation
                                  confirm_all - confirm trades even if they were not accepted by this bot (after trade 
                                                is accepted manually)
    add - Adds a variable to a list. Lists can be displayed with the 'change' command
          Settings to change - owners - a list of id64s whose offers will automatically be accepted
    remove - Removes a variable from a list. This item must already be in the list for this to work
             Settings to change - owners
    """)

        else:
            print("I'm unsure what you mean.")
