#!/usr/bin/python3

import argparse
import functools
import os
import pathlib
import tempfile
import shutil
import subprocess
import sys


ITEMS = [
    "~/.homesick/",
    "~/.config/goa-1.0/accounts.conf",
    "~/.config/evolution/sources/",
    "~/.local/share/keyrings/",
    "~/.local/share/fonts/",
]


def run_rsync(remote, source, target=None, delete=True):

    if not target:
        target = source

    sp = pathlib.Path(os.path.expanduser(source))
    source = os.fspath(sp)

    if not sp.exists():
        print(f"[S] {source}")
        return
    if sp.is_dir():
        print(f"[D] {source}")

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


def main():
    parser = argparse.ArgumentParser(description="sync bare bones $HOME")
    parser.add_argument("dest", metavar="DEST", help="destination computer")
    parser.add_argument("--ssh-key", metavar="KEYFILE", dest="sshkey", default=None,
                        help="Enable ssh key auth")
    parser.add_argument("--no-delete", dest="delete", default=True,
                        action="store_false",
                        help="Delete remote files that don't exist locally")
    parser.add_argument("--appdata", metavar="APP", type=str, nargs="*", default=[],
                        help="Copy flatpak application data")
    args = parser.parse_args(sys.argv[1:])

    dest = args.dest
    print(f"[T] {dest}")
    rsync = functools.partial(run_rsync, args.dest, delete=args.delete)

    if args.sshkey:
        authorize_host(rsync, args.sshkey)

    for item in ITEMS:
        rsync(item)

    for app in args.appdata:
        rsync(f"~/.var/app/{app}")


if __name__ == "__main__":
    main()
