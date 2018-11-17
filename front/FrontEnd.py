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
        #Boolean to make sure the error message only prints once instead of a billion times which would stress the user out
        hasPrinted = False
        while True:
            try:
                #The self.menu code will throw a screen size exception if nesecary
                self.player = player
                self.player.play(sys.argv[1])
                curses.wrapper(self.menu)
            #if the window is too small...
            except exceptions.CLI_Audio_Screen_Size_Exception:
                #using hasPrinted to make sure we only print the error message once instead of spamming the user infinitly
                if not hasPrinted:
                    print("Window is too small, please resize")
                    hasPrinted = True;
                #having small pauses before rerunning the while loop, waiting for the user to resize the window
                #This is because I do not want to run this while loop a bunch uneccecarly, wasting resources
                #when the user obviously is not going to be able to resize the window faster than the computer
                #could proccess the while loop. I used .1 seconds to make the user think it is instant though
                #when they resize the window. This way, the user is happy and the computer is happy.
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
        
        #I chose 20 by 20 as the minimum size, it is aproximatly the lowest it can go
        height, width = self.stdscr.getmaxyx()
        #Rasing exceptions if the window is too small
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
                        #Getting a list of all files in the directory "library" (Strings)
                        list = os.listdir("library")
                        #Displaying the title "Libary" to the screen 
                        self.stdscr.addstr(16, 10, "Library:")
                        #Counting variable to increment the text line
                        y = 0
                        #Going through all files in the list of .wav files we retrieved from the os
                        for filename in list:
                            #adding that filename to the screen at a lower line than the previous one
                            self.stdscr.addstr(17 + y, 12, filename)
                            #incrementing the counting variable so that the next one can be on a lower line and not replace it
                            y += 1
                        #Creating a new window to receive user input of the desired file in the displayed library
                        changeWindow = curses.newwin(5, 50, 5, 50)
                        changeWindow.border()
                        changeWindow.addstr(0,0, "Enter File: ", curses.A_REVERSE)
                        self.stdscr.refresh()
                        #Allowing for user iput by typing with "echo"
                        curses.echo()
                        #Receiving userinput for the desired file in the library from the window
                        desired_file = changeWindow.getstr(1,1,30)
                        #ending the user's ability to type
                        curses.noecho()
                        #Refreshing the main window to remove the one we put up to get user input (I think)
                        self.stdscr.touchwin()
                        self.stdscr.refresh()
                        #Playing the song if the requested on actually exists
                        if desired_file.decode(encoding="utf-8") in list:
                             self.player.stop()
                             self.player.play(desired_file.decode(encoding="utf-8")
                             self.updateSong()
                             #"Erasing" displayed list
                             self.stdscr.addstr(16, 10, "                        ")
                             y = 0
                             #Erasing the displayed library line by line               
                             for filename in list:
                                 self.stdscr.addstr(17 + y, 12, "                                       ")
                                 y += 1
                        else:
                            #This is raised if the library does NOT contain the requested filename
                            raise exceptions.CLI_Audio_File_Exception
                    except exceptions.CLI_Audio_File_Exception:
                        #If it is raise (above), then the code will restart at the beginning of the while loop and the error is displayed
                        self.stdscr.addstr(20, 20, "No file found by that name")
                    else:
                        #If no exception is raised, then we can break the while loop and move on
                        #Just in case, erasing the line where the "No file found by that name" error message is displayed.
                        #This is only needed if the user has previously requested a non-existant file, otherwise it does nothing
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
        #Boolean for whether or not the requested file exists
        exists = os.path.isfile(path.decode(encoding="utf-8"))
        if exists:
            del changeWindow
            self.stdscr.touchwin()
            self.stdscr.refresh()
            self.player.stop()
            self.player.play(path.decode(encoding="utf-8"))
        else:
            raise exceptions.CLI_Audio_File_Exception
        

    def quit(self):
        self.player.stop()
        exit()
