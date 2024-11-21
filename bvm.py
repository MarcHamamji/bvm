#!/usr/bin/python3

import argparse
from enum import Enum

from commands.install import install_version
from commands.list import list_installed_versions


class Platform(Enum):
    LINUX = "linux"
    MACOS = "macos"
    WINDOWS = "windows"

    def __str__(self):
        return self.value


def main():
    parser = argparse.ArgumentParser(
        prog="bvm", description="Version management CLI for Blender")
    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser(
        "list", help="List all available Blender versions")
    list_parser.set_defaults(func=list_installed_versions)

    install_parser = subparsers.add_parser(
        "install", help="Install a Blender version")
    install_parser.add_argument(
        "version", type=str, help="The version to install", nargs="?")
    install_parser.add_argument(
        "--platform", type=Platform, help="The platform to install Blender for", choices=list(Platform), nargs="?"
    )
    install_parser.add_argument(
        "--keep-archive", help="Keep the downloaded .tar.xz archive", action="store_true",
    )
    install_parser.set_defaults(
        func=lambda args: install_version(args, install_parser))

    # Parse and execute the appropriate function based on arguments
    args = parser.parse_args()
    if args.command:
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
