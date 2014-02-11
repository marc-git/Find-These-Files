import sys
from cx_Freeze import setup, Executable

setup(
    name = "Find These Files",
    version = "0.9.9",
    description = "Finds a file in a folder even if the names are different",
    executables = [Executable("ftfui.py", base = "Win32GUI")])
