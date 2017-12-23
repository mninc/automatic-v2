def nextk(key2, num):
    num += 1
    if num >= len(key2):
        num -= len(key2)
    return num


def _encrypt(key, string):
    while len(string) % 4 != 0:
        string += " "
    while len(key) % 4 != 0:
        key += " "

    quarter = len(string) // 4
    first = string[0:quarter]
    second = string[quarter:2 * quarter]
    third = string[2 * quarter:3 * quarter]
    fourth = string[3 * quarter:4 * quarter]

    quarter = len(key) // 4
    first_k = key[0:quarter]
    second_k = key[quarter:2 * quarter]
    third_k = key[2 * quarter:3 * quarter]
    fourth_k = key[3 * quarter:4 * quarter]

    encrypted = []

    number = 0
    for char in first:
        ec = ord(char) * ord(first_k[number])
        encrypted.append(str(ec))
        number = nextk(first_k, number)

    number = 0
    for char in second:
        ec = ord(char) * ord(second_k[number])
        encrypted.append(str(ec))
        number = nextk(second_k, number)

    number = 0
    for char in third:
        ec = ord(char) * ord(third_k[number])
        encrypted.append(str(ec))
        number = nextk(third_k, number)

    number = 0
    for char in fourth:
        ec = ord(char) * ord(fourth_k[number])
        encrypted.append(str(ec))
        number = nextk(fourth_k, number)

    encrypted = ",".join(encrypted)
    return encrypted


file = input("Please enter the file name. This should be settings.json unless you have changed something.\n")

with open(file, "r") as f:
    string = f.read()

with open(file, "w") as f:
    f.write(_encrypt(input("Please enter your encryption key. You will have to enter this every time you want to "
                           "use the progtam."), string))

print("Finished.")
