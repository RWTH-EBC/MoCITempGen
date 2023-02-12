# /bin/bash
import argparse
import glob
import os
import platform
import sys
import time
from git import Repo
from natsort import natsorted
from Dymola_python_tests.CI_test_config import CI_config



class Git_Repository_Clone(object):

    def __init__(self, repo_dir: str, git_url: str):
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


class Check_python_dymola(CI_config):

    def __init__(self,
                 dymola,
                 dymola_exception,
                 dymola_version: int = 2022,
                 single_package: str = "Airflow",
                 simulate_examples: bool = False,
                 changed_model: bool = False,
                 library: str = "AixLib",
                 wh_library: str = "IBPSA",
                 filter_whitelist: bool = False,
                 extended_example: bool = False):
        """
        The class check or simulate models. Return an error-log. Can filter models from a whitelist
        Args:
            dymola (): python_dymola_interface class.
            dymola_exception (): python_dymola_exception class.
            single_package (): Package to be testet.
            simulate_examples (): boolean - true: simulate examples
            changed_model (): boolean - true: check or simulate only models in a commit .
            library (): library to test.
            wh_library (): whitelist library, filter failed models with a whitelist.
            filter_whitelist (): boolean - true: filter models from a whitelist.
        """
        self.single_package = single_package
        self.simulate_examples = simulate_examples
        self.changed_model = changed_model
        self.library = library
        self.wh_library = wh_library
        self.filter_whitelist = filter_whitelist
        self.extended_example = extended_example
        self.dymola_version = dymola_version
        self.lib_path = f'{self.library}{os.sep}package.mo'
        self.root_package = f'{self.library}{os.sep}{self.single_package}'
        self.err_log = f'{self.library}{os.sep}{self.library}.{self.single_package}-errorlog.txt'
        self.dymola_log = f'{self.library}.{self.single_package}-log.txt'
        super().__init__()
        self.dymola = dymola
        self.dymola_exception = dymola_exception
        self.dymola.ExecuteCommand("Advanced.TranslationInCommandLog:=true;")

    def _library_path_check(self):
        """
        Open library in dymola and  checks if the library was opened correctly.
        """
        pack_check = self.dymola.openModel(self.lib_path)
        print(f'Library path: {self.lib_path}')
        if pack_check is True:
            print(f'Found {self.library} Library and start check model test.\nCheck Package {self.single_package} \n')
        elif pack_check is False:
            print(f'Library path is wrong. Please check the path of {self.library} library path.')
            exit(1)

    def _check_model(self, model_list):
        """
        Check models and return an error log, if the check failed
        Args:
            model_list (): list of models to be checked
        Returns:
            error_model_message_dic (): dictionary with models and its error message
        """
        error_model_message_dic = {}
        if len(model_list) == 0:
            print(f'{self.CRED}Error:{self.CEND} Found no models in {self.single_package}.')
            exit(0)
        else:
            try:
                error_log = open(self.err_log, "w")
                for model in model_list:
                    if self.simulate_examples is True:
                        result = self.dymola.checkModel(model, simulate=True)
                    else:
                        result = self.dymola.checkModel(model)
                    if result is True:
                        print(f'\n {self.green} Successful: {self.CEND} {model} \n')
                        continue
                    if result is False:
                        print(
                            f'Check for Model {model}{self.CRED} failed!{self.CEND}\n\n{self.CRED}Error:{self.CEND} {model}\nSecond Check Test for model {model}')
                        if self.simulate_examples is True:
                            sec_result = self.dymola.checkModel(model, simulate=True)
                        else:
                            sec_result = self.dymola.checkModel(model)
                        if sec_result is True:
                            print(f'\n {self.green} Successful: {self.CEND} {model} \n')
                            continue
                        if sec_result is False:
                            print(f'\n   {self.CRED}  Error:   {self.CEND}  {model}  \n')
                            log = self.dymola.getLastError()
                            error_model_message_dic[model] = log
                            print(f'{log}')
                            error_log.write(f'\n \n Error in model:  {model} \n{log}')
                            continue
                error_log.close()
            except IOError:
                print(f'Error: File {self.err_log} does not exist.')
                exit(0)
        self.dymola.savelog(f'{self.dymola_log}')
        self.dymola.close()
        return error_model_message_dic

    def check_result(self, error_model_message_dic):
        """
        Args:
            error_model_message_dic ():  Dictionary with models and its error message.
        """
        if len(error_model_message_dic) == 0:
            print(f'Test was {self.green}Successful!{self.CEND}')
            return 0
        if len(error_model_message_dic) > 0:
            print(f'Test {self.CRED}failed!{self.CEND}')
            for model in error_model_message_dic:
                print(f'{self.CRED}Error:{self.CEND} Check Model {model}')
            return 1
        if error_model_message_dic is None:
            print(f'Don´t find models that failed.')
            return 1

    def check_model_workflow(self):
        """
        Check models in package.
            changed_model: boolean - true: Test only changed or new models
            filter_whitelist: boolean - true  Filter model on whitelist
        """
        self.check_arguments_settings(argument_list=[self.single_package, self.library])
        self.check_structure_setting(path_list=[self.root_package])
        """python_dymola_interface(dymola=self.dymola,
                                dymola_exception=self.dymola_exception).dym_check_lic()"""
        model_list = modelica_model().get_option_model(dymola=self.dymola,
                                                       dymola_exception=self.dymola_exception,
                                                       changed_flag=self.changed_model,
                                                       library=self.library,
                                                       package=self.single_package,
                                                       simulate_flag=self.simulate_examples,
                                                       filter_wh_flag=self.filter_whitelist,
                                                       wh_library=self.wh_library,
                                                       root_package=self.root_package,
                                                       extended_ex_flag=self.extended_example,
                                                       dymola_version=self.dymola_version)
        self._library_path_check()
        error_model_message_dic = self._check_model(model_list=model_list)
        self.prepare_data(del_flag=True,
                          path_list=[f'{self.result_check_result_dir}{os.sep}{self.single_package}'],
                          file_path_dict={self.err_log: f'{self.result_check_result_dir}{os.sep}{self.single_package}',
                                          f'{self.library}{os.sep}{self.dymola_log}': f'{self.result_check_result_dir}{os.sep}{self.single_package}'})
        var = self.check_result(error_model_message_dic=error_model_message_dic)
        return var


