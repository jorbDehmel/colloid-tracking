#!/bin/python3

import os

import tkinter as tk
from tkinter import filedialog

import main

'''
Provides an elementary GUI to interface with
main.py and. This should be compatible with
Windows and POSIX systems.

Jordan Dehmel, 2023
'''

dir: str = ''


def walk_and_sweep(dir: str) -> None:
    print('Began', dir)

    main.sweep_folder(dir)

    for dirpath, dirs, _ in os.walk(dir):
        for dir in dirs:
            print('Walking directory', dirpath + os.sep + dir)
            main.sweep_folder(dirpath + os.sep + dir)

    print('Finished', dir)


def choose() -> None:
    global dir
    dir = filedialog.askdirectory()

    print('set dir to', dir)


def start() -> None:
    global dir

    if dir != '':
        walk_and_sweep(dir)


if __name__ == '__main__':
    root = tk.Tk()

    tk.Label(
        root,
        text='Choose a directory to operate upon below, then press start.\n'
    ).pack()

    tk.Label(
        root,
        text='Files must take the form "Xkhz' +
        main.suffix + '", which X being a number.\n'
    ).pack()

    tk.Button(
        root,
        text='Choose directory',
        command=choose
    ).pack()

    tk.Button(
        root,
        text='Start',
        command=start
    ).pack()

    tk.Button(
        root,
        text='Quit',
        command=root.destroy
    ).pack()

    root.mainloop()

    exit(0)
