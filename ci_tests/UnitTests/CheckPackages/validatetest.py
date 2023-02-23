# /bin/bash
import argparse
import glob
import os
import platform
import sys
import time
from git import Repo
from natsort import natsorted
from pathlib import Path
from ci_test_config import ci_config
from ci_tests.structure.sort_mo_model import modelica_model
from ci_tests.structure.toml_to_py import Convert_types
from ci_tests.structure.config_structure import data_structure
import toml


class GitRepository(object):

    def __init__(self, repo_dir: Path, git_url: str):
        """
        Args:
            repo_dir ():  Folder of the cloned project.
            git_url (): Git url of the cloned project.
        """
        self.repo_dir = repo_dir
        self.git_url = git_url

    def clone_repository(self):
        """
        Pull git repository.
        """
        if os.path.exists(self.repo_dir):
            print(f'{self.repo_dir} folder already exists.')
        else:
            print(f'Clone {self.repo_dir} Repo')
            Repo.clone_from(self.git_url, self.repo_dir)


class CheckPythonDymola(ci_config):

    def __init__(self,
                 dym,
                 dym_exp,
                 library: str,
                 root_library: Path,
                 dymola_version: int = 2022,
                 working_path: Path = Path(Path.cwd().parent),
                 add_libraries_loc: dict = None,
                 inst_libraries: list = None):
        """
        The class check or simulate models. Return an error-log. Can filter models from a whitelist
        Args:
            dym (): python_dymola_interface class.
            dym_exp (): python_dymola_exception class.
            library (): library to test.

        """
        super().__init__()
        # [Libraries]
        self.root_library = root_library
        self.add_libraries_loc = add_libraries_loc
        self.install_libraries = inst_libraries
        self.library = library
        self.working_path = working_path
        # [dymola version]
        self.dymola_version = dymola_version
        # [Start Dymola]
        self.dymola = dym
        self.dymola_exception = dym_exp
        self.dymola.ExecuteCommand("Advanced.TranslationInCommandLog:=true;")

    def __call__(self):
        dym_int = PythonDymolaInterface(dymola=self.dymola,
                                        dymola_exception=self.dymola_exception)
        dym_int.dym_check_lic()
        dym_int.load_library(root_library=self.root_library, add_libraries_loc=self.add_libraries_loc)
        dym_int.install_library(libraries=self.install_libraries)

    def check_dymola_model(self,
                           check_model_list: list = None,
                           exception_list: list = None,
                           simulate_examples: bool = False):
        """
        Check models and return an error log, if the check failed
        Args:
            simulate_examples ():
            exception_list ():
            check_model_list (): list of models to be checked
        Returns:
            error_model_message_dic (): dictionary with models and its error message
        """
        error_model_message_dic = {}
        if len(check_model_list) == 0 or check_model_list is None:
            print(f'{self.CRED}Error:{self.CEND} Found no models in {self.single_package}.')
            exit(0)
        else:
            for model in check_model_list:
                try:
                    err_list = []
                    if simulate_examples is True:
                        res = self.dymola.checkModel(model, simulate=True)
                    else:
                        res = self.dymola.checkModel(model)
                    if res is True:
                        print(f'\n {self.green} Successful: {self.CEND} {model} \n')
                        continue
                    if res is False:
                        print(
                            f'Check for Model {model}{self.CRED} failed!{self.CEND}\n\n{self.CRED}Error:{self.CEND} {model}\nSecond Check Test for model {model}')
                        if simulate_examples is True:
                            sec_result = self.dymola.checkModel(model, simulate=True)
                        else:
                            sec_result = self.dymola.checkModel(model)
                        if sec_result is True:
                            print(f'\n {self.green} Successful: {self.CEND} {model} \n')
                            continue
                        if sec_result is False:
                            print(f'\n   {self.CRED}  Error:   {self.CEND}  {model}  \n')
                            log = self.dymola.getLastError()
                            for line in log.split("\n"):
                                exception_flag = False
                                if len(line) == 0:
                                    continue
                                if exception_list is not None:
                                    for exception in exception_list:
                                        if exception in line:
                                            exception_flag = True
                                    if exception_flag is False:
                                        err_list.append(line)
                                else:
                                    err_list.append(line)
                            if len(err_list) > 0:
                                print(f'\n   {self.CRED}  Error:   {self.CEND}  {model}  \n')
                                print(f'{log}')
                            else:
                                print(f'\n   {self.yellow}  Warning:   {self.CEND}  {model}  \n')
                                print(f'{log}')
                            error_model_message_dic[model] = log
                            continue

                except self.dymola_exception.DymolaFunctionException as err:
                    print("Simulation failed: " + str(err))
                    continue
        self.dymola.savelog(f'{self.dymola_log}')
        self.dymola.close()
        return error_model_message_dic

    def write_error_log(self,
                        pack: str = None,
                        error_dict: dict = None,
                        exception_list: list = None):
        """
        Write an error log with all models, that don´t pass the check
        Args:
            pack ():
            exception_list ():
            error_dict ():
        """
        if error_dict is not None:
            if pack is not None:
                ch_log = Path(self.working_path, self.result_check_result_dir, f'{self.library}.{pack}-check_log.txt')
                error_log = Path(self.working_path, self.result_check_result_dir,
                                 f'{self.library}.{pack}-error_log.txt')
                os.makedirs(Path(ch_log).parent, exist_ok=True)
                check_log = open(ch_log, "w")
                err_log = open(error_log, "w")
                for error_model in error_dict:
                    err_list = []
                    warning_list = []
                    for line in error_dict[error_model].split("\n"):
                        exception_flag = False
                        if len(line) == 0:
                            continue
                        if exception_list is not None:
                            for exception in exception_list:
                                if exception in line:
                                    exception_flag = True
                                    warning_list.append(line)
                            if exception_flag is False:
                                err_list.append(line)
                        else:
                            err_list.append(line)
                    if len(err_list) > 0:
                        check_log.write(f'\n\nError in model:  {error_model} \n')
                        err_log.write(f'\n\nError in model:  {error_model} \n')
                        for err in err_list:
                            check_log.write(err + "\n")
                            err_log.write(err + "\n")
                        if len(warning_list) > 0:
                            for warning in warning_list:
                                check_log.write(warning + "\n")
                        else:
                            for err in err_list:
                                check_log.write(err + "\n")
                                err_log.write(err + "\n")
                    else:
                        check_log.write(f'\n\nWarning in model:  {error_model} \n')
                        if len(warning_list) > 0:
                            for warning in warning_list:
                                check_log.write(warning + "\n")
                check_log.close()
                err_log.close()
                var = self._read_error_log(pack=pack, err_log=error_log, check_log=ch_log)
                if var != 0:
                    exit(var)
                return var
            else:
                print(f'Package is not set.')
                exit(1)
        else:
            print(f"{self.green}Check was successful.{self.CEND}")
            exit(0)

    def _read_error_log(self, pack: str, err_log, check_log):
        error_log = open(err_log, "r")
        lines = error_log.readlines()
        error_log_list = []
        for line in lines:
            if "Error in model" in line:
                error_log_list.append(line)
                line = line.strip("\n")
                print(f'{self.CRED}{line}{self.CEND}')
        if len(error_log_list) > 0:
            print(f'{self.CRED}Dymola check failed{self.CEND}')
            e_var = 1
        else:
            print(f'{self.green}Dymola check was successful{self.CEND}')
            e_var = 0
        error_log.close()
        self.prepare_data(source_target_dict={
            check_log: Path(self.result_check_result_dir, f'{self.library}.{pack}'),
            err_log: Path(self.result_check_result_dir, f'{self.library}.{pack}')},
            del_flag=True)
        return e_var


