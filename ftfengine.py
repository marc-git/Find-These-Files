'''
Created on 12/02/2013

@author: Marc Graham
'''
"""script to check if a file matches those in a directory
Marc Graham
 Version 0.9.9 -
 Improvements:
      - Added the the functions rem-bir and copy_nondupes adding file ops
Bugs sqaushed:
      - Danger detection was not working properly, had to flip around the relpath
      - Various NoneType errors causing crashes in exe file
To be improved:
    - Add hide/show functionality
"""

import hashlib, os
from shutil import copy2

BLOCKSIZE = 65536
RECURSE = True
VERBOSE = True
#Really VERBOSE
RVERBOSE = False

class Controler(object):
    """This class provides the functions and variables that interface between
    UI and engine.  This was introduced to really pull all the non-UI stuff
    from ftf, so that a change in user interface would be possible in the future

    It has variables:
    self.filesToFind -- A list of files (HashMaker obj) to be looked for (left pane)
                    Structure is [hM, matches, basedir]
    self.searchDir -- The directory to be searched (right pane)
    self.selectedFile -- The file in filesToFind that we're looking for (?)
    self.matches -- The matches corresponding to that file
    self.danger -- if the added files are inside within the search dir
    """

    def __init__(self):
        self.filesToFind = []
        self.searchDir = None
        self.selectedFile = None
        self.matches = None
        self.danger = False

    def add_file(self, path, basedir=None):
        path = self.full_path(path)
        if os.path.isfile(path):
            exists = False
            for f in self.filesToFind:
                if f[0].path == path:
                    exists += 1
            if not exists:
                h = HashMaker(path)
                self.filesToFind.append([h, None, basedir])
                #check that the file is not within the search
                if self.searchDir is not None:
                    if self.is_subdir(self.searchDir.compareDir, path):
                        self.danger = True
                        print("Danger!! Searched File is inside the search Dir!")
                        if VERBOSE:
                            print(self.searchDir.compareDir, path)
                if RVERBOSE:
                    print("Added "+path)
                return True
            else :
                if VERBOSE:
                    print("Already exists, "+path)
                return False
        else:
            if VERBOSE:
                print("Not a file, moron! "+path)
            return False

    def is_subdir(self, path, directory):
        """Checks if we're searching in the same directory"""
        path = self.full_path(path)
        directory = self.full_path(directory)
        #True if it is not a subdir
        notSub = None
        #if the drive letter is not the same it can't be in the same path
        #relpath will crash if they are on different drives.
        if RVERBOSE :
            print(path[0], directory[0])
        if path[0] != directory[0]:
            notSub = True
        else:
            relative = os.path.normpath(os.path.relpath(directory, path))
            notSub = relative.startswith(os.pardir + os.sep)
        #a .. will not be made if the file is in the base dir
        if (self.full_path(os.path.dirname(path))==directory):
            notSub = False
            if VERBOSE:
                print(self.full_path(os.path.dirname(path)) +
                       " is " + directory)
        if notSub:
            return False
        else:
            if VERBOSE:
                print("Danger... ")
            return True

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

    def copy_nondupes(self, copyTo, keepStruct, overwrite):
        """Makes a copy of the checked but not duplicated files to a
        given (copyTo) location with or without keeping the directory
        structure (keepStruct)"""
        print ("Copying")
        tot = float(len(self.filesToFind))
        i = 0.0
        copyTo = self.full_path(copyTo)
        for f in self.filesToFind:
            fpath = f[0].path
            nm = None
            if isinstance(f[1], list):
                nm = len(f[1])
            basedir = f[2]
            i += 1.0
            print("Now at ", round(i*100.0/tot,2), "%")
            if nm == 0 :
                (p, fn) = os.path.split(fpath)
                if basedir is not None:
                    print(basedir, " ", p)
                    p = self.rem_bdir(basedir, p)
                    p = p.strip(os.sep)
                else :
                    p = ''
                if not keepStruct :
                    p = ''
                newp = os.path.join(copyTo, p)
                newp = self.full_path(newp)
                os.makedirs(newp,exist_ok=True)
                newf = os.path.join(copyTo, fn)
                newf = self.full_path(newf)
                if os.path.exists(newf):
                    if overwrite:
                        if VERBOSE:
                            print("Copying ", fpath, " to ", newp)
                        copy2(fpath, newp)
                        if VERBOSE:
                            print("Overwriting ", newf)
                else:
                    if VERBOSE:
                        print("Copying ", fpath, " to ", newp)
                    copy2(fpath, newp)


    def get_matches(self, path):
        """Returns matches to a certain path. Stores the result against that
        file.  """
        result = None
        if self.searchDir is not None:
            path = self.full_path(path)
            for f in self.filesToFind:
                if path == f[0].path:
                    if isinstance(f[1], list):
                        if len(f[1]) > 0:
                            result = f[1]
                        else :
                            matches = self.searchDir.check(f[0])
                            f[1] = matches[:]
                            result = f[1]
                    else:
                        matches = self.searchDir.check(f[0])
                        f[1] = matches[:]
                        result = f[1]
                    return result

    def check_all(self):
        """Checks all files for matches"""
        tot = float(len(self.filesToFind))
        i = 0.0
        matchCount = 0
        for f in self.filesToFind :
            if f[1] is None:
                f[1] = self.searchDir.check(f[0])
                if len(f[1]) > 0 :
                    matchCount += 1
            i += 1.0
            print(round(i*100.0/tot, 2))
        return matchCount


    def clear_matches(self):
        """Clears the matches (like for when changing search directories"""
        for f in self.filesToFind:
            f[1] = None

    def set_search_dir(self, dir):
        """Sets the directory to be searched, taking input from the UI, clears
        any match results
        Keyword Argument:
        dir -- The path to the directory to be searched
        """
        self.danger = False
        path = self.full_path(dir)
        if self.searchDir is None:
            if RVERBOSE:
                print("Setting new search dir "+path)
            self.searchDir = FileTree(path)
            if len(self.filesToFind) != 0:
                for f in self.filesToFind:
                    if self.is_subdir(self.searchDir.compareDir, f[0].path):
                        print("Danger! Searched File is in the search Dir!")
                        if VERBOSE:
                            print((self.searchDir.compareDir, f[0].path))
                        self.danger = True
        else :
            if VERBOSE:
                print("Resetting search dir to: "+path)
            self.searchDir = None
            self.clear_matches()
            self.searchDir = FileTree(path)
            if len(self.filesToFind) != 0:
                if VERBOSE:
                    print("Checking for auto-inclusions...")
                for f in self.filesToFind:
                    if RVERBOSE:
                        print(self.searchDir.compareDir, f[0].path)
                    if self.is_subdir(self.searchDir.compareDir, f[0].path):
                        print("Danger!!! Searched File is in the search Dir!")
                        if VERBOSE:
                            print((self.searchDir.compareDir, f[0].path))
                        self.danger = True


    def clear_left(self):
        """Resets the files to be found to as new conditions"""
        self.filesToFind = []
        self.selectedFile = None
        self.matches = None

    def clear_right(self):
        self.clear_matches()
        self.searchDir = None

    def full_path(self, path):
        path = os.path.expandvars(os.path.normpath(path))
        return path


