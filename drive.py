#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: Gabriel Bustamante
Email: gabrielbusta@gmail.com

Selfdriving GoPiGo: An open source self-driving robot application.
This app was built using the GoPiGo robotics platform for the Raspberry Pi.

Copyright (C) 2017 Gabriel Bustamante
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/gpl-3.0.txt>.
"""
import gopigo
from curses import wrapper, A_BOLD


def main(stdscr):
    addinfo(stdscr)
    stdscr.refresh()
    while True:
        c = stdscr.getch()
        if c == ord(' '):
            break
        stdscr.clear()
        addinfo(stdscr)
        stdscr.addstr(13, 1, handle_input(c))
        stdscr.refresh()


def addinfo(stdscr):
    stdscr.addstr(1, 1, 'Use the keyboard to control the GoPiGo:', A_BOLD)
    stdscr.addstr(3, 1, 'w = forward')
    stdscr.addstr(4, 1, 's = backward')
    stdscr.addstr(5, 1, 'a = left')
    stdscr.addstr(6, 1, 'd = right')
    stdscr.addstr(7, 1, 'q = rotate left')
    stdscr.addstr(8, 1, 'e = rotate right')
    stdscr.addstr(9, 1, 'h = stop')
    stdscr.addstr(11, 1, 'Hit SPACE to quit...')


def handle_input(c):
    if c == ord('w'):
        gopigo.fwd()
        return 'Going forward!'
    elif c ==  ord('s'):
        gopigo.bwd()
        return 'Going Backward!'
    elif c ==  ord('a'):
        gopigo.left()
        return 'Turning left!'
    elif c ==  ord('d'):
        gopigo.right()
        return 'Turning right!'
    elif c ==  ord('q'):
        gopigo.left_rot()
        return 'Rotating left!'
    elif c ==  ord('e'):
        gopigo.right_rot()
        return 'Rotating right!'
    elif c == ord('h'):
        gopigo.stop()
        return 'Stopped.'
    else:
        return '{} is not a valid command.'.format(chr(c))


if __name__ == '__main__':
    wrapper(main)