class CreateWhitelist(ci_config):

    def __init__(self,
                 dym,
                 dymola_ex,
                 library: str,
                 wh_library: str,
                 working_path: Path = Path(Path.cwd().parent),
                 dymola_version: int = 2022,
                 add_libraries_loc: dict = None,
                 inst_libraries: list = None,
                 repo_dir: Path = None,
                 git_url: str = None):
        """
        The class creates a whitelist of faulty models based on wh_library.
        Args:
            dym (): python_dymola_interface class.
            dymola_ex (): python_dymola_exception class.
            library (): library to be tested.
            wh_library ():  Library and its models that can be on the whitelist.
            repo_dir ():  Folder of the cloned project.
            git_url (): Git url of the cloned project.

        """
        super().__init__()
        self.wh_root_library = wh_root_library

        self.library = library
        self.wh_library = wh_library
        self.repo_dir = repo_dir
        self.git_url = git_url
        self.working_path = working_path
        # [Libraries]
        self.add_libraries_loc = add_libraries_loc
        self.install_libraries = inst_libraries
        self.library = library
        # [dymola version]
        self.dymola_version = dymola_version
        # [Start Dymola]
        self.dymola = dym
        self.dymola_exception = dymola_ex
        self.dymola.ExecuteCommand("Advanced.TranslationInCommandLog:=true;")

    def __call__(self):

        dym_int = PythonDymolaInterface(dymola=self.dymola, dymola_exception=self.dymola_exception)
        dym_int.dym_check_lic()
        dym_int.load_library(root_library=root_library, add_libraries_loc=self.add_libraries_loc)
        dym_int.install_library(libraries=self.install_libraries)

    def write_exit_log(self, vers_check: bool):
        """
        Write entry in exit file. Necessary for CI templates-
        Args:
            vers_check (): Boolean that check if the version number is up-to-date.
        """
        try:
            exit_file = open(self.config_ci_exit_file, "w")
            if vers_check is False:
                exit_file.write(f'FAIL')
            else:
                exit_file.write(f'successful')
            exit_file.close()
        except IOError:
            print(f'Error: File {self.config_ci_exit_file} does not exist.')
            exit(1)

    def read_script_version(self):
        """
        Returns:
            version (): return the latest version number of aixlib conversion script.
        """
        path = f'{self.library}{os.sep}Resources{os.sep}Scripts'
        filelist = (glob.glob(f'{path}{os.sep}*.mos'))
        if len(filelist) == 0:
            print(f'Cannot find a Conversion Script in {self.wh_library} repository.')
            exit(0)
        else:
            l_aixlib_conv = natsorted(filelist)[(-1)]
            l_aixlib_conv = l_aixlib_conv.split(os.sep)
            vers = (l_aixlib_conv[len(l_aixlib_conv) - 1])
            print(f'Latest {self.library} version: {vers}')
            return vers

    @staticmethod
    def check_whitelist_version(version, wh_file):
        """
        Check the latest whitelist version with the latest version of Aixlib conversion script.
        Read the last version of whitelist-
        Args:
            version (): Latest version number of aixlib conversion script.
        Returns:
            version_check (): Boolean - return true, if the whitelist version is equal to Aixlib conversion script version
            @param version:
            @param wh_file:
            @return:
        """
        try:
            version_file = open(wh_file, "r")
            lines = version_file.readlines()
            vers_check = False
            for line in lines:
                line = line.strip()
                if line.strip("\n") == version.strip("\n"):
                    print(f'Whitelist is on version {version}. The whitelist is already up to date')
                    vers_check = True
            version_file.close()
            return vers_check
        except IOError:
            print(f'Error: File {wh_file} does not exist.')
            exit(1)

    def check_whitelist_model(self, model_list: list, wh_files: Path, version: float, simulate_examples: bool):
        """
        Check whitelist_library models for creating whitelist and create a whitelist with failed models.
        Write an error log with all models, that don´t pass the check.
        Args:
            model_list (): List of models that are being tested
            version (): version number of whitelist based on the latest Aixlib conversion script.
            wh_files (): Path to withelist file
            simulate_examples() : bool simulate or not
        """
        error_model_message_dic = {}
        err_log = Path(self.working_path, f'{self.wh_library}-error_log.txt')
        dymola_log = Path(self.working_path, f'{self.wh_library}-log.txt')
        if model_list is None or len(model_list) == 0:
            print(f'{self.CRED}Error:{self.CEND} Found no models')
            exit(0)
        try:
            wh_files = open(wh_files, "w")
            error_log = open(err_log, "w")
            print(
                f'Write new whitelist for {self.wh_library} library\nNew whitelist was created with the version {version}')
            wh_files.write(f'\n{version} \n \n')
            for model in model_list:
                if simulate_examples is True:
                    result = self.dymola.checkModel(model, simulate=True)
                else:
                    result = self.dymola.checkModel(model)
                if result is True:
                    print(f'\n{self.green}Successful:{self.CEND} {model}\n')
                    continue
                if result is False:
                    print(f'\n{self.CRED}Error:{self.CEND} {model}\n')
                    log = self.dymola.getLastError()
                    print(f'{log}')
                    error_model_message_dic[model] = log
                    wh_files.write(f'\n{model} \n \n')
                    error_log.write(f'\n \n Error in model:  {model} \n{log}')
                    continue
            wh_files.close()
            error_log.close()
            self.dymola.savelog(f'{dymola_log}')
            self.dymola.close()
            print(f'Whitelist check finished.')
            self.prepare_data(source_target_dict={
                err_log: Path(self.result_whitelist_dir, f'{self.wh_library}'),
                dymola_log: Path(self.result_whitelist_dir, f'{self.wh_library}'),
                wh_files: Path(self.result_whitelist_dir, f'{self.wh_library}')})
            return error_model_message_dic

        except IOError:
            print(f'Error: File {wh_files} does not exist.')
            exit(1)


