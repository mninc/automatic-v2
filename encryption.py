version = "1.0.0"


def nextk(key2, num):
    num += 1
    if num >= len(key2):
        num -= len(key2)
    return num


# Encrypt a string
def encrypt(key, string):
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


# Decrypt a string
def decrypt(key, encrypted):
    while len(encrypted) % 4 != 0:
        encrypted += " "
    while len(key) % 4 != 0:
        key += " "

    string = encrypted.split(",")

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

    unencrypted = ""

    number = 0
    for char in first:
        uec = int(char) // ord(first_k[number])
        unencrypted += chr(uec)
        number = nextk(first_k, number)

    number = 0
    for char in second:
        uec = int(char) // ord(second_k[number])
        unencrypted += chr(uec)
        number = nextk(second_k, number)

    number = 0
    for char in third:
        uec = int(char) // ord(third_k[number])
        unencrypted += chr(uec)
        number = nextk(third_k, number)

    number = 0
    for char in fourth:
        uec = int(char) // ord(fourth_k[number])
        unencrypted += chr(uec)
        number = nextk(fourth_k, number)

    return unencrypted.strip()
