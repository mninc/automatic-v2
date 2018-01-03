try:
    from Crypto.Cipher import DES
except ImportError:
    from crypto.Cipher import DES

file = input("Please enter the file name. (Note - this should be 'settings.json' - only put in something different if "
             "you have renamed a file)\n")
with open(file, "rb") as f:
    des = DES.new(input("Please enter your encryption key.\n").encode(), DES.MODE_ECB)
    x = des.decrypt(f.read())
with open(file, "w") as f:
    f.write(x)