class PythonDymolaInterface(ci_config):

    def __init__(self, dymola, dymola_exception, dymola_version: int = 2022):
        """
        Args:
            dymola (): python-dymola interface
            dymola_exception ():  python-dymola exception
        """
        super().__init__()
        self.dymola = dymola
        self.dymola_exception = dymola_exception
        self.dymola.ExecuteCommand("Advanced.TranslationInCommandLog:=true;")
        self.dymola_version = dymola_version

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
        pass

    def load_library(self, root_library: Path = None, add_libraries_loc: dict = None):
        """
        Open library in dymola and  checks if the library was opened correctly.

        Args:
            root_library ():
            add_libraries_loc ():
        """
        if root_library is not None:
            pack_check = self.dymola.openModel(root_library)
            print(f'Library path: {self.lib_path}')
            if pack_check is True:
                print(
                    f'Found {self.library} Library and start check model test.\nCheck Package {self.single_package} \n')
            elif pack_check is False:
                print(f'Library path is wrong. Please check the path of {self.library} library path.')
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


def set_environment_variables(var, value):
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


def set_environment_path(dymola_version):
    """
    Args:
        dymola_version (): Version von dymola-docker image (e.g. 2022)
    Set path of python dymola interface for windows or linux
    """
    if platform.system() == "Windows":  # Checks the Operating System, Important for the Python-Dymola Interface
        set_environment_variables("PATH", os.path.join(os.path.abspath('.'), "Resources", "Library", "win32"))
        sys.path.insert(0, os.path.join('C:\\',
                                        'Program Files',
                                        'Dymola ' + dymola_version,
                                        'Modelica',
                                        'Library',
                                        'python_interface',
                                        'dymola.egg'))
    else:
        set_environment_variables("LD_LIBRARY_PATH",
                                  os.path.join(os.path.abspath('.'), "Resources", "Library", "linux32") + ":" +
                                  os.path.join(os.path.abspath('.'), "Resources", "Library", "linux64"))
        sys.path.insert(0, os.path.join('opt',
                                        'dymola-' + dymola_version + '-x86_64',
                                        'Modelica',
                                        'Library',
                                        'python_interface',
                                        'dymola.egg'))
    print(f'Operating system {platform.system()}')
    sys.path.append(os.path.join(os.path.abspath('.'), "..", "..", "BuildingsPy"))


