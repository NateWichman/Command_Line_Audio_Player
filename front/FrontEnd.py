import curses
import curses.textpad

import sys
import exceptions
import time
import os

class FrontEnd:
    def __init__(self, player):
        """Constructor. Attempts to initiate a 
        player object and create a menu through
        its menu function. Catches CLI_Audio_
        Screen_Size_Exceptions if the screen size
        is too small to draw the menu. If so, it
        will keep trying to create the menu until
        the user resizes their window to an 
        appropriate size."""
        hasPrinted = False
        while True:
            try:
                self.player = player
                #self.player.play(sys.argv[1])
                curses.wrapper(self.menu)
            except exceptions.CLI_Audio_Screen_Size_Exception:
                if not hasPrinted:
                    print("Window is too small, please resize")
                    hasPrinted = True;
                time.sleep(.1)
            else:
                break

    def menu(self, args):
        """Displays a menu, throws CLI_Audio_Screen_Size_Exception
        if the window size is too small. Allows for the user to 
        select from different options.

        "c" will change a song, throws CLI_Audio_File_Exception
            if that file does not exist
        "p" will pause the current song
        "l" will display all file in the directory called "library"
            and allow the user to select from one of them. Throws
            CLI_Audio_File_Exception if inputed file string does
            not exist.
        "ESC" will exit the menu and end the program."""
        self.stdscr = curses.initscr()

        height, width = self.stdscr.getmaxyx()
        if(height < 20):
            raise exceptions.CLI_Audio_Screen_Size_Exception
        if(width < 20):
            raise exceptions.CLI_Audio_Screen_Size_Exception

        self.stdscr.border()
        self.stdscr.addstr(0,0, "cli-audio",curses.A_REVERSE)
        self.stdscr.addstr(5,10, "c - Change current song")
        self.stdscr.addstr(6,10, "p - Play/Pause")
        self.stdscr.addstr(7,10, "l - Library")
        self.stdscr.addstr(9,10, "ESC - Quit")
        self.updateSong()
        self.stdscr.refresh()
        while True:
            c = self.stdscr.getch()
            if c == 27:
                self.quit()
            elif c == ord('p'):
                self.player.pause()
            elif c == ord('c'):
                while True:
                    try:
                        self.changeSong()
                        self.updateSong()
                        self.stdscr.touchwin()
                        self.stdscr.refresh()
                    except exceptions.CLI_Audio_File_Exception:
                        self.stdscr.addstr(20, 20, "No file found by that name")
                    else:
                        self.stdscr.addstr(20, 20, "                             ")
                        break
                        

            elif c == ord('l'):
                while True:
                    try:
                        list = os.listdir("library")
                        self.stdscr.addstr(16, 10, "Library:")
                        y = 0
                        for filename in list:
                            self.stdscr.addstr(17 + y, 12, filename)
                            y += 1
                        changeWindow = curses.newwin(5, 50, 5, 50)
                        changeWindow.border()
                        changeWindow.addstr(0,0, "Enter File: ", curses.A_REVERSE)
                        self.stdscr.refresh()
                        curses.echo()
                        desired_file = changeWindow.getstr(1,1,30)
                        curses.noecho()
                        self.stdscr.touchwin()
                        self.stdscr.refresh()
                        if list[1] == desired_file.decode(encoding="utf-8"):
                             #self.player.stop()
                             #self.player.play(desired_file.decode(encoding="utf-8")
                             self.updateSong()
                             #"Erasing" displayed list
                             self.stdscr.addstr(16, 10, "                        ")
                             y = 0
                             for filename in list:
                                 self.stdscr.addstr(17 + y, 12, "                                       ")
                                 y += 1
                        else:
                            raise exceptions.CLI_Audio_File_Exception
                    except exceptions.CLI_Audio_File_Exception:
                        self.stdscr.addstr(20, 20, "No file found by that name")
                    else:
                        self.stdscr.addstr(20, 20, "                            ")
                        break
            
    
    def updateSong(self):
        self.stdscr.addstr(15,10, "                                        ")
        self.stdscr.addstr(15,10, "Now playing: " + self.player.getCurrentSong())

    def changeSong(self):
        changeWindow = curses.newwin(5, 40, 5, 50)
        changeWindow.border()
        changeWindow.addstr(0,0, "What is the file path?", curses.A_REVERSE)
        self.stdscr.refresh()
        curses.echo()
        path = changeWindow.getstr(1,1, 30)
        curses.noecho()
        exists = os.path.isfile(path.decode(encoding="utf-8"))
        if exists:
            del changeWindow
            self.stdscr.touchwin()
            self.stdscr.refresh()
            # self.player.stop()
            # self.player.play(path.decode(encoding="utf-8"))
        else:
            raise exceptions.CLI_Audio_File_Exception
        

    def quit(self):
        self.player.stop()
        exit()
