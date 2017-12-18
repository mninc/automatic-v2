def check(ask):
    while True:
        text = input(ask).lower()[:1]
        if text == "y":
            return True
        elif text == "n":
            return False
        else:
            print("Please enter yes or no.")


try:
    import time
    import webbrowser
    import pytrade
    import requests
except ImportError as e:
    print("You have not installed the " + str(e)[16:] + " package.")
    print("You'll have to go back to the installation page and check you did everything.")
    if check("Want me to take you there?\nyes/no\n"):
        webbrowser.open("https://github.com/mninc/automatic-v2/blob/master/README.md", new=2, autoraise=True)
    else:
        print("Well, if you want to go there anyway you can just paste in this link: " +
              "https://github.com/mninc/automatic-v2/blob/master/README.md")
    input("Press enter to exit")
    exit(0)


version = "0.0.1"
if requests.get("https://raw.githubusercontent.com/mninc/automatic-v2/master/__version__").text[:-1] != version:
    print("You are not running the current version of the program.")
    print("You really should be. It's better. I promise.")
    if check("Want me to download it for you?\ny/n\n"):
        pass
    else:
        if check("Want me to take you to the page so you can update it yourself?\ny/n\n"):
            webbrowser.open("link", new=2, autoraise=True)
    input("You can press enter to continue running the bot with this version or close the program now.")

