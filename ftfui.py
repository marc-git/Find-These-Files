'''
Created on 12/02/2013

@author: Marc Graham
'''
"""
User Interface for Find These Files
Version 0.9.9a
Improvements/Changes Made in 0.9:
    - Added copy functionality to copy non-duplicates out(!)
Bugs Squished:
    - Fixed some NoneType errors causing crashes in exe
    - Fixed Danger operation, looks pretty good now
    - Fixed bug in Copy all which would not cancel when trying to stop
    - Sorted files by name in left pane
    - Dealing with hidden files now works better (left pane only)
      fully implementing that solution would require a smart solution
      for the ftfengine too.
Improvements to come:
    - Filtering by number of matches?

"""

import os, ctypes
import ftfengine as ftfe
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog as fd
from tkinter import ttk


VERBOSE = True
#Really VERBOSE
RVERBOSE = False

class UIWindow(tk.Tk):
    """This is the container class for the Tkinter app.

        Variables used in here are
        - self.parent which is a reference to the parent window
        - self.file_names which is a text list of file_names to be checked for
        - self.filesToFind which is a list of lists [name, Hashmaker object]
        - self.dir_name is the text name for the base dir we want to look in
        - lastDir is a place holder to keep the last directory
        - isFileSelected is a boolean for whether anything has been added to
            the left window
        - isFolderSelected is a boolean for having selected a folder to search
        - treeList is a FileTree object for the searched dir
        - self.selectedFile is the HashMaker object for the file selected (left)
        - sames is the list of matches as HashMaker objects
    """

    def __init__(self,parent):
        tk.Tk.__init__(self,parent)
        self.parent = parent
        self.file_names = None
        self.dir_name = None
        self.lastdir = None
        self.isFileSelected = False
        self.isFolderSelected = False
        self.ctrl = ftfe.Controler()
        self.initialize()

    def initialize(self):

        self.topGroup= tk.LabelFrame(self.parent)
        self.topGroup.pack(pady=5, padx=5, fill='x', expand='no')

        self.leftGroup = tk.LabelFrame(self.topGroup,
                                       text="These are the files you want find...")
        self.leftGroup.pack(side='left')

        self.addFiles = tk.Button(
                self.leftGroup,text="Add file(s) individually...",
                command=lambda: self.file_pick())
        self.addFiles.pack(side='left', padx=2, pady=5)

        self.addDirLeftB = tk.Button(self.leftGroup,
                                     text="Add a whole directory",
                                     command=lambda: self.add_folder_select())
        self.addDirLeftB.pack(side='left', padx=2, pady=5)

        self.clearEntries = tk.Button(self.leftGroup,
                                      text="Clear list",
                                      command=lambda: self.clear_left())
        self.clearEntries.pack(side='right', padx=2, pady=5)

        self.checkAll = tk.Button(self.leftGroup, text="Check All",
                                  command=lambda: self.check_all())
        self.checkAll.pack(side='right', padx=2, pady=5)

        self.rightGroup = tk.LabelFrame(self.topGroup,
                                        text="This is the directory you want to search...")
        self.rightGroup.pack(side='right')

        self.selSearchDir = tk.Button(self.rightGroup,
                                      text="Select Search Directory... ",
                                      command=lambda: self.browse_dir())
        self.selSearchDir.pack(padx=2, pady=5)

        self.bottomGroup = tk.LabelFrame(self.parent,
                                         text="Filter Results")
        #self.bottomGroup.pack(side='bottom', fill='both', padx=5, pady=5)

        self.showAllB = tk.Button(self.bottomGroup,
                                  text="Show All",
                                  command=lambda: self.left_show_all())
        self.showAllB.pack(side='left')
        self.hideUnchecked = tk.Button(self.bottomGroup,
                                       text="Hide Unchecked",
                                       command=lambda: self.left_hide_unchecked())
        self.hideUnchecked.pack(side='left')
        self.hideNoMatch = tk.Button(self.bottomGroup,
                                     text="Hide Unduplicated",
                                     command=lambda: self.left_hide_nomatch())
        self.hideNoMatch.pack(side='left')
        self.hideMatch = tk.Button(self.bottomGroup,
                                   text="Hide Duplicated",
                                   command=lambda: self.left_hide_matched())
        self.hideMatch.pack(side='left')

        self.actionGroup = tk.LabelFrame(self.parent,
                                         text="Take Action")
        self.actionGroup.pack(side='bottom', fill='both', padx=5, pady=5)
        self.copyOriginals = tk.Button(self.actionGroup,
                                     text="Copy Un-duplicated",
                                     command=lambda: self.copy_origs())
        self.copyOriginals.pack(side='left')

        #self.state = tk.Label(self.parent, text="")
        #self.state.pack(side='top')
        #add a Tree Group
        self.tg = tk.LabelFrame(self.parent, text="Files", height=400, padx=5, pady=5)
        self.tg.pack(padx=5, pady=5, side='bottom', fill='both', expand='yes')

        #add the left treeviewer

        self.tree = ttk.Treeview(self.tg,selectmode="browse",columns=('Matches'))
        self.tree.pack(fill='y', side='left', padx=5)
        self.tree.heading("#0", text="File")
        self.tree.column("#0",minwidth=200,width=self.max_el_size(),stretch='YES')
        self.tree.heading('Matches', text="Matches")
        self.tree.column("Matches",minwidth=25,stretch='NO',width=40)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<<TreeviewSelect>>", self.send_selected)


        """self.tree.heading("A", text="Size")
        self.tree.column("A",minwidth=0,width=200, stretch='NO')
        self.tree.heading("B", text="Matches")
        self.tree.column("B",minwidth=0,width=300)"""

        #make a tree on the right side
        self.rTree = ttk.Treeview(self.tg,selectmode="browse")
        self.rTree.pack(expand='YES', fill='both', side='left', padx=5)
        self.rTree.heading("#0", text="Please load a search directory...")
        self.rTree.column("#0",minwidth=500,width=500, stretch='YES')
        self.rTree.bind("<Double-1>", self.on_double_click2)
        self.rTree.bind("<<TreeviewSelect>>", self.printSames)

    def full_path(self, path):
        path = os.path.expandvars(os.path.normpath(path))
        return path

    def check_all(self):
        if self.isFolderSelected:
            matches = self.ctrl.check_all()
            self.disp_matches_deep()
            messagebox.showinfo("Finished", message=str(str(matches)
                                                        + " matches found."))
        else:
            messagebox.showinfo("Not ready!",
                                message=str("Please first select a folder to"+
                                            " search and/or a file to find"))


    def delete_dupes(self, clearEmpty=True):
        self.ctrl.delete_dupes()

    def is_hidden(self, filepath):
        name = os.path.basename(os.path.abspath(filepath))
        return name.startswith('.') or self.has_hidden_attribute(filepath)

    def has_hidden_attribute(self, filepath):
        try:
            attrs = ctypes.windll.kernel32.GetFileAttributesW(filepath)
            assert attrs != -1
            result = bool(attrs & 2)
        except (AttributeError, AssertionError):
            result = False
        return result

    def copy_origs(self):
        copyTo = None
        keepStruct = None
        overwrite = None
        copyTo = fd.askdirectory(initialdir=self.lastdir)
        mbayn = messagebox.askyesno
        cancel = None
        if copyTo != '':
            copyTo = self.full_path(copyTo)
            if os.path.exists(copyTo):
                if len(os.listdir(copyTo)) > 0:
                    msg = "Do you want to continue?"
                    if mbayn("Directory Not Empty", msg):
                        msg = "Do you want to overwrite?"
                        overwrite = mbayn("Directory Not Empty", msg)
                    else:
                        cancel = True
                else:
                    overwrite = False
                if not cancel :
                    msg = "Do you want to maintain the existing directory sub-structure"
                    keepStruct = mbayn("Maintain Structure", msg)
                    if not keepStruct :
                        msg1 = "This can get messy if files have shared names"
                        msg2 = " across directories. Continue anyway?"
                        msg = msg1 + msg2
                        cancel = not mbayn("Warning", msg)
                    if not cancel:
                        self.ctrl.copy_nondupes(copyTo, keepStruct, overwrite)
                        if VERBOSE:
                            print("Copied")

    def disp_matches_deep(self, child=''):
        """Recursive method to add a number of matches value for each entry in
        the left tree"""
        numMatch = None
        for i in self.tree.get_children(child):
            kids = self.tree.get_children(i)
            if len(kids) > 0:
                self.disp_matches_deep(i)
            if os.path.isfile(self.full_path(i)):
                numMatch = len(self.ctrl.get_matches(self.full_path(i)))
                self.tree.item(i, values=(str(numMatch)))

    def clear_left(self):
        "clears all entries on the left and resets, keeps the treeList"
        #clear left
        self.file_names = None
        self.isFileSelected = False
        self.ctrl.clear_left()
        for i in self.tree.get_children():
            self.tree.delete(i)
        #clear right
        for i in self.rTree.get_children():
            self.rTree.delete(i)

    def browse_dir(self):
        if self.dir_name is None:
            self.right_dir_sel()
        else:
            if messagebox.askyesno("Woah!",
                                   "Do you want to clear all the search results"+
                                   " and load a new directory?"):
                self.dir_name = None
                self.ctrl.clear_right()
                for i in self.rTree.get_children():
                    self.rTree.delete(i)
                self.right_dir_sel()


    def printSames(self, event):
        item = self.rTree.selection()[0]
        print("item is ",item)
        print("text is ", self.rTree.item(item, "text"))
        print()

    def max_el_size(self):
        treemaxwidth = 0
        for i in self.tree.get_children():
            if i > treemaxwidth :
                treemaxwidth = i
        return treemaxwidth+400

    def on_double_click(self, event):
        item = self.tree.selection()[0]
        os.system("explorer.exe /select," + item)

    def on_double_click2(self, event):
        item = self.rTree.selection()[0]
        os.system("explorer.exe /select," + item)

    def file_pick(self):
        """
        Opens a popup dialog to select one or more files. Stores those names in
        self.file_names. Sends them to the controler.  Sets
        states for isFileSelected.
        """
        self.file_names = fd.askopenfilenames(
                                              title='Choose one or more files',
                                              initialdir=self.lastdir)
        self.file_names = self.splitlist(self.file_names)
        new_names = []
        for i in self.file_names :
            #had to do this due to wierd behaviour with mounted drives
            j = os.path.join(os.path.split(i)[0],os.path.split(i)[1])
            j = self.full_path(j)
            new_names.append(j)
        self.file_names = new_names
        if len(self.file_names) == 0:
            self.file_names = ['.']
        if self.file_names[0] != '.':
            self.lastdir = os.path.dirname(self.file_names[0])
            #make full path
            self.lastdir = self.full_path(self.lastdir)
            for f in self.file_names:
                f = self.full_path(f) #expands the path where $home might be present
                if not self.tree.exists(f):
                    self.ctrl.add_file(f)
                    self.tree.insert('', 'end', f, text=os.path.basename(f))
            self.isFileSelected = True
        elif len(self.tree.get_children("")) > 0:
            self.isFileSelected = True
        else:
            self.isFileSelected = False

    def right_dir_sel(self):
        self.dir_name = fd.askdirectory(initialdir=self.lastdir)
        if self.dir_name :
            self.rTree.heading("#0", text="Loading Directory")
            self.lastdir = self.full_path(self.dir_name)
            #make things normalised
            i = self.dir_name
            #stops weird stuff happening with mapped drives
            j = os.path.join(os.path.split(i)[0],os.path.split(i)[1])
            j = self.full_path(j)
            self.rTree.insert('', 'end', j, text=j)
            self.ctrl.set_search_dir(j)
            #clear the matches
            for i in self.tree.get_children():
                self.tree.item(i, values=(""))
            self.pop_folders(j)
            self.isFolderSelected = True
            self.rTree.heading("#0", text=str("Showing results for "+
                                               os.path.normpath(self.dir_name)))
        else:
            self.dir_name = None

    def pop_folders(self, dirName):
        """Method to add a folder to the RIGHT tree, with hierarchy
        """
        j = os.path.expandvars(dirName)
        #check if dirname is a dir
        if os.path.isdir(j):
            #get the list of directories
            dirList = os.listdir(j)
            #do dirs first
            for e in dirList:
                full = self.full_path((os.path.join(j,e)))
                if os.path.isdir(full):
                    self.rTree.insert(j, 'end', full, text=e, tags=('dir',))
                    self.pop_folders(full)
            #now do files, no need to add files to a hash list
            for e in dirList:
                full = os.path.expandvars(os.path.join(j,e))
                if os.path.isfile(full):
                    self.rTree.insert(j, 'end', full, text=e, tags=('file',))
        else:
            print("Not a directory")

    def add_folder_select(self):
        leftDirName = fd.askdirectory(initialdir=self.lastdir)
        if leftDirName :
            self.lastdir = self.full_path(leftDirName)
            #make things normalised
            i = leftDirName
            j = os.path.join(os.path.split(i)[0],os.path.split(i)[1])
            j = self.full_path(j)
            mbayn = messagebox.askyesno
            ph = mbayn("Hidden or System Files", "Ignore Hidden/System Files?")
            if not self.tree.exists(j):
                self.tree.insert('', 'end', j, text=j)
                self.add_folder(ph, j)

    def add_folder(self, ignoreHidden, basedir, dirName=None):
        """Method to add a folder to the left tree, with hierarchy. This works
        recursively by scanning through all the directories first, then adding
        the files.
        """
        ph = ignoreHidden
        #This will keep track of the basedir through the recursions
        basedir = self.full_path(basedir)
        if dirName is None:
            dirName = basedir
        j = self.full_path(dirName)
        notHidden = None
        #check if dirname is a dir
        if os.path.isdir(j):
            #get the list of directories
            dirList = os.listdir(j)
            dirList.sort(key=str.lower)
            #do dirs first
            for e in dirList:
                full = self.full_path(os.path.join(j,e))
                notHidden = not self.is_hidden(full)
                if notHidden or (not ph):
                    if os.path.isdir(full):
                        if not self.tree.exists(full):
                            self.tree.insert(j, 'end', full, text=e, tags=('dir',))
                            self.add_folder(ph, basedir, full)
                        else:
                            self.tree.delete(full)
                            self.tree.insert(j, 'end', full, text=e, tags=('dir',))
                            self.add_folder(ph, basedir, full)
                elif VERBOSE:
                    print("Ignoring hidden/system directory ", full)
            #now do files
            for e in dirList:
                full = self.full_path(os.path.join(j,e))
                notHidden = not self.is_hidden(full)
                if (not ph) or notHidden:
                    if os.path.isfile(full):
                        if not self.tree.exists(full):
                            self.tree.insert(j, 'end', full, text=e, tags=('file',))
                            self.ctrl.add_file(full, basedir)
                        else:
                            if RVERBOSE:
                                print("Adding "+full+" but it already exists")
                            self.tree.delete(full)
                            self.tree.insert(j, 'end', full, text=e, tags=('file',))
                            self.ctrl.add_file(full, basedir)
                elif RVERBOSE:
                    print("Ignoring hidden/system file ", full)
        else:
            if VERBOSE:
                print("Not a directory")

    def send_selected(self, event):
        """Only does action to right side if a file is selected"""
        item = self.tree.selection()[0]
        if os.path.isfile(item):
            self.show_sames(self.full_path(item))

    def show_sames(self, item):
        """Called by send_selected, this method makes the right side list
        become a tree of matches.  It's input is item, which is found on
        the left list.
        """
        if (self.dir_name is not None):
            self.rTree.tag_configure('highlight', foreground='black')
            for i in self.rTree.get_children():
                self.rTree.item(i, open=False, tags=())
            if VERBOSE:
                print(self.tree.selection())
            #clear last result
            for e in self.rTree.get_children():
                self.rTree.delete(e)
            #find matches (uses ftfe)
            matchList = self.ctrl.get_matches(item)
            numMatches = len(matchList)
            if len(matchList) > 0:
                self.do_match(matchList)
            else :
                self.rTree.insert('', 'end',
                                  text="No matches.")
            self.tree.item(item, values=(str(numMatches)))
        else:
            if messagebox.askyesno("No search directory loaded",
                                   "Would you like to load a new search directory?"):
                self.browse_dir()

    def do_match(self, matchList):
        """This really just clears the right list, sets up the list of matches
        and palms them off to add_match for insertion
        """
        for i in self.rTree.get_children():
            self.rTree.delete(i)
        rootNode = str(str(len(matchList))+" Matches found in... "
                       +str(os.path.normpath(self.dir_name)))
        self.rTree.insert('', 'end',
                          self.full_path(self.dir_name),
                          text=rootNode)
        for f in matchList:
            self.add_match(f, self.full_path(self.dir_name))
        self.rTree.tag_configure('idem', foreground='red')

    def add_match(self, match, root):
        #remove the trunk path from the path
        spath = self.rem_bdir(os.path.normpath(root), match.path)
        top = self.get_top(spath)
        path = os.path.join(root,top)
        while os.path.isdir(path):
            if not self.rTree.exists(path):
                self.rTree.insert(root, 'end', path, text=top)
            root = path
            spath = self.rem_bdir(os.path.normpath(root), match.path)
            top = self.get_top(spath)
            path = os.path.join(root,top)
        item = self.tree.selection()[0]
        if match.path == item:
            print("Major Error returning same path matches")
        else:
            self.rTree.insert(root, 'end', path, text=top)
        self.rTree.see(path)

    def get_top(self, spath):
        split = os.path.split(spath)
        top = None
        while split[0] != '\\':
            split = os.path.split(split[0])
            if split[0] == '\\':
                top = split[1]
        if top is None:
            top = os.path.split(spath)[1]
        return top

    def rem_bdir(self, basedir, path):
        """Returns the path without the hanging basedir"""
        path = os.path.normpath(path)
        basedir = os.path.normpath(basedir)
        smallpath=""
        while path != basedir:
            split = os.path.split(path)
            if os.path.isfile(path):
                smallpath = os.sep + split[1]
            else :
                smallpath = os.sep + split[1] + os.sep + smallpath
            path = os.path.normpath(split[0])
        return self.full_path(smallpath)


if __name__ == "__main__":
    app = UIWindow(None)
    app.title('Find these files')
    app.mainloop()


__author__          = "Marc Graham"
__copyright__       = "Copyright 2014"
__version__         = "0.9.9"
