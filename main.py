#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
firefox_launcher.py -- Launch a specific Firefox Version
'''

import imp
import json
import os

from ttk import *
from Tkinter import *
import sys
from subprocess import *


# TODO: add checks for import statements
# TODO: add python version checker
# TODO: add sorting to dialog window based on Firefox version number
# maybe not? user might want their own order presereved


class Example(Frame):

    def __init__(self, parent):
        '''Initialize ALL THE THINGS'''

        Frame.__init__(self, parent)

        self.parent = parent

        # pre-generate currently_selected var with needed keys
        self.currently_selected = {'path': StringVar(), 'name': StringVar(),
                                   'version': StringVar()}

        # launch UI
        self.initUI()

    def initUI(self):
        '''Initialize User Interface'''

        self.parent.title('FireStarter')

        frame = Frame(self, relief=RAISED, borderwidth=1)
        self.pack(fill=BOTH, expand=1)

        list_of_firefoxes = get_firefoxes()

        lb = Listbox(self)
        for i in list_of_firefoxes:
            lb.insert(END, i)

        lb.bind('<<ListboxSelect>>', self.onSelect)

        lb.place(x=20, y=20)

        self.pack(fill=BOTH, expand=1)

        # print the Firefox Version number
        self.label = Label(self, text='Version:')
        self.label.place(x=20, y=210)

        self.label = Label(self, text=0,
                           textvariable=self.currently_selected['version'])
        self.label.place(x=80, y=210)

        # print the path:
        self.label = Label(self, text='Path:')
        self.label.place(x=20, y=240)

        self.label = Label(self, text=0,
                           textvariable=self.currently_selected['path'])
        self.label.place(x=60, y=240)

        # put buttons at bottom
        frame.pack(fill=BOTH, expand=1)
        self.pack(fill=BOTH, expand=1)

        closeButton = Button(self, text='Quit', command=self.quit)
        closeButton.pack(side=RIGHT, padx=5, pady=5)

        okButton = Button(self, text='Launch', command=self.selectOption)
        okButton.pack(side=RIGHT)

    def selectOption(self):
        '''Launch the selected Firefox when the user presses 'okay' '''

        dict_fx = get_firefoxes()
        fx_path = self.currently_selected['path'].get()

        # launch the specified firefox
        pid = Popen([fx_path, '-ProfileManager', '-no-remote'],
                    stdout=PIPE, stderr=PIPE).pid

        sys.exit(0)

    def onSelect(self, val):
        '''
        When any line in the dialog box is highlighted the following
        code will run
        '''

        # grab the text of the selected line
        sender = val.widget
        idx = sender.curselection()
        value = sender.get(idx)

        # lookup the user's configuration
        dict_fx = get_firefoxes()

        # based on the user's configuration get the path, version, and name
        # of the firefox they selected
        path, version = dict_fx[value]
        self.currently_selected['path'].set(path)
        self.currently_selected['version'].set(version)
        self.currently_selected['name'].set(value)


def get_firefoxes():
    ''' General function that parses the user's configuration file'''

    user = os.environ['HOME']
    config_location = '/home/yano/.config/FireStarter/firefox.conf'
    firefox_file = imp.load_source('module.name', config_location)
    fx_dict = firefox_file.firefox_dict

    # remove 'compiled' version of the config file
    try:
        os.remove('%s/.config/FireStarter/firefox.confc' % (user))
    except IOError:
        # add logging / maybe popup
        pass

    # generate new dictionary to return
    new_dict = dict()

    for fx in fx_dict:
        # for every Firefox we have (or are told about) on the system
        # lets find out what version it is.
        fx_path = fx_dict[fx]

        # place a call out to the command prompt to find the version
        # of the Firefox in question
        try:
            s1 = Popen([fx_dict[fx], '-v'], stdout=PIPE, stderr=PIPE)
            text = s1.stdout.read()
        except:
            continue

        # Format should be "Mozilla Firefox 28.0"
        if text.startswith('Mozilla Firefox'):
            version = text[15:]
            # chomp off the 'Mozilla Firefox' part
        else:
            version = False

        # re-build the dictionary in a sane way
        if fx not in new_dict:
            new_dict[fx] = list()

        # if the path for 'Firefox' isn't really Firefox
        # or isn't giving us a valid output on -v
        # lets skip it from the list
        if version:
            version = version.strip()
            new_dict[fx] = (fx_path, version)

    return new_dict


def which(f):
    '''Find system default for a given command, "f"'''

    for path in os.environ['PATH'].split(':'):
        if os.path.exists(path + '/' + f):
            return path + '/' + f
    return None


def generate_config_file():
    '''Generates a config file in ~/.config/FireStarter/firefox.conf'''

    user = os.environ['HOME']

    # check to see if the user has a ~/.config folder
    if not os.path.exists('%s/.config/' % (user)):
        try:
            # create ~/.config folder since it doesn't exist
            os.mkdir('%s/.config' % (user))
        except IOError:
            # add some logging and a pop up alert box
            print 'I could not create %s/.config/' % (user)
            pass

    # check to see if the user has a ~/.config/FireStarter/ folder
    if not os.path.exists('%s/.config/FireStarter/' % (user)):
        try:
            # create ~/.config/FireStarter/ folder since it doesn't exist
            os.mkdir('%s/.config/FireStarter/' % (user))
        except IOError:
            # add some logging and a pop up alert box
            print 'I could not create %s/.config/FireStarter/' % (user)
            pass

    # create the file
    # and check for errors while doing so
    try:
        config_file = open('%s/.config/FireStarter/firefox.conf' % (user), 'w')
    except IOError:
        # add some logging and a pop up alert box
        print 'I could not _open_ %s/.config/FireStarter/firefox.conf' % (user)
        sys.exit()
        pass

    # find system firefox
    default_firefox_path = which('firefox')
    firefox_dict = {'Firefox': default_firefox_path}

    # write a pretty dictionary to the config file
    config_file.write('firefox_dict = {\n')
    for each in firefox_dict:
        config_file.write("    '%s': '%s',\n" % (each, firefox_dict[each]))

    # also write a commented out entry so it can help exlpain to the user
    # how to add more options
    config_file.write("    # 'Firefox Name Here': ")
    config_file.write("'absolute_path_to_firefox_here',\n")
    config_file.write('}\n')
    config_file.close()


def main():
    '''main function -- brains of the operation'''

    # Check for config file
    config_file_path = '%s/.config/FireStarter/firefox.conf' % (os.environ['HOME'])
    if not os.path.exists(config_file_path):
        generate_config_file()

    width = 200
    height = 400

    # launch GUI
    root = Tk()
    ex = Example(root)
    root.geometry('%sx%s+200+200' % (width, height))
    root.mainloop()


if __name__ == '__main__':
    main()
