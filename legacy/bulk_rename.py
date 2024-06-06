"""
A simple bulk rename tool.
"""

import os
import sys
from typing import List
import shutil
from speckle import speckle


def main(args: List[str]) -> int:
    """
    The main function. Takes in command-line arguments
    and returns an exit code.

    :param args: The command line args
    :returns: 0 on success, other on failure
    """

    if len(args) == 1:
        print("Please provide at least one argument",
              "(the folder to go through)")

        return 1

    where: str = args[1]
    pattern: str = r".*\.avi"

    if len(args) > 2:
        pattern = args[2]

    def rename_avi(path: str) -> None:
        """
        Cleans up an avi file"s name once it has been
        moved into the correct place.

        Attempts to erase evidence of name mangling from
        previous scripts.
        """

        path = os.path.realpath(path)

        try:

            # Split into directory and file
            file: str = path

            while "/" in file:
                file = file[file.index("/") + 1:]

            directory: str = path[:len(path) - len(file) - 1]

            immediate_dir: str = directory
            while "/" in immediate_dir:
                immediate_dir = immediate_dir[immediate_dir.index("/") + 1:]
            immediate_dir = immediate_dir.lower()

            new_name: str = file

            new_name = new_name.replace("_avi.avi", ".avi")
            new_name = new_name.replace(".avi.avi", ".avi")
            new_name = new_name.replace("_", "")

            if immediate_dir in file:
                new_name = file[file.index(
                    immediate_dir) + len(immediate_dir) + 1:]

            new_name = directory + "/" + new_name

            if new_name == path:
                raise ValueError('No modification made')

            # print(f"Old: {path}\nNew: {new_name}")

            shutil.move(path, new_name)

        except ValueError:
            print(f"Skipped: {path}")

            return

    speckle.for_each_file(rename_avi, where, pattern)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
