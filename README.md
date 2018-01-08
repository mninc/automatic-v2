# automatic-v2
The unofficial version 2 of backpack.tf automatic

## How to use

You'll need to [download python3.6+](https://www.python.org/downloads/) to use this.

Then, download `automatic.py` by going [here](https://raw.githubusercontent.com/mninc/automatic-v2/master/automatic.py), right clicking and saving as a .py file in the directory you want it in.
Run the program in a command-line interface.

The program will guide you through all the steps you need. It will also update itself (after asking you) when the time comes.
One important thing to note is that elevated access to the backpack.tf apis is necessary to use this program.

You can use the `help` command to see all the commands you can use.

This program is confirmed to work on all operating systems - if you have an issue it most likely isn't because of this.

Feel free to submit an issue or a pull request.

Written entirely by me - hit me up on discord `manic#5170` or on my [steam profile](http://steamcommunity.com/id/manic_/)

Thanks to [Steam](http://store.steampowered.com) and [backpack.tf](http://www.backpack.tf) for their services and to [this library](https://github.com/Zwork101/steam-trade) by zwork for the main trading interface. 

## Note on logging
A detailed log is kept at `automatic.log`.

## OSX notes
After installing python you may need to run `/Applications/Python\ 3.6/Install\ Certificates.command` if an error occurs.


## Note on encrypting and decrypting files from before 23/12/2017 (12/23/2017)
On this date the method of encrypting and decrypting files was changed. Users with encrypted files from before this date should save [this](https://raw.githubusercontent.com/mninc/automatic-v2/master/tools/decrypt.py) program into the same directory as `automatic.py` and run it.
Users then wanting to encrypt their file with the new method should save [this](https://raw.githubusercontent.com/mninc/automatic-v2/master/tools/encrypt.py) program into the same directory and run it.

## TODO list
* Get confirmation there are no more bugs (there probably are)
* Build package for distribution that doesn't require a python installation - this is going to be done when there are definitely no more issues with this at all. The auto-updater will most likely have to be removed at this point, making it impossible to push smaller updates for bugs.

### TODO list history
* Make generic unusual buy orders work - Completed
