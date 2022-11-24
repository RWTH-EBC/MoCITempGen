#!/usr/bin/env python
"""Deletes all temporary files created by Dymola, starting
   at the current working directory and recursively searching the 
   subdirectories for files.
   In the current directory, the subdirectory 'binaries' will also be
   deleted as Dymola 2013 creates this directory when exporting an FMU.
"""
import fnmatch
import os
import shutil
import sys


class CleanModelica(object):

    def __init__(self):
        """
        List of files that should be deleted
        Directories to be deleted. This will be non-recursive
        """
        self.delete_files = ['buildlog.txt', 'dsfinal.txt', 'dsin.txt', 'dslog.txt',
                             'dsmodel*', 'dymosim', 'dymosim.lib', 'dymosim.exp',
                             'dymosim.dll', 'dymola.log', 'dymosim.exe', '*.mat', '*.mof',
                             '*.bak-mo', 'request.', 'status.', 'status', 'failure',
                             'success.',
                             'stop', 'stop.',
                             'fmiModelIdentifier.h', 'modelDescription.xml',
                             'fmiFunctions.o',
                             'CSVWriter.csvWriter.csv', 'test.csv']
        self.delete_dirs = ['binaries']

    def delete_files_func(self):
        """
        Array in which the names of the files that will be deleted are stored
        """
        matches = []
        for root, dirnames, filenames in os.walk('.'):
            for file in self.delete_files:
                for filename in fnmatch.filter(filenames, file):
                    matches.append(os.path.join(root, filename))
            if '.svn' in dirnames:  # Exclude .svn directories
                dirnames.remove('.svn')
        matches = list(set(matches))  # Removed duplicate entries which may be due to wildcards
        for f in matches:  # Delete the files
            sys.stdout.write("Deleting file '" + f + "'.\n")
            os.remove(f)

    def delete_dir_func(self):  # Delete directories
        for folder in self.delete_dirs:
            if os.path.exists(folder):
                sys.stdout.write("Deleting directory '" + folder + "'.\n")
                shutil.rmtree(folder)


if __name__ == "__main__":
    clean = CleanModelica()
    clean.delete_files_func()
    clean.delete_dir_func()






        
