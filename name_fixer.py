#!/usr/bin/python3

import re
import os


'''
Utilities for sweeping for filenames

Takes an array of str patterns to search for,
returns a list of files matching that pattern.
If a pattern could not be found, the corresponding
index in the output is None.
'''


def fix_names(patterns: [str], given_names: [str] = None) -> [str | None]:
    # Initialize output array
    out: [str | None] = [None for _ in patterns]

    # Iterate
    if given_names is None or len(given_names) == 0:
        for name in os.listdir():
            for i, pattern in enumerate(patterns):
                if out[i] is not None:
                    continue
                elif re.search(pattern, name) and name[-4:] == '.csv' and name[0] != '_':
                    out[i] = name
    else:
        for name in given_names:
            for i, pattern in enumerate(patterns):
                if out[i] is not None:
                    continue
                elif re.search(pattern, name) and name[-4:] == '.csv':
                    out[i] = name

    # Return results
    return out


# Given a filepath, yields the number of HERTZ (not kilo)
def path_to_hz(path: str) -> float:
    if 'control' in path or 'Control' in path:
        return 0.0

    path_temp: str = path
    path_temp = path_temp.lower()

    if path_temp.find('/') != -1:
        path_temp = path_temp[path_temp.find('/') + 1:]
    if path_temp.find('\\') != -1:
        path_temp = path_temp[path_temp.find('\\') + 1:]

    in_khz: bool = (path.find('khz') != -1)

    numbers: str = '0123456789.'
    i: int = 0

    while path_temp[0] not in numbers:
        path_temp = path_temp[1:]

    while path_temp[i] in numbers:
        i += 1

    out: float = float(path_temp[:i])

    if in_khz:
        out *= 1000.0

    return out


# Find all filenames matching a given pattern
def find_all(pattern: str) -> [str]:
    # Initialize output array
    out: [str | None] = []

    # Iterate
    for name in os.listdir():
        if re.search(pattern, name):
            out.append(name)

    # Return results
    return out


# Find all filenames which match a given set of patterns
def find_all_from_filters(filters: [str], final_file_qualifier: str) -> [str]:
    name_array: [str] = find_all(filters[0])

    for filter in filters[1:]:
        temp: [str] = find_all(filter)

        name_array = [name for name in name_array if name in temp]

        if len(name_array) == 0:
            break

    name_array = [name for name in name_array if re.search(final_file_qualifier, name) is not None]

    return name_array

# Find all filenames matching a given pattern
# AND search subfolders
def find_all_recursive(pattern: str) -> [str]:
    # Initialize output array
    out: [str | None] = []

    # Iterate
    for root, _, filenames in os.walk(os.getcwd()):
        for filename in filenames:
            name = root + os.sep + filename
            if re.search(pattern, name):
                out.append(name)

    # Return results
    return out

# Gets the cleaned cwd as a string


def get_cwd() -> str:
    out: str = os.getcwd()

    out = out.replace('/', '_')
    out = out.replace('\\', '_')
    out = out.replace('.', '_')
    out = out.replace(' ', '_')

    return out


if __name__ == '__main__':
    patterns: [str] = ['(^0 ?khz|control)', '(0.8 ?khz|800 ?khz)',
                       '^1 ?khz', '^10 ?khz', '^25 ?khz', '^50 ?khz',
                       '^75 ?khz', '^100 ?khz', '^150 ?khz', '^200 ?khz']

    out = fix_names(patterns)

    print(out)

    pass