class Create_whitelist(CI_config):

    def __init__(self, dymola, dymola_exception, library: str = "AixLib", wh_library: str = "IBPSA",
                 repo_dir: str = "", git_url: str = "", simulate_examples: bool = False, dymola_version: int = 2022):
        """
        The class creates a whitelist of faulty models based on wh_library.
        Args:
            dymola (): python_dymola_interface class.
            dymola_exception (): python_dymola_exception class.
            library (): library to be tested.
            wh_library ():  Library and its models that can be on the whitelist.
            repo_dir ():  Folder of the cloned project.
            git_url (): Git url of the cloned project.
            simulate_examples (): boolean - true: simulate examples
        """
        self.library = library
        self.wh_library = wh_library
        self.repo_dir = repo_dir
        self.git_url = git_url
        self.simulate_examples = simulate_examples
        self.dymola_version = dymola_version
        self.wh_lib_path = f'{self.wh_library}{os.sep}{self.wh_library}{os.sep}package.mo'
        self.err_log = f'{self.wh_library}{os.sep}{self.wh_library}-errorlog.txt'
        self.dymola_log = f'{self.wh_library}-log.txt'
        super().__init__()
        self.dymola = dymola
        self.dymola_exception = dymola_exception
        self.dymola.ExecuteCommand(
            "Advanced.TranslationInCommandLog:=true;")

    def _write_exit_log(self, version_check):
        """
        Write entry in exit file. Necessary for CI templates-
        Args:
            version_check (): Boolean that check if the version number is up-to-date.
        """
        try:
            exit_file = open(self.config_ci_exit_file, "w")
            if version_check is False:
                exit_file.write(f'FAIL')
            else:
                exit_file.write(f'successful')
            exit_file.close()
        except IOError:
            print(f'Error: File {self.config_ci_exit_file} does not exist.')
            exit(1)

    def _read_script_version(self):
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
            version = (l_aixlib_conv[len(l_aixlib_conv) - 1])
            print(f'Latest {self.library} version: {version}')
            return version

    @staticmethod
    def _check_whitelist_version(version, wh_file):
        """
        Check the latest whitelist version with the latest version of Aixlib conversion script.
        Read the last version of whitelist-
        Args:
            version (): Latest version number of aixlib conversion script.
        Returns:
            version_check (): Boolean - return true, if the whitelist version is equal to Aixlib conversion script version
        """
        try:
            version_file = open(wh_file, "r")
            lines = version_file.readlines()
            version_check = False
            for line in lines:
                line = line.strip()
                if line.strip("\n") == version.strip("\n"):
                    print(f'Whitelist is on version {version}. The whitelist is already up to date')
                    version_check = True
            version_file.close()
            return version_check
        except IOError:
            print(f'Error: File {wh_file} does not exist.')
            exit(1)

    def _check_whitelist_model(self, model_list, wh_file, version):
        """
        Check whitelist_library models for creating whitelist and create a whitelist with failed models.
        Write an error log with all models, that don´t pass the check.
        Args:
            model_list (): List of models that are being tested
            version (): version number of whitelist based on the latest Aixlib conversion script.
        """
        package_check = self.dymola.openModel(self.wh_lib_path)
        print(f'Library path: {self.wh_lib_path}')
        if package_check is True:
            print(f'Found {self.wh_library} Library and check models in library {self.wh_library} \n')
        elif package_check is False:
            print(f'Library path is wrong. Please check path of {self.wh_library} library path.')
            exit(1)
        error_model_message_dic = {}
        if model_list is None or len(model_list) == 0:
            print(f'{self.CRED}Error:{self.CEND} Found no models')
            exit(0)
        try:
            wh_file = open(wh_file, "w")
            error_log = open(self.err_log, "w")
            print(
                f'Write new whitelist for {self.wh_library} library\nNew whitelist was created with the version {version}')
            wh_file.write(f'\n{version} \n \n')
            for model in model_list:
                if self.simulate_examples is True:
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
                    wh_file.write(f'\n{model} \n \n')
                    error_log.write(f'\n \n Error in model:  {model} \n{log}')
                    continue
            wh_file.close()
            error_log.close()
        except IOError:
            print(f'Error: File {wh_file} does not exist.')
            exit(1)
        self.dymola.savelog(f'{self.dymola_log}')
        self.dymola.close()
        print(f'Whitelist check finished.')
        return error_model_message_dic

    def create_wh_workflow(self):
        """
        Workflow for creating the whitelist based on a whitelist-library.
        """
        self.check_arguments_settings(argument_list=[self.wh_library, self.library, self.git_url, self.repo_dir])
        self.check_ci_folder_structure(folders_list=[self.config_ci_dir, self.wh_ci_dir])
        if self.simulate_examples is True:
            file_list = [self.wh_simulate_file, self.config_ci_exit_file]
            wh_file = self.wh_simulate_file
        else:  # Check models
            file_list = [self.wh_model_file, self.config_ci_exit_file]
            wh_file = self.wh_model_file
        self.check_ci_file_structure(files_list=file_list)
        version = self._read_script_version()
        version_check = self._check_whitelist_version(version=version,
                                                      wh_file=wh_file)
        self._write_exit_log(version_check=version_check)
        if version_check is False:
            mo = modelica_model()
            model_list = list()
            if self.git_url is not None:
                Git_Repository_Clone(repo_dir=self.repo_dir,
                                     git_url=self.git_url).clone_repository()
                model_list = mo.get_models(path=self.repo_dir,
                                           library=self.wh_library)[0]
            elif self.wh_lib_path is not None:
                print(f'Setting: Whitelist path library {self.wh_lib_path}')
                model_list = mo.get_models(path=self.wh_lib_path,
                                           library=self.wh_library)[0]
            python_dymola_interface(dymola=self.dymola,
                                    dymola_exception=self.dymola_exception).dym_check_lic()
            self._check_whitelist_model(model_list=model_list,
                                        wh_file=wh_file,
                                        version=version)

            self.prepare_data(path_list=[f'{self.result_whitelist_dir}_{self.wh_library}'],
                              file_path_dict={wh_file: f'{self.result_whitelist_dir}_{self.wh_library}',
                                              self.err_log: f'{self.result_check_result_dir}_{self.wh_library}',
                                              f'{self.wh_library}{os.sep}{self.dymola_log}': f'{self.result_check_result_dir}_{self.wh_library}'
                                              })
            exit(0)
        else:
            exit(0)



