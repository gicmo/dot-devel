#!/usr/bin/python3

import argparse
import functools
import os
import pathlib
import tempfile
import shutil
import subprocess
import sys


ITEMS = {
    "homesick": [
        "~/.homesick/"
    ],
    "accounts": [
        "~/.config/goa-1.0/accounts.conf",
        "~/.config/evolution/sources/",
    ],
    "keyrings": [
        "~/.local/share/keyrings/",
    ],
    "fonts": [
        "~/.local/share/fonts/"
    ],
}


def run_rsync(remote, source, target=None, delete=True, dry=False):

    if not target:
        target = source

    sp = pathlib.Path(os.path.expanduser(source))
    source = os.fspath(sp)

    if not sp.exists():
        print(f"[S] {source}")
        return
    if sp.is_dir():
        print(f"[D] {source}")

        if not dry:
            subprocess.run(["ssh", remote, "mkdir", "-p", target],
                           check=False)
        source += "/"

    cmd = [
        "rsync",
        "-a",
    ]

    if delete:
        cmd += ["--delete"]

    cmd += [
        source,
        f"{remote}:{target}"
    ]

    if dry:
        print(cmd)
        return

    subprocess.run(cmd, encoding="utf-8", check=True)


def authorize_host(rsync, keyfile):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = pathlib.Path(tmpdir)
        sshdir = tmp / ".ssh"
        sshdir.mkdir()
        authorized = sshdir / "authorized_keys"
        shutil.copy(keyfile, authorized)
        sshdir.chmod(0o700)
        authorized.chmod(0o600)
        rsync(os.fspath(sshdir) + "/", "~/.ssh/", delete=False)


def flatten(lst):
    return list(x for l in lst for x in l)


def defaults(arg, default):
    if arg is None:
        return []
    arg = flatten(arg)
    if not arg:
        arg = default
    return arg


def main():
    apps = [d.name for d in os.scandir(os.path.expanduser("~/.var/app/"))]

    parser = argparse.ArgumentParser(description="sync bare bones $HOME")
    parser.add_argument("dest", metavar="DEST", help="destination computer")
    parser.add_argument("--dry-run", dest="dry", default=False,
                        action="store_true",
                        help="Show what would happen")
    parser.add_argument("--ssh-key", metavar="KEYFILE", dest="sshkey", default=None,
                        help="Enable ssh key auth")
    parser.add_argument("--no-delete", dest="delete", default=True,
                        action="store_false",
                        help="Delete remote files that don't exist locally")
    parser.add_argument("--appdata", metavar="APP", type=str, nargs="*", default=None,
                        choices=apps[:] + [[]], action="append",
                        help="Copy flatpak application data")
    parser.add_argument("--data", metavar="DATA", type=str, nargs="*", default=None,
                        choices=ITEMS.keys(), action="append",
                        help="Copy specified data")
    args = parser.parse_args(sys.argv[1:])

    dest = args.dest
    print(f"[T] {dest}")
    rsync = functools.partial(run_rsync, args.dest, delete=args.delete, dry=args.dry)

    if args.sshkey:
        authorize_host(rsync, args.sshkey)

    for data in defaults(args.data, ITEMS):
        print(data)
        for item in ITEMS[data]:
            rsync(item)

    for app in defaults(args.appdata, apps):
        rsync(f"~/.var/app/{app}")


if __name__ == "__main__":
    main()
