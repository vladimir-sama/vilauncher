
![404](ui/icon.svg)

# VILauncher
Vlad Impaler Launcher (VILauncher) is a Python Qt5 Minecraft launcher!

## About VILauncher

### Why
I wanted my own personal Minecraft launcher and also was bored, so I started VILauncher on September 2021 .

### Outcome
So since it is made with Qt5 it has low RAM usage on my Artix Linux installation.
Valgrind 241 MB total heap usage.

### Memory Leak (IMPORTANT)
Possible Pyside2 and Python memory leak, to test with Valgrind. (Python 3.9.6)

## Modpacks
I implemented a modpack system for VILauncher.

### Usage
Just drop your valid modpack JSON into the [modpacks](json/modpacks) JSON directory and launch VILauncher.
Or use the default Impaler JSON that brings performance boosts!

### Creation
To create a modpack use the [dump_modpack](utils/dump_modpack.py) utility.
Add the valid Modrinth mod ids or Github repositories ids for your modpack and Minecraft versions that yor modpack supports.
Also give it a single word name. Example `Raspberry` or `Optimizer` (No spaces) (No symbols) (Capitalized)

## Mojang Accounts
Supports Minecraft Mojang accounts!

### Instructions
Select Mojang account type and type your username and password, leave NULL area empty.
Once you press play, VILauncher will get your UUID and Token.
Passwords will not be saved.

## TLauncher Accounts
Also supports TLauncher accounts and TLSkinCape!

### Instructions
Select TLauncher account and type your username, also paste your UUID and access token.
Once you press play VILauncher will download the required mod and libraries.

## Install
Here are the Installation instructions

### Notice
On first launch, VILauncher creates a version cache, which may take some time to generate if it does not exist in the [json](json) directory.
Please do not download binaries from unknown sources.

### Binaries
Go to [releases](https://github.com/Ogre44/vilauncher/releases) and download latest stable release for your OS.
Place the binary in an empty directory and run.

### Linux (Source) (Unstable)
Clone the repository.

`git clone https://github.com/Ogre44/vilauncher.git`

Enter the new directory.

`cd vilauncher`

Install Python dependencies.

`pip install -r requirements.txt`

Run VILauncher.

`python vilauncher.py`

Run VILauncher with debug (SIGSEGV Error Traceback)

`python vilauncher.py --debug`

### Build (Source) (Unstable)
Build an executable.

#### Linux Instructions
Clone the repository.

`git clone https://github.com/Ogre44/vilauncher.git`

Enter the new directory.

`cd vilauncher`

Install Python dependencies.

`pip install -r requirements.txt`

Install PyInstaller.

`pip install pyinstaller`

Run PyInstaller with correct options and create executable.

`pyinstaller -Fw vilauncher.py`

Now find your new executable and run.

## Decisions
Here are the reasons some things are missing.

### Installed Versions
No installed versions filter (for now) since there are incompatibility issues with certain modified versions.

### No Forge
Yes there is no Forge filter (yet) because of incompatibility and bugs with older versions of my launcher library.

## Suggestions
Have ideas? Open an issue [here](https://github.com/Ogre44/vilauncher/issues)