class HashMaker(object):
    """This class defines the basic storage unit for files which may or may not be hashed

    Keyword Argument:
    path -- the path to the file (directory only)
    name -- the name of the file at that location
    shortHash -- able to specify the hash of the first BLOCKSIZE characters
    fullHash -- able to specify the full hash of the file if you've got it
    matchMe -- a list of matching HashMaker objects (might remove this)

    """

    def __init__(self, path, shortHash=None, fullHash=None):
        self.path = path
        self.name = os.path.basename(path)
        self.size = os.path.getsize(self.path)
        self.sHash = shortHash
        self.fHash = fullHash
        self.matchMe = []

    def read_hash(self,block):
        """
        Reads the hash of the file up to the block
        Keyword Arguments:
        block -- the number of bytes to read, 0 if all
        """
        ifile = self.path
        block = int(block)
        hasher = hashlib.md5()
        with open(ifile, 'rb') as source:
            if block == 0 :
                print(ifile)
                buf = source.read()
            else:
                buf = source.read(block)
            hasher.update(buf)
        return(hasher.hexdigest())

    def set_short(self):
        """Sets the hash of the first BLOCKSIZE bytes of the file"""
        if self.sHash is None :
            self.sHash = self.read_hash(BLOCKSIZE)
        if BLOCKSIZE > self.size:
            self.fHash = self.sHash

    def set_full(self):
        """Sets the full hash of the file"""
        if self.fHash is None:
            self.fHash = self.read_hash(0)

    def say_me(self):
        """Returns a tuple with pathname, size, sHash, fHash"""
        a = (self.path, self.size, self.sHash, self.fHash)
        return a


