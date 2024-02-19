"""
A simple bulk rename tool.
"""

import sys
from typing import List
import shutil
from speckle import speckle


def main(args: List[str]) -> int:
    """
    The main function. Takes in command-line arguments
    are returns an exit code.

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
        """

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

            new_name: str = file[file.index(
                immediate_dir) + len(immediate_dir) + 1:]

            new_name = new_name.replace("_avi.avi", ".avi")
            new_name = new_name.replace("_", "")

            new_name = directory + "/" + new_name

            print(f"New: {new_name}")

            shutil.move(path, new_name)

        except ValueError:
            print(f"Skipped: {path}")

            return

    speckle.for_each_file(rename_avi, where, pattern)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
