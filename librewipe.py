#!/usr/bin/env python3

import argparse
import configparser
import os
import pwd
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def real_home():
    sudo_user = os.environ.get("SUDO_USER")
    if os.geteuid() == 0 and sudo_user:
        return Path(pwd.getpwnam(sudo_user).pw_dir)
    return Path.home()


def candidate_roots():
    home = real_home()
    return [
        home / ".librewolf",
        home / ".var/app/io.gitlab.librewolf-community/.librewolf",
        home / "snap/librewolf/common/.librewolf",
    ]


def profiles_from_root(root):
    ini = root / "profiles.ini"
    if not ini.exists():
        return []
    cfg = configparser.ConfigParser()
    cfg.read(ini)
    profiles = []
    for section in cfg.sections():
        if not section.startswith("Profile"):
            continue
        path = cfg[section].get("Path")
        if not path:
            continue
        is_relative = cfg[section].get("IsRelative", "1") == "1"
        full = (root / path) if is_relative else Path(path)
        if full.is_dir():
            profiles.append(full)
    return profiles


def find_profiles(custom_dir=None):
    if custom_dir is not None:
        profiles = profiles_from_root(custom_dir)
        if profiles:
            return profiles
        if (custom_dir / "places.sqlite").exists() or (custom_dir / "cookies.sqlite").exists():
            return [custom_dir]
        return []

    profiles = []
    for root in candidate_roots():
        profiles.extend(profiles_from_root(root))
    return profiles


def librewolf_running():
    result = subprocess.run(["pgrep", "-x", "librewolf"], capture_output=True)
    return result.returncode == 0


def wipe_history(profile):
    db = profile / "places.sqlite"
    if not db.exists():
        return
    con = sqlite3.connect(db)
    try:
        con.execute("DELETE FROM moz_historyvisits")
        con.execute(
            "DELETE FROM moz_places WHERE id NOT IN "
            "(SELECT fk FROM moz_bookmarks WHERE fk IS NOT NULL)"
        )
        con.commit()
        con.execute("VACUUM")
    finally:
        con.close()


def wipe_cookies(profile):
    db = profile / "cookies.sqlite"
    if not db.exists():
        return
    con = sqlite3.connect(db)
    try:
        con.execute("DELETE FROM moz_cookies")
        con.commit()
        con.execute("VACUUM")
    finally:
        con.close()


def wipe_everything(profile):
    for item in profile.iterdir():
        if item.is_dir() and not item.is_symlink():
            shutil.rmtree(item)
        else:
            item.unlink()


ACTIONS = {
    "1": ("Wipe History", wipe_history),
    "2": ("Wipe Cookies", wipe_cookies),
    "3": ("Wipe Everything", wipe_everything),
}


def show_menu():
    print(f"\n{BOLD}LibreWipe{RESET}\n")
    print("  1) Wipe History")
    print("  2) Wipe Cookies")
    print(f"  3) {RED}Wipe Everything{RESET}\n")


def confirm():
    answer = input("Are You Sure? [Y/N] ").strip().lower()
    return answer == "y"


def elevate(choice, custom_dir=None):
    print("Some files may need elevated permissions.")
    print("Re-running with sudo...")
    cmd = ["sudo", sys.executable, os.path.abspath(sys.argv[0]), "--run", choice]
    if custom_dir is not None:
        cmd += ["--customdir-path", str(custom_dir)]
    os.execvp("sudo", cmd)


def run_wipe(choice, custom_dir=None):
    label, func = ACTIONS[choice]
    profiles = find_profiles(custom_dir)
    if not profiles:
        print("Could not find a LibreWolf profile.")
        sys.exit(1)

    if librewolf_running():
        print("LibreWolf is running. Close it first and try again.")
        sys.exit(1)

    for profile in profiles:
        print(f"{label}: {profile}")
        try:
            func(profile)
        except PermissionError:
            return False
    return True


def ask_custom_dir():
    while True:
        raw = input("What is the directory of your Librewolf?: ").strip()
        if not raw:
            print("[x] No directory entered. Check again!")
            continue

        path = Path(raw).expanduser()
        print(f"[-] Checking if {raw} exists...")
        if path.is_dir():
            print(f"[+] {raw} Exists!")
            return path

        print(f"[x] {raw} Does not exist. Check again!")


def start(custom_dir=None):
    if not find_profiles(custom_dir):
        if custom_dir is not None:
            print(f"No LibreWolf profile found in {custom_dir}.")
        else:
            print("LibreWolf not found (no profile directory detected).")
        sys.exit(1)

    show_menu()
    choice = input("Select an option [1/2/3]: ").strip()
    if choice not in ACTIONS:
        print("Invalid choice.")
        sys.exit(1)

    if not confirm():
        print("Cancelled.")
        sys.exit(0)

    if not run_wipe(choice, custom_dir):
        elevate(choice, custom_dir)
        return

    print("Done.")


def run_direct(choice, custom_dir=None):
    if choice not in ACTIONS:
        print("Invalid choice.")
        sys.exit(1)
    if not run_wipe(choice, custom_dir):
        print("Permission denied even with elevated privileges.")
        sys.exit(1)
    print("Done.")


def main():
    parser = argparse.ArgumentParser(prog="librewipe")
    parser.add_argument("--start", action="store_true", help="launch the interactive menu")
    parser.add_argument(
        "--customdir",
        action="store_true",
        help="ask for a custom LibreWolf directory, then launch the menu",
    )
    parser.add_argument("--customdir-path", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--run", choices=list(ACTIONS), help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.run:
        run_direct(args.run, args.customdir_path)
    elif args.customdir:
        start(ask_custom_dir())
    elif args.customdir_path:
        start(args.customdir_path)
    elif args.start:
        start()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
