'''
Utilities for sweeping for filenames

Takes an array of str patterns to search for,
returns a list of files matching that pattern.
If a pattern could not be found, the corresponding
index in the output is None.
'''

import re
import os
from typing import List, Union, Optional
import sys


def fix_names(patterns: List[str],
              given_names: Optional[List[str]] = None
              ) -> List[Optional[str]]:
    '''
    Fix the given names.

    :param patterns: The name patterns to match items to.
    :param given_names: The candidates to be matched to
        patterns. If None, uses all items in the current
        directory.
    :returns: A list of names where the i-th item corresponds to
        the found name for the i-th pattern. If no item was
        found for a given item, it is left as None.
    '''

    # Initialize output array
    out: List[Union[str, None]] = [None for _ in patterns]

    # Iterate
    if given_names is None or len(given_names) == 0:
        for name in os.listdir():
            for i, pattern in enumerate(patterns):
                if out[i] is not None:
                    continue

                if re.search(pattern,
                             name) and name[-4:] == '.csv' and name[0] != '_':
                    out[i] = name

    else:
        for name in given_names:
            for i, pattern in enumerate(patterns):
                if out[i] is not None:
                    continue

                if re.search(pattern, name) and name[-4:] == '.csv':
                    out[i] = name

    # Return results
    return out


def path_to_hz(path: str) -> float:
    '''
    Given a filepath, yields the number of HERTZ (not khz).

    :param path: The filepath in question.
    :returns: The applied frequency in hertz.
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
    Find all filenames matching a given pattern in the current
    directory.

    :param pattern: A regex pattern for the desired file(s).
    :returns: All files in `./*` which match the given regex
        pattern.
    '''

    # Initialize output array
    output: List[str] = []

    # Iterate
    for name in os.listdir():
        if re.search(pattern, name):
            output.append(name)

    # Return results
    return output


def find_all_from_filters(filters: List[str],
                          final_file_qualifier: Optional[str]) -> List[str]:
    '''
    Find all filenames which match a given set of patterns.

    :param filters: The set of regex patterns a given file must
        match in order to be included in the output.
    :param final_file_qualifier: The final regex pattern which
        all files must match. If None, does not use.
    :returns: The set of all files in the current working
        directory which match all the given regular expressions.
    '''

    name_array: List[str] = find_all(filters[0])

    for filter_item in filters[1:]:
        temp: List[str] = find_all(filter_item)

        name_array = [name for name in name_array if name in temp]

        if len(name_array) == 0:
            break

    if final_file_qualifier:
        name_array = [name for name in name_array if re.search(
            final_file_qualifier, name) is not None]

    return name_array


def find_all_recursive(pattern: str) -> List[str]:
    '''
    Find all filenames matching a given pattern
    AND search subfolders
    '''

    # Initialize output array
    output: List[str] = []

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

    return 0


if __name__ == '__main__':
    sys.exit(main())