class FileTree(object):
    """
    This class stores the file tree which is basically a list of HashMaker objects

    Keyword Argument:
    compareDir -- Specifies which is the directory to be searched

    """
    def __init__(self, compareDir):
        self.compareDir = os.path.normpath(compareDir)
        self.fileList = []
        self.sizedList = []
        self.sHList = []
        self.fHList = []
        self.get_files(self.compareDir)

    def get_files(self, cD):
        """Recursive method reads all the files in the given directory"""
        for f in os.listdir(cD):
            fpath = self.full_path(os.path.join(cD,f))
            if os.path.isfile(fpath):
                self.fileList.append(HashMaker(fpath))
            elif os.path.isdir(fpath) :
                #if RECURSE is set to true we'll dig right down
                if RECURSE:
                    #method calls itself on the subdir by joining the path and the subdir
                    self.get_files(fpath)
        if VERBOSE :
            print(len(self.fileList))

    def trim_by_size(self, chksize):
        """Writes to sizedList a list with all the files having the right size"""
        self.sizedList = []
        for f in self.fileList:
            if f.size == chksize:
                self.sizedList.append(f)

    def trim_by_sHash(self, chksHash):
        """Writes to sHList all the files matching chksHash in the sizedList"""
        self.sHList = []
        for f in self.sizedList:
            f.set_short()
            if f.sHash == chksHash:
                self.sHList.append(f)

    def trim_by_fHash(self, chkfHash):
        """Writes to fHList all the files matching chksHash in the sHList"""
        self.fHList = []
        for f in self.sHList :
            f.set_full()
            if f.fHash == chkfHash:
                self.fHList.append(f)

    def re_init(self):
        """Re-vanillas the File Tree without deleting or re-seeking"""
        self.sizedList = []
        self.sHList = []
        self.fHList = []

    def check(self, matchFile):
        """Checks which files in the search dir match a given (matchFile)
        hashMaker object. Returns an empty list for no result"""
        mD = matchFile
        returnList = []
        #mD will be a single HashMaker object
        self.re_init()
        self.trim_by_size(mD.size)
        if VERBOSE:
            print(str(len(self.sizedList))+" of " +
                  str(len(self.fileList)) + " matched on size...")
        if len(self.sizedList) > 0:
            mD.set_short()
            self.trim_by_sHash(mD.sHash)
            if VERBOSE:
                print(str(len(self.sHList))+ " of " +
                      str(len(self.sizedList)) + " matched on short hash")
            #if the trimmed short hash list has matches then continue and
            #trim by full hash
            if len(self.sHList) > 0:
                mD.set_full()
                self.trim_by_fHash(mD.fHash)
                if VERBOSE:
                    print(str(len(self.fHList))+ " of " +
                          str(len(self.sHList)) + " matched on full hash")
            else:
                #return no matches on semi-hash
                print("No Matches on semi-Hash")
        else:
            #return no matches on size
            print("No Matches on Size")
        for ff in self.fHList:
            if ff.path != mD.path:
                returnList.append(ff)
            else:
                print("Omitting self-detection match")
        return returnList

    def full_path(self, path):
        path = os.path.expandvars(os.path.normpath(path))
        return path


__author__          = "Marc Graham"
__copyright__       = "Copyright 2014"


