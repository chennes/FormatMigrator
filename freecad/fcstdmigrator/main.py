# SPDX-License-Identifier: LGPL-2.1-or-later

# To run the migrator from the command line run this file with python and three arguments: the input
# FCStd file, the output FCStd file, and the FreeCAD version to migrate to. Note that this is not
# the main intended use for this software and is provided mainly for testing purposes.

import argparse
import pathlib
import freecad.fcstdmigrator.migrate as migrate


def parse_args() -> argparse.Namespace:

    parser = argparse.ArgumentParser(description="Migrate FreeCAD files between different versions")
    parser.add_argument("-i", "--input", required=True, type=pathlib.Path, help="Input file")
    parser.add_argument("-o", "--output", required=True, type=pathlib.Path, help="Output file")
    parser.add_argument("-v", "--version", required=True, help="Target FreeCAD version")

    arguments = parser.parse_args()

    if not arguments.input.is_file():
        raise FileNotFoundError(f"Input file {arguments.input} does not exist")

    if arguments.output.exists():
        print(
            "WARNING: Output file already exists, it will be overwritten. Continue? (y/N)", end=" "
        )
        if input().lower() != "y":
            exit(1)

    return arguments


if __name__ == "__main__":
    args = parse_args()
    migrator = migrate.Migrate(str(args.input), args.version)
    migrator.export(str(args.output))
