#!/usr/bin/python3

'''
Utilities for sweeping for filenames

Takes an array of str patterns to search for,
returns a list of files matching that pattern.
If a pattern could not be found, the corresponding
index in the output is None.
'''

import re
import os
from typing import List, Union
import sys


def fix_names(patterns: List[str],
              given_names: Union[List[str], None] = None
              ) -> List[Union[str, None]]:
    '''
    Fix the given names
    '''

    # Initialize output array
    out: List[Union[str, None]] = [None for _ in patterns]

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


def path_to_hz(path: str) -> float:
    '''
    Given a filepath, yields the number of HERTZ (not kilo)
    '''

    if 'control' in path or 'Control' in path:
        return 0.0

    path_temp: str = path
    path_temp = path_temp.lower()

    if path_temp.find('/') != -1:
        path_temp = path_temp[path_temp.find('/') + 1:]
    if path_temp.find('\\') != -1:
        path_temp = path_temp[path_temp.find('\\') + 1:]

    in_khz: bool = path.find('khz') != -1

    numbers: str = '0123456789.'
    i: int = 0

    while path_temp[0] not in numbers:
        path_temp = path_temp[1:]

    while path_temp[i] in numbers:
        i += 1

    output: float = float(path_temp[:i])

    if in_khz:
        output *= 1000.0

    return output


def find_all(pattern: str) -> List[str]:
    '''
    Find all filenames matching a given pattern
    '''

    # Initialize output array
    output: List[Union[str, None]] = []

    # Iterate
    for name in os.listdir():
        if re.search(pattern, name):
            output.append(name)

    # Return results
    return output


def find_all_from_filters(filters: List[str], final_file_qualifier: str) -> List[str]:
    '''
    Find all filenames which match a given set of patterns
    '''

    name_array: List[str] = find_all(filters[0])

    for filter_item in filters[1:]:
        temp: List[str] = find_all(filter_item)

        name_array = [name for name in name_array if name in temp]

        if len(name_array) == 0:
            break

    name_array = [name for name in name_array if re.search(
        final_file_qualifier, name) is not None]

    return name_array


def find_all_recursive(pattern: str) -> List[str]:
    '''
    Find all filenames matching a given pattern
    AND search subfolders
    '''

    # Initialize output array
    output: List[Union[str, None]] = []

    # Iterate
    for root, _, filenames in os.walk(os.getcwd()):
        for filename in filenames:
            name = root + os.sep + filename
            if re.search(pattern, name):
                output.append(name)

    # Return results
    return output


def get_cwd() -> str:
    '''
    Gets the cleaned cwd as a string
    '''

    out: str = os.getcwd()

    out = out.replace('/', '_')
    out = out.replace('\\', '_')
    out = out.replace('.', '_')
    out = out.replace(' ', '_')

    return out


def main() -> int:
    '''
    The main function to be called when this is being
    run as a script.
    '''

    patterns: List[str] = ['(^0 ?khz|control)', '(0.8 ?khz|800 ?khz)',
                           '^1 ?khz', '^10 ?khz', '^25 ?khz', '^50 ?khz',
                           '^75 ?khz', '^100 ?khz', '^150 ?khz', '^200 ?khz']

    output_value = fix_names(patterns)

    print(output_value)


if __name__ == '__main__':
    sys.exit(main())
