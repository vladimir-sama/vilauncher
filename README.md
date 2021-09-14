
![404](ui/icon.svg)

# VILauncher
Vlad Impaler Launcher (VILauncher) is a Python Qt5 Minecraft launcher!

## About VILauncher

### Why
I wanted my own personal Minecraft launcher and also was bored, so I started VILauncher on September 2021

### Outcome
So since it is made with Qt5 it has low RAM usage on my Artix Linux installation.
Valgrind 241 MB total heap usage

### Memory Leak (IMPORTANT)
Possible Pyside2 and Python memory leak, to test with Valgrind.

## Mojang Accounts
Supports Minecraft Mojang accounts!

### Instructions
Select Mojang account type and type your username and password, leave NULL area empty.
Once you press play, VILauncher will get your UUID and Token!
Passwords will not be saved.

## TLauncher Accounts
Also supports TLauncher accounts and TLSkinCape!

### Instructions
Select TLauncher account and type your username, also paste your UUID and access token.
Once you press play VILauncher will download the required mod and libraries.

## Install

### Notice
On first launch, VILauncher creates a version cache, which may take some time to generate if it does not exist in the `json` directory.
Please do not download binaries from unknown sources.

### Binaries
Go to `https://github.com/Ogre44/vilauncher/releases` and download latest stable release for your OS.
Place the binary in an empty directory and run.

### Linux (Source) (Unstable)
Clone the repository

`git clone https://github.com/Ogre44/vilauncher.git`

Enter the new directory

`cd vilauncher`

Install Python dependencies

`pip install -r requirements.txt`

Run VILauncher

`python vilauncher.py`

Run VILauncher with debug (SIGSEGV Errors)

`python vilauncher.py --debug`