class Parser:
    def __init__(self, args):
        self.args = args

    def main(self):
        parser = argparse.ArgumentParser(description="Check and validate single packages")
        check_test_group = parser.add_argument_group("Arguments to run check tests")
        # [Library - settings]
        """check_test_group.add_argument("--library", dest="library_dict", action=StoreDictKeyPair, nargs="*",
                                      metavar="Library1=Path_Lib1 Library2=Path_Lib2")
        check_test_group.add_argument("--package", dest="package_dict", action=StoreDictKeyPair_list, nargs="*",
                                      metavar="Library1=Package1,Package2 Library2=Package3,Package4")"""
        check_test_group.add_argument("--library", default="AixLib", help="Library to test (e.g. AixLib")
        check_test_group.add_argument("--packages", default=["Airflow"], nargs="+",
                                      help="Library to test (e.g. Airflow.Multizone)")
        check_test_group.add_argument("--root-library", default=Path(Path.cwd().parent, "AixLib", "package.mo"),
                                      help="root of library",
                                      type=Path)
        check_test_group.add_argument("--wh-library", default="IBPSA", help="library on a whitelist")
        check_test_group.add_argument("--root-wh-library",
                                      help="library on a whitelist")

        # [Dymola - settings]
        check_test_group.add_argument("-DS", "--dymola-version",
                                      default="2022",
                                      help="Version of dymola (Give the number e.g. 2020")
        # [ bool - flag]
        check_test_group.add_argument("--changed-flag", default=False, action="store_true")
        check_test_group.add_argument("--filter-wh-flag", default=False, action="store_true")
        check_test_group.add_argument("--extended-ex-flag", default=False, action="store_true")
        check_test_group.add_argument("--create-wh-flag", help="Create a whitelist of a library with failed models.",
                                      action="store_true")
        check_test_group.add_argument("--load-setting-flag",
                                      default=False,
                                      action="store_true")
        # [dym - Options: DYM_CHECK, DYM_SIM]
        check_test_group.add_argument("--dym-options",
                                      default=["DYM_CHECK"],
                                      help="Chose between openmodelica check, compare or simulate")
        # [repository - setting ]
        check_test_group.add_argument("--repo-dir", help="folder of a whitelist library ")
        check_test_group.add_argument("--git-url", default="https://github.com/ibpsa/modelica-ibpsa.git",
                                      help="url repository of whitelist library")
        args = parser.parse_args()
        return args


