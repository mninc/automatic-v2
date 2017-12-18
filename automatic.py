version = "0.0.1"


class GlobalFuncs:
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

    @staticmethod
    def show(url, instructions, thing):
        ans = input("Please enter your " + thing + ". If you don't know where to find this enter 'help'.")
        if ans != "help":
            return ans
        else:
            print(instructions)
            input("Press enter to go to this page.")
            webbrowser.open(url, new=2, autoraise=True)
            return input("Please enter your " + thing + ".")


try:
    import time
    import webbrowser
    import pytrade
    import requests
    import json
    import base64
    from Crypto.Cipher import DES
    import threading
    import platform
    if platform.release() == "Windows":
        import msvcrt
    else:
        print("Platform is not Windows, toggling will not work. This will be fixed in a future release.")
except ImportError as e:
    print("You have not installed the " + str(e)[16:] + " package.")
    print("You'll have to go back to the installation page and check you did everything.")
    if GlobalFuncs.check("Want me to take you there?\nyes/no\n"):
        webbrowser.open("https://github.com/mninc/automatic-v2/blob/master/README.md", new=2, autoraise=True)
    else:
        print("Well, if you want to go there anyway you can just paste in this link: "
              "https://github.com/mninc/automatic-v2/blob/master/README.md")
    input("Press enter to exit")
    exit(0)


def listener():
    chars = []
    while True:
        letter = msvcrt.getwche()
        if letter == "\r":
            word = "".join(chars)
            print("\n")
            if word.startswith("toggle"):
                word = word[7:]
                if word.startswith("acceptgifts"):
                    info.update("acceptgifts", not info.settings["acceptgifts"])
            else:
                print("I'm unsure what you mean.")
            chars = []
        else:
            chars.append(letter)


if requests.get("https://raw.githubusercontent.com/mninc/automatic-v2/master/__version__").text[:-1] != version:
    print("You are not running the current version of the program.")
    print("You really should be. It's better. I promise.")
    if GlobalFuncs.check("Want me to download it for you?\ny/n\n"):
        new = requests.get("https://raw.githubusercontent.com/mninc/automatic-v2/master/automatic.py").text
        with open("automatic.py", "w") as f:
            f.write(new)
        print("Success!")
        input("You should restart the bot now.")
        exit()
    else:
        if GlobalFuncs.check("Want me to take you to the page so you can update it yourself?\ny/n\n"):
            input("I'll take you to the page when you press enter. Right-click the page, click Save As... and choose "
                  "the correct file location.")
            webbrowser.open("https://raw.githubusercontent.com/mninc/automatic-v2/master/automatic.py", new=2,
                            autoraise=True)
            input("Once you've done that you can restart the bot.")
            exit()
    input("You can press enter to continue running the bot with this version or close the program now.")



class Settings:
    def __init__(self):
        self.settings = {}
        self.key = None
        try:
            with open("settings.json", "r") as f:
                self.settings = json.load(f)
        except (json.decoder.JSONDecodeError, UnicodeDecodeError):
            with open("settings.json", "rb") as f:
                print("File is encrypted.")
                self.key = input("Please enter your key.")
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
                                                                    "you don't enter this, trades will not be confirmed "
                                                                    "automatically.",
                                                                    "identity secret")
                self.settings["sid"] = GlobalFuncs.show("https://steamid.io/",
                                                        "Enter the profile URL of the account and copy the 'steamID64'.",
                                                        "steam id")

                while True:
                    self.key = input(
                        "Please enter 8 characters to encrypt your data. You will have to enter this key every time "
                        "you start the bot. If you do not want to encrypt this data, leave this blank.")
                    if len(self.key) == 8 or len(self.key) == 0:
                        break
                    else:
                        print("Key needs to be 8 characters.")
                if len(self.key) == 0:
                    with open("settings.json", "w") as f:
                        json.dump(self.settings, f)
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


info = Settings()

currencies = {"Refined Metal": 18, "Reclaimed Metal": 9, "Scrap Metal": 2}


steam_client = pytrade.login.AsyncClient(info.settings["username"], info.settings["password"])
manager = pytrade.client.TradeManager(info.settings["sid"], key=info.settings["sapikey"],
                                      identity_secret=info.settings["identity_secret"], poll_delay=10)


@manager.on("logged_on")
async def logon():
    print("Logged in.")


@manager.on("new_trade")
async def new_offer(offer):
    print("Received offer " + offer.tradeofferid)
