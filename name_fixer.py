#!/usr/bin/python3

import re
import sys
import os


'''
Takes an array of str patterns to search for,
returns a list of files matching that pattern.
If a pattern could not be found, the corresponding
index in the output is None.
'''


def fix_names(patterns: [str]) -> [str | None]:
    # Initialize output array
    out: [str | None] = [None for _ in patterns]

    # Iterate
    for name in os.listdir():
        for i, pattern in enumerate(patterns):
            if out[i] is not None:
                continue
            elif re.search(pattern, name) and name[-4:] == '.csv':
                out[i] = name

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