if __name__ == '__main__':
    args = Parser(sys.argv[1:]).main()
    set_environment_path(dymola_version=args.dymola_version)
    from dymola.dymola_interface import DymolaInterface
    from dymola.dymola_exception import DymolaException

    print(f'1: Starting Dymola instance')
    if platform.system() == "Windows":
        dymola = DymolaInterface()
        dymola_exception = DymolaException()
    else:
        dymola = DymolaInterface(dymolapath="/usr/local/bin/dymola")
        dymola_exception = DymolaException()

    if args.load_setting_flag is True:
        toml_file = f'Dymola_python_tests{os.sep}test_config.toml'
        data = toml.load(f'{toml_file}')
        install_libraries = data["Dymola_Check"]["install_libraries"]
        except_list = data["Dymola_Check"]["except_list"]
        additional_libraries_local = data["Dymola_Check"]["additional_libraries_local"]
        additional_libraries_local = Convert_types().convert_list_to_dict_toml(convert_list=additional_libraries_local,
                                                                               wh_library=args.wh_library)
    else:
        install_libraries = None
        except_list = None
        additional_libraries_local = None
    # [Check arguments, files, path]
    check = data_structure()
    check.check_arguments_settings(args.library, args.packages)
    check.check_file_setting(args.root_library)
    if additional_libraries_local is not None:
        for lib in additional_libraries_local:
            add_lib_path = Path(additional_libraries_local[lib], lib, "package.mo")
            check.check_file_setting(add_lib_path)

    dym = CheckPythonDymola(dym=dymola,
                            dym_exp=dymola_exception,
                            dymola_version=args.dymola_version,
                            library=args.library,
                            root_library=args.root_library,
                            add_libraries_loc=additional_libraries_local,
                            inst_libraries=install_libraries)
    dym()
    model = modelica_model()

    for package in args.packages:
        for options in args.dym_options:
            if options == "DYM_CHECK":
                model_list = model.get_option_model(library=args.library,
                                                    package=package,
                                                    wh_library=args.wh_library,
                                                    changed_flag=args.changed_flag,
                                                    simulate_flag=False,
                                                    filter_wh_flag=args.filter_wh_flag,
                                                    root_library=args.root_library)
                error_model_dict = dym.check_dymola_model(check_model_list=model_list,
                                                          exception_list=except_list,
                                                          simulate_examples=False)
                exit_var = dym.write_error_log(pack=package,
                                               error_dict=error_model_dict,
                                               exception_list=except_list)

            if args.dym_options == "DYM_SIM":
                model_list = model.get_option_model(library=args.library,
                                                    package=package,
                                                    wh_library=args.wh_library,
                                                    changed_flag=args.changed_flag,
                                                    simulate_flag=True,
                                                    filter_wh_flag=args.filter_wh_flag,
                                                    root_library=args.root_library)
                error_model_dict = dym.check_dymola_model(check_model_list=model_list,
                                                          exception_list=except_list,
                                                          simulate_examples=True)
                exit_var = dym.write_error_log(pack=package,
                                               error_dict=error_model_dict,
                                               exception_list=except_list)

    if args.create_wh_flag is True:
        check.check_arguments_settings(args.wh_library)
        mo = modelica_model()
        conf = ci_config()
        check.create_path(conf.config_ci_dir, conf.wh_ci_dir)
        wh = CreateWhitelist(dym=dymola,
                             dymola_ex=dymola_exception,
                             library=args.library,
                             wh_library=args.wh_library,
                             repo_dir=args.repo_dir,
                             git_url=args.git_url,
                             dymola_version=args.dymola_version,
                             add_libraries_loc=additional_libraries_local)
        wh()
        version = wh.read_script_version()
        for options in args.dym_options:
            if options == "DYM_CHECK":
                check.create_files(conf.wh_model_file, conf.config_ci_exit_file)
                version_check = wh.check_whitelist_version(version=version,
                                                           wh_file=conf.wh_model_file)
                wh.write_exit_log(vers_check=version_check)
                if version_check is False:
                    if args.git_url is not None and args.repo_dir is not None:
                        GitRepository(repo_dir=args.repo_dir,
                                      git_url=args.git_url).clone_repository()
                        root_wh_library = Path(args.working_path, args.repo_dir, args.wh_library, "package.mo")
                    elif args.root_wh_library is None:
                        root_wh_library = Path(Path.cwd().parent, args.wh_library, "package.mo")
                    elif args.root_wh_library is not None:
                        root_wh_library = args.root_wh_library
                    check.check_file_setting(root_wh_library)

                    model_list = mo.get_option_model(library=args.wh_library,
                                                     package=".",
                                                     wh_library=args.wh_library,
                                                     changed_flag=False,
                                                     simulate_flag=True,
                                                     filter_wh_flag=False,
                                                     extended_ex_flag=False,
                                                     root_library=root_wh_library)
                    wh.check_whitelist_model(model_list=model_list,
                                             wh_files=conf.wh_model_file,
                                             version=version,
                                             simulate_examples=False)

            if options == "DYM_SIM":
                check.create_files(conf.wh_simulate_file, conf.config_ci_exit_file)
                version_check = wh.check_whitelist_version(version=version,
                                                           wh_file=conf.wh_simulate_file)
                wh.write_exit_log(vers_check=version_check)
                if version_check is False:
                    if args.git_url is not None and args.repo_dir is not None:
                        GitRepository(repo_dir=args.repo_dir,
                                      git_url=args.git_url).clone_repository()
                        root_wh_library = Path(args.working_path, args.repo_dir, args.wh_library, "package.mo")
                    elif args.root_wh_library is None:
                        root_wh_library = Path(Path.cwd().parent, args.wh_library, "package.mo")
                    elif args.root_wh_library is not None:
                        root_wh_library = args.root_wh_library
                    check.check_file_setting(root_wh_library)
                    model_list = mo.get_option_model(library=args.wh_library,
                                                     package=".",
                                                     wh_library=args.wh_library,
                                                     changed_flag=False,
                                                     simulate_flag=True,
                                                     filter_wh_flag=False,
                                                     extended_ex_flag=False,
                                                     root_library=root_wh_library)
                    wh.check_whitelist_model(model_list=model_list,
                                             wh_files=conf.wh_simulate_file,
                                             version=version,
                                             simulate_examples=True)
