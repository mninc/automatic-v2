version = "1.0.1"


# Listens for keystrokes without disrupting the main thread. This toggles all the options
def listener(info):
    import msvcrt
    chars = []
    while True:
        while not msvcrt.kbhit():
            pass
        letter = msvcrt.getche().decode("utf-8")
        if letter == "\x03":
            raise KeyboardInterrupt
        if letter == "\x08":
            if len(chars) != 0:
                del chars[len(chars)-1]
        elif letter == "\r":
            word = "".join(chars)
            print("\n")
            info.process_command(word)
            chars = []
        else:
            chars.append(letter)


# Listener for non-windows systems
def listener_unix(info):
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
    chars = []
    while True:
        letter = getch()
        back = False
        if letter == "\x03":
            raise KeyboardInterrupt
        if letter == "\x7f":
            back = True
            if len(chars) != 0:
                del chars[len(chars)-1]
        if letter == "\r":
            word = "".join(chars)
            print("\n")
            info.process_command(word)
            chars = []
        else:
            if not back:
                chars.append(letter)
            print("".join(chars))
