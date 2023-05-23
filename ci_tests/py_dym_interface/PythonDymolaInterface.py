from ci_test_config import ci_config
import platform
from pathlib import Path
import time
import os
import sys


class PythonDymolaInterface:

    def __init__(self,
                 dymola: classmethod = None,
                 dymola_exception: classmethod = None):
        """
        Args:
            dymola ():
            dymola_exception ():
            dymola_version ():
        """
        super().__init__()
        self.dymola = dymola
        self.dymola_exception = dymola_exception
        # todo exception mit einbauen
        if self.dymola is not None:
            self.dymola.ExecuteCommand("Advanced.TranslationInCommandLog:=true;")
        # Color
        self.CRED = f"\033[91m"
        self.CEND = f"\033[0m"
        self.green = f"\033[0;32m"
        self.yellow = f"\033[33m"
        self.blue = f"\033[44m"

    def dym_check_lic(self):
        """
            Check dymola license.
        """
        lic_counter = 0
        dym_sta_lic_available = self.dymola.ExecuteCommand('RequestOption("Standard");')
        while dym_sta_lic_available is False:
            print(f'{self.CRED} No Dymola License is available {self.CEND} \n Check Dymola license after 180.0 seconds')
            self.dymola.close()
            time.sleep(180.0)
            dym_sta_lic_available = self.dymola.ExecuteCommand('RequestOption("Standard");')
            lic_counter += 1
            if lic_counter > 10:
                if dym_sta_lic_available is False:
                    print(f'There are currently no available Dymola licenses available. Please try again later.')
                    self.dymola.close()
                    exit(1)
        print(
            f'2: Using Dymola port {str(self.dymola._portnumber)} \n {self.green} Dymola License is available {self.CEND}')

    def install_library(self, libraries: list = None):
        """
        Args:
            libraries ():
        """
        # Add function if necessary
        # todo: add function to install dymola libraries
        pass

    def load_library(self, root_library: Path = None, add_libraries_loc: dict = None):
        """
        Open library in dymola and  checks if the library was opened correctly.
        Args:
            root_library ():
            add_libraries_loc ():
        """
        if root_library is not None:
            print(f'Library path: {root_library}')
            pack_check = self.dymola.openModel(str(root_library))
            if pack_check is True:
                print(
                    f'{self.green}Found {root_library.parent} Library and start checks. {self.CEND}\n')
            elif pack_check is False:
                print(
                    f'{self.CRED}Error: {self.CEND} Library path is wrong.Please check the path of {root_library} library path.')
                exit(1)
        else:
            print(f'Library path is not set.')
            exit(1)
        if add_libraries_loc is not None:
            for library in add_libraries_loc:
                lib_path = Path(add_libraries_loc[library], library, "package.mo")
                load_add_bib = self.dymola.openModel(lib_path)
                if load_add_bib is True:
                    print(f'{self.green}Load library {library}:{self.CEND} {lib_path}')
                else:
                    print(f'{self.CRED}Error:{self.CEND} Load of library {library} with path {lib_path} failed!')
                    exit(1)


    def set_environment_variables(self, var, value):
        """
        Args:
            var ():
            value ():
        """
        if var in os.environ:
            if platform.system() == "Windows":
                os.environ[var] = value + ";" + os.environ[var]
            else:
                os.environ[var] = value + ":" + os.environ[var]
        else:
            os.environ[var] = value

    def set_environment_path(self, dymola_version):
        """
        Checks the Operating System, Important for the Python-Dymola Interface
        Args:
            dymola_version (): Version von dymola-docker image (e.g. 2022)
        Set path of python dymola interface for windows or linux
        """
        if platform.system() == "Windows":
            self.set_environment_variables("PATH",
                                           os.path.join(os.path.abspath('.'), "Resources", "Library",
                                                        "win32"))
            sys.path.insert(0, os.path.join('C:\\',
                                            'Program Files',
                                            'Dymola ' + dymola_version,
                                            'Modelica',
                                            'Library',
                                            'python_interface',
                                            'dymola.egg'))
        else:
            self.set_environment_variables("LD_LIBRARY_PATH",
                                           os.path.join(os.path.abspath('.'), "Resources", "Library",
                                                        "linux32") + ":" +
                                           os.path.join(os.path.abspath('.'), "Resources", "Library",
                                                        "linux64"))
            sys.path.insert(0, os.path.join('/opt',
                                            'dymola-' + dymola_version + '-x86_64',
                                            'Modelica',
                                            'Library',
                                            'python_interface',
                                            'dymola.egg'))
        print(f'Operating system {platform.system()}')
        sys.path.append(os.path.join(os.path.abspath('.'), "..", "..", "BuildingsPy"))

    @staticmethod
    def load_dymola_python_interface(dymola_version: int = 2022):
        """
        Load dymola python interface and dymola exception
        Args:
            dymola_version ():
        Returns:
        """
        PythonDymolaInterface().set_environment_path(dymola_version=dymola_version)
        from dymola.dymola_interface import DymolaInterface
        from dymola.dymola_exception import DymolaException
        print(f'1: Starting Dymola instance')
        if platform.system() == "Windows":
            dymola = DymolaInterface()
            dymola_exception = DymolaException()
        else:
            dymola = DymolaInterface(dymolapath="/usr/local/bin/dymola")
            dymola_exception = DymolaException()
        return dymola, dymola_exception
