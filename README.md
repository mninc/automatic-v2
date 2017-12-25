# automatic-v2
The unofficial version 2 of backpack.tf automatic

## How to use

You'll need to [download python3.6+](https://www.python.org/downloads/) to use this.

Then, download `automatic.py` by going [here](https://raw.githubusercontent.com/mninc/automatic-v2/master/automatic.py), right clicking and saving as a .py file in the directory you want it in.
Run the program in a command-line interface.

The program will guide you through all the steps you need. It will also update itself (after asking you) when the time comes.
One important thing to note is that elevated access to the backpack.tf apis is necessary to use this program.

You can use the `help` command to see all the commands you can use.

This program is extremely new, and there are likely bugs littered throughout it. If I were you, I wouldn't use this with higher-value items yet.

I am not responsible for any items you lose as a result of using this program.

This program is confirmed to work on Windows and Linux.

Feel free to submit an issue or a pull request.

Written entirely by me - hit me up on discord `manic#5170` or on my [steam profile](http://steamcommunity.com/id/manic_/)

Thanks to [Steam](http://store.steampowered.com) and [backpack.tf](http://www.backpack.tf) for their services and to [this library](https://github.com/Zwork101/steam-trade) by zwork for the main trading interface. 

## Note on logging
A detailed log is kept at `automatic.log`.

## OSX notes
After installing python you may need to run `/Applications/Python\ 3.6/Install\ Certificates.command` if an error occurs.

## Notes on errors
If you get an error ending with `message='Attempt to decode JSON with unexpected mimetype: text/html; charset=utf-8'`, 
this is because one of the modules this program uses needs fixing. The only person with the ability to fix this has a broken PC so this cannot be done at the module level. 

One way to fix this is to download [this](http://manicbot.me/client.py) file and place it in the directory of the module. 

If you want `accept_any_sell_order` as False to work you will need to download [this](http://manicbot.me/EconItem.py) and do the same.

On Windows the directory can be found at `C:\Users\<user>\AppData\Local\Programs\Python\Python36-32\lib\site-packages\pytrade\`.
On linux this can be found at `/usr/local/lib/python3.6/dist-packages/pytrade`.
If this is incorrect or you are on a mac, open a python shell (`python` from the command line) and type `import pytrade`. 
Then do `pytrade.__file__`. This should output the directory you need to go to (remove the `/__init__.py` bit)

## Notes on updates
From 27/12/17 to 01/01/18, I (manic) am on holiday. For this period you will have to find `Zwack010#5682` on discord for help.

## Note on encrypting and decrypting files from before 23/12/2017 (12/23/2017)
On this date the method of encrypting and decrypting files was changed. Users with encrypted files from before this date should save [this](https://raw.githubusercontent.com/mninc/automatic-v2/master/decrypt.py) program into the same directory as `automatic.py` and run it.
Users then wanting to encrypt their file with the new method should save [this](https://raw.githubusercontent.com/mninc/automatic-v2/master/encrypt.py) program into the same directory and run it.

## TODO list
* Make generic unusual buy orders work 
* Get confirmation there are no more bugs (there probably are)
* Build package for distribution that doesn't require a python installation