class python_dymola_interface(CI_config):

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





def _setEnvironmentVariables(var, value):
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


def _setEnvironmentPath(dymola_version):
    """
    Args:
        dymola_version (): Version von dymola-docker image (e.g. 2022)
    Set path of python dymola interface for windows or linux
    """
    if platform.system() == "Windows":  # Checks the Operating System, Important for the Python-Dymola Interface
        _setEnvironmentVariables("PATH", os.path.join(os.path.abspath('.'), "Resources", "Library", "win32"))
        sys.path.insert(0, os.path.join('C:\\',
                                        'Program Files',
                                        'Dymola ' + dymola_version,
                                        'Modelica',
                                        'Library',
                                        'python_interface',
                                        'dymola.egg'))
    else:
        _setEnvironmentVariables("LD_LIBRARY_PATH",
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Check and validate single packages")
    check_test_group = parser.add_argument_group("Arguments to run check tests")
    check_test_group.add_argument('-s', "--single-package", metavar="AixLib.Package",
                                  help="Test the Modelica package")
    check_test_group.add_argument("-WL", "--whitelist",
                                  help="Create a whitelist of a library with failed models.",
                                  action="store_true")
    check_test_group.add_argument("-SE", "--simulate-examples",
                                  help="Check and simulate examples in the package",
                                  action="store_true")
    check_test_group.add_argument("-DS", "--dymola-version",
                                  default="2022",
                                  help="Version of dymola (Give the number e.g. 2020")
    check_test_group.add_argument("-CM", "--changed-model", default=False, action="store_true")
    check_test_group.add_argument("-FW", "--filter-whitelist", default=False, action="store_true")
    check_test_group.add_argument("-l", "--library", default="AixLib", help="Library to test")
    check_test_group.add_argument("-wh-l", "--wh-library", default="IBPSA", help="library on a whitelist")
    check_test_group.add_argument("--repo-dir", help="folder of a whitelist library ")
    check_test_group.add_argument("--git-url", default="https://github.com/ibpsa/modelica-ibpsa.git",
                                  help="url repository of whitelist library")
    check_test_group.add_argument("--extended-example", default=False, action="store_true")
    check_test_group.add_argument("--tool", default="dymola",
                                  help="Chose between dymola or openModelica")
    check_test_group.add_argument("--om-options", default="om_check",
                                  help="Chose between openmodelica check, compare or simulate")
    check_test_group.add_argument("--dymola-tool", help="Check and simulate examples in the package",
                                  action="store_true", default=True)
    args = parser.parse_args()
    if args.dymola_tool is False:
        om = Check_openModelica(dymola=None,
                                dymola_version=args.dymola_version,
                                dymola_exception=None,
                                package=args.single_package,
                                om_options=args.om_options,
                                library=args.library,
                                simulate_examples=args.simulate_examples,
                                changed_model=args.changed_model,
                                wh_library=args.wh_library,
                                filter_whitelist=args.filter_whitelist,
                                extended_example=args.extended_example,
                                )
        om.check_OM_workflow()

    else:
        _setEnvironmentPath(dymola_version=args.dymola_version)
        from dymola.dymola_interface import DymolaInterface
        from dymola.dymola_exception import DymolaException

        print(f'1: Starting Dymola instance')
        if platform.system() == "Windows":
            dymola = DymolaInterface()
            dymola_exception = DymolaException()
        else:
            dymola = DymolaInterface(dymolapath="/usr/local/bin/dymola")
            dymola_exception = DymolaException()

        if args.tool == "dymola":

            if args.whitelist is True:
                wh = Create_whitelist(dymola=dymola,
                                      dymola_exception=dymola_exception,
                                      library=args.library,
                                      wh_library=args.wh_library,
                                      repo_dir=args.repo_dir,
                                      git_url=args.git_url,
                                      simulate_examples=args.simulate_examples,
                                      dymola_version=args.dymola_version)
                wh.create_wh_workflow()


            else:
                Check = Check_python_dymola(dymola=dymola,
                                            dymola_exception=dymola_exception,
                                            single_package=args.single_package,
                                            simulate_examples=args.simulate_examples,
                                            changed_model=args.changed_model,
                                            library=args.library,
                                            wh_library=args.wh_library,
                                            filter_whitelist=args.filter_whitelist,
                                            extended_example=args.extended_example,
                                            dymola_version=args.dymola_version)
                var = Check.check_model_workflow()

                exit(var)

        if args.tool == "openModelica":
            om = Check_openModelica(dymola=dymola,
                                    dymola_version=args.dymola_version,
                                    dymola_exception=dymola_exception,
                                    package=args.single_package,
                                    om_options=args.om_options,
                                    library=args.library,
                                    simulate_examples=args.simulate_examples,
                                    changed_model=args.changed_model,
                                    wh_library=args.wh_library,
                                    filter_whitelist=args.filter_whitelist,
                                    extended_example=args.extended_example,
                                    )
            om.check_OM_workflow()
        else:
            raise ValueError(f"{args.tool} not supported")
