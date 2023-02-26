import argparse
import codecs
import os
import platform
import sys
import time
from ci_test_config import ci_config
from ci_tests.py_dym_interface.modelmanagement import ModelManagement
from ci_tests.py_dym_interface.PythonDymolaInterface import PythonDymolaInterface
from ci_tests.structure.sort_mo_model import modelica_model
from ci_tests.structure.config_structure import data_structure
from pathlib import Path


class StyleCheck(ci_config):

    def __init__(self,
                 dymola,
                 dymola_exception,
                 library: str,
                 dymola_version: int,
                 root_library: Path,
                 working_path: Path = Path(Path.cwd().parent),
                 add_libraries_loc: dict = None,
                 inst_libraries: list = None
                 ):
        """
        Class to Check the style of packages and models.
        Export HTML-Log File.
        Args:
            dymola (): dymola_python interface class
            dymola_exception (): dymola_exception class
            library (): library to test
            dymola_version (): dymola version (e.g. 2022)
        """
        self.library = library
        self.dymola_version = dymola_version
        self.working_path = working_path
        self.add_libraries_loc = add_libraries_loc
        self.inst_libraries = inst_libraries
        self.root_library = root_library
        super().__init__()
        self.dymola = dymola
        self.dymola_exception = dymola_exception
        self.dymola.ExecuteCommand("Advanced.TranslationInCommandLog:=true;")

    def __call__(self):
        dym_int = PythonDymolaInterface(dymola=self.dymola,
                                        dymola_exception=self.dymola_exception,
                                        dymola_version=self.dymola_version)
        # dym_int.dym_check_lic()
        dym_int.load_library(root_library=self.root_library, add_libraries_loc=self.add_libraries_loc)
        dym_int.install_library(libraries=self.inst_libraries)

    def read_log(self, file):
        """
        Args:
            file (): Read log file, if error exist variable 1 else 0
        """
        log_file = codecs.open(file, "r", encoding='utf8')
        error_list = list()
        for line in log_file:
            line = line.strip()
            if line.find("Check ok") > -1 or line.find("Library style check log") > -1 or len(line) == 0:
                continue
            else:
                print(f'{self.CRED}Error in model: {self.CEND}{line.lstrip()}')
                error_list.append(line)
        log_file.close()
        data_structure().prepare_data(source_target_dict={file: self.result_syntax_dir})
        if len(error_list) == 0:
            print(f'{self.green}Style check for library {self.library} was successful{self.CEND}')
            return 0
        elif len(error_list) > 0:
            print(f'{self.CRED}Test failed. Look in {self.library}_StyleErrorLog.html{self.CEND}')
            return 1


class Parser:
    def __init__(self, args):
        self.args = args

    def main(self):
        parser = argparse.ArgumentParser(description="Check the Style of Packages")
        check_test_group = parser.add_argument_group("Arguments to start style tests")
        check_test_group.add_argument("--packages", default=["Airflow"], nargs="+",
                                      help="Library to test (e.g. Airflow.Multizone)")
        check_test_group.add_argument("--root-library", default=Path("AixLib", "package.mo"),
                                      help="root of library",
                                      type=Path)
        check_test_group.add_argument("--library", default="AixLib",
                                      help="Path where top-level package.mo of the library is located")
        check_test_group.add_argument("--dymola-version", default="2022",
                                      help="Version of Dymola(Give the number e.g. 2022")
        check_test_group.add_argument("--changed-flag", default=False, action="store_true")
        args = parser.parse_args()
        return args


if __name__ == '__main__':
    args = Parser(sys.argv[1:]).main()
    dym = PythonDymolaInterface.load_dymola_python_interface(dymola_version=args.dymola_version)
    dymola = dym[0]
    dymola_exception = dym[1]

    mm = ModelManagement(dymola=dymola,
                         dymola_exception=dymola_exception,
                         dymola_version=args.dymola_version)
    mm.load_model_management()
    CheckStyle = StyleCheck(dymola=dymola,
                            dymola_exception=dymola_exception,
                            library=args.library,
                            dymola_version=args.dymola_version,
                            root_library=args.root_library,
                            working_path=Path(Path.cwd().parent),
                            add_libraries_loc=None,
                            inst_libraries=None)
    CheckStyle()
    mo = modelica_model()
    model_list = mo.get_option_model(library=args.library,
                                     package="",
                                     changed_flag=args.changed_flag)
    logfile = mm.mm_style_check(models_list=model_list,
                                library=args.library,
                                changed_flag=args.changed_flag)
    var = CheckStyle.read_log(file=logfile)
    exit(var)
