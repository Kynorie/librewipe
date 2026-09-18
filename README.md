# LibreWipe

A small terminal tool that wipes your LibreWolf data. Linux only.

## About

LibreWipe finds your LibreWolf profile and lets you clear your data from the terminal. You pick what to delete from a simple menu.

You can wipe:

1. History
2. Cookies
3. Everything

Before anything is deleted, LibreWipe asks you to confirm. If it does not have permission to delete a file, it asks to run again with sudo.

## Features

- Finds LibreWolf automatically (normal install, Flatpak, and Snap)
- Simple menu with three options
- Confirmation step before anything is deleted
- Keeps your bookmarks when you wipe history
- Refuses to run while LibreWolf is open, so nothing gets broken
- Works with a custom LibreWolf folder
- Asks for sudo only when it is needed

## Requirements

- Linux
- Python 3.6 or newer
- LibreWolf

LibreWipe only uses the Python standard library. You do not need to install any extra packages.

## Installation

Clone the repo:

```bash
git clone https://github.com/kynorie/librewipe.git
cd librewipe
```

Make the script runnable:

```bash
chmod +x librewipe.py
```

Move it to a folder in your PATH so you can run it from anywhere:

```bash
sudo cp librewipe.py /usr/local/bin/librewipe
```

Now you can run `librewipe` from any folder.

## Usage

Start the menu:

```bash
librewipe --start
```

You will see this:

```
LibreWipe

  1) Wipe History
  2) Wipe Cookies
  3) Wipe Everything

Select an option [1/2/3]:
```

Type `1`, `2`, or `3` and press Enter. Option 3 is shown in red because it deletes everything in your profile.

LibreWipe will then ask:

```
Are You Sure? [Y/N]
```

Press `Y` to continue. If LibreWipe needs more permission, it will run again with sudo.

### Custom folder

If your LibreWolf folder is not in the normal place, use:

```bash
librewipe --customdir
```

LibreWipe will ask:

```
What is the directory of your Librewolf?:
```

Type the path and press Enter. LibreWipe checks if it exists:

```
[-] Checking if /path/to/folder exists...
[+] /path/to/folder Exists!
```

If the folder does not exist, you will see this and be asked again:

```
[-] Checking if /path/to/folder exists...
[x] /path/to/folder Does not exist. Check again!
```

You can type a LibreWolf folder (the one with `profiles.ini`) or a profile folder directly.

## What each option does

| Option | What it deletes |
| --- | --- |
| Wipe History | Browsing history. Bookmarks are kept. |
| Wipe Cookies | All saved cookies |
| Wipe Everything | Everything inside your profile folder |

## Where LibreWipe looks

LibreWipe checks these folders by default:

- `~/.librewolf`
- `~/.var/app/io.gitlab.librewolf-community/.librewolf`
- `~/snap/librewolf/common/.librewolf`

## Warning

Deleting data cannot be undone. There is no backup. Wipe Everything removes your logins, extensions, settings, and saved data, so only use it if you are sure.

Close LibreWolf before you run LibreWipe. The tool will stop if LibreWolf is still open.

## License

MIT.
