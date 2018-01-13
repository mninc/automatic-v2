import webbrowser


version = "1.0.0"


# Basic function to ask for a yes or no answer. Returns True for yes, False for no
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
def show(url, instructions, thing):
    ans = input("Please enter your " + thing + ". If you don't know where to find this enter 'help'.\n")
    if ans != "help":
        return ans
    else:
        print(instructions)
        input("Press enter to go to this page.\n")
        webbrowser.open(url, new=2, autoraise=True)
        return input("Please enter your " + thing + ".\n")
