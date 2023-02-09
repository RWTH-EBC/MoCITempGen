# /bin/bash
import argparse
import glob
import os
import platform
import sys
import time
from git import Repo
from natsort import natsorted

sys.path.append(f'Dymola_python_tests{os.sep}CITests{os.sep}CI_Configuration')

from Dymola_python_tests.CI_test_config import CI_config
import matplotlib.pyplot as plt
import numpy as np
from ebcpy import DymolaAPI, TimeSeriesData
from ebcpy.utils.statistics_analyzer import StatisticsAnalyzer
from OMPython import OMCSessionZMQ
import pathlib
import shutil


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
                                                       changed_model=self.changed_model,
                                                       library=self.library,
                                                       package=self.single_package,
                                                       simulate_examples=self.simulate_examples,
                                                       filter_whitelist=self.filter_whitelist,
                                                       wh_library=self.wh_library,
                                                       root_package=self.root_package,
                                                       extended_example=self.extended_example,
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


class modelica_model(CI_config):

    def __init__(self):
        """
        return models or simulates to check
        Args:
        """
        super().__init__()

    def get_option_model(self, dymola, dymola_exception, changed_model: bool = False, library: str = "AixLib",
                         package: str = "Airflow",
                         simulate_examples: bool = False, filter_whitelist: bool = False, wh_library: str = "IBPSA",
                         root_package: str = "AixLib/Airflow", extended_example: bool = False,
                         dymola_version: int = 2022):
        if dymola is None:
            extended_example = False

        if changed_model is True:
            self.check_ci_structure(folders_list=[self.config_ci_dir],
                                    files_list=[self.config_ci_changed_file])
            model_list = self.get_changed_models(ch_file=self.config_ci_changed_file,
                                                 library=library,
                                                 single_package=package,
                                                 simulate_examples=simulate_examples)
        elif filter_whitelist is True:
            if simulate_examples is True:
                ci_wh_file = self.wh_simulate_file
                file_list = [self.wh_simulate_file]
            else:
                ci_wh_file = self.wh_model_file
                file_list = [self.wh_model_file]
            self.check_ci_structure(folders_list=self.wh_ci_dir,
                                    files_list=file_list)
            wh_list_models = self.get_wh_models(wh_file=ci_wh_file,
                                                wh_library=wh_library,
                                                library=library,
                                                single_package=package)
            result = self.get_models(path=root_package,
                                     library=library)
            model_list = result[0]
            if extended_example is True:
                simulate_list = Model_management(dymola=dymola,
                                                 dymola_exception=dymola_exception,
                                                 dymola_version=dymola_version).model_management_structure(
                    model_list=result[1],
                    library=library)
                model_list.extend(simulate_list)
                model_list = list(set(model_list))
            model_list = self.filter_wh_models(models=model_list,
                                               wh_list=wh_list_models)
        else:
            result = self.get_models(path=root_package,
                                     library=library)
            model_list = result[0]
            if extended_example is True:
                simulate_list = Model_management(dymola=dymola,
                                                 dymola_exception=dymola_exception,
                                                 dymola_version=dymola_version).model_management_structure(
                    model_list=result[1],
                    library=library)
                model_list.extend(simulate_list)
                model_list = list(set(model_list))
        if len(model_list) == 0 or model_list is None:
            print(f'Find no models in package {package}')
            exit(0)
        else:
            return model_list

    @staticmethod
    def get_wh_models(wh_file: str, wh_library: str, library: str, single_package: str):
        """
        Returns: return models that are on the whitelist
        """
        wh_list_models = list()
        try:
            wh_file = open(wh_file, "r")
            lines = wh_file.readlines()
            for line in lines:
                model = line.lstrip()
                model = model.strip().replace("\n", "")
                if model.find(f'{wh_library}.{single_package}') > -1:
                    print(f'Dont test {wh_library} model: {model}. Model is on the whitelist.')
                    wh_list_models.append(model.replace(wh_library, library))
                elif model.find(f'{library}.{single_package}') > -1:
                    print(f'Dont test {library} model: {model}. Model is on the whitelist.')
                    wh_list_models.append(model)
            wh_file.close()
            return wh_list_models
        except IOError:
            print(f'Error: File {wh_file} does not exist.')
            return wh_list_models

    @staticmethod
    def filter_wh_models(models, wh_list):
        """
        Args:
            models (): models from library.
            wh_list (): model from whitelist.
        Returns:
            return models from library who are not on the whitelist.
        """
        wh_list_mo = list()
        if len(models) == 0:
            exit(0)
        else:
            for element in models:
                for subelement in wh_list:
                    if element == subelement:
                        wh_list_mo.append(element)
            wh_list_mo = list(set(wh_list_mo))
            for example in wh_list_mo:
                models.remove(example)
            return models

    @staticmethod
    def _get_icon_example(filepath, library):
        """
        Args:
            filepath (): file of a dymola model.
            library (): library to test.
        Returns:
            example: return examples that have the string extends Modelica.Icons.Examples
        """
        try:
            ex_file = open(filepath, "r", encoding='utf8', errors='ignore')
            lines = ex_file.readlines()
            for line in lines:
                if line.find("extends") > -1 and line.find("Modelica.Icons.Example") > -1:
                    example = filepath.replace(os.sep, ".")
                    example = example[example.rfind(library):example.rfind(".mo")]
                    ex_file.close()
                    return example
        except IOError:
            print(f'Error: File {filepath} does not exist.')

    def get_changed_models(self, ch_file, library, single_package, simulate_examples):
        """
        Returns: return a list with changed models.
        """
        try:
            file = open(ch_file, "r", encoding='utf8', errors='ignore')
            lines = file.readlines()
            modelica_models = list()
            for line in lines:
                line = line.lstrip()
                line = line.strip().replace("\n", "")
                if line.rfind(".mo") > -1 and line.find("package") == -1:
                    if line.find(f'{library}{os.sep}{single_package}') > -1 and line.find("ReferenceResults") == -1:
                        if simulate_examples is True:
                            model_name = line[line.rfind(library):line.rfind('.mo') + 3]
                            example_test = self._get_icon_example(filepath=model_name,
                                                                  library=library)
                            if example_test is None:
                                print(
                                    f'Model {model_name} is not a simulation example because it does not contain the following "Modelica.Icons.Example"')
                                continue
                            else:
                                modelica_models.append(example_test)
                                continue
                        else:
                            model_name = line[line.rfind(library):line.rfind('.mo')]
                            model_name = model_name.replace(os.sep, ".")
                            model_name = model_name.replace('/', ".")
                            modelica_models.append(model_name)
                            continue
            if len(modelica_models) == 0:
                print(f'No models in Package: {single_package}')
                exit(0)
            file.close()
            return modelica_models
        except IOError:
            print(f'Error: File {ch_file} does not exist.')
            exit(0)

    def get_models(self, path: str, library: str = "AixLib", simulate_examples: bool = False,
                   extended_example: bool = False):
        """
            Args:
                path (): whitelist library or library path.
                library (): library to test.
            Returns:
                model_list (): return a list with models to check.
        """
        model_list = list()
        no_example_list = list()
        for subdir, dirs, files in os.walk(path):
            for file in files:
                filepath = subdir + os.sep + file
                if filepath.endswith(".mo") and file != "package.mo":
                    if simulate_examples is True:
                        example_test = self._get_icon_example(filepath=filepath,
                                                              library=library)
                        if example_test is None:
                            print(
                                f'Model {filepath} is not a simulation example because it does not contain the following "Modelica.Icons.Example"')
                            if extended_example is True:
                                no_example = filepath.replace(os.sep, ".")
                                no_example = no_example[no_example.rfind(library):no_example.rfind(".mo")]
                                no_example_list.append(no_example)
                            continue
                        else:
                            model_list.append(example_test)
                            continue
                    else:
                        model = filepath.replace(os.sep, ".")
                        model = model[model.rfind(library):model.rfind(".mo")]
                        model_list.append(model)
        if model_list is None or len(model_list) == 0:
            print(f'No models in package {path}')
            exit(0)
        else:
            return model_list, no_example_list


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


class Model_management(CI_config):

    def __init__(self, dymola, dymola_exception, dymola_version: int = 2022):
        super().__init__()
        self.dymola = dymola
        self.dymola_exception = dymola_exception
        self.dymola.ExecuteCommand("Advanced.TranslationInCommandLog:=true;")
        self.dymola_version = dymola_version

    def model_management_structure(self, model_list: list, library: str = "AixLib"):
        '''
        model = get_models(self,
                           path=self.single_package,
                           library=self.library)
        model_list = model[0]
        no_simulate_list = model[1]
        '''

        self._load_modelmanagement()
        simulate_list = list()
        for model in model_list:
            print(f' **** Check structure of model {model} ****')
            extended_list = self._get_extended_examples(model=model)
            used_list = self._get_used_models(model=model)
            extended_list.extend(used_list)
            for ext in extended_list:
                print(f'Extended model {ext} ')
                filepath = f'{ext.replace(".", os.sep)}.mo'
                example_test = modelica_model()._get_icon_example(filepath=filepath,
                                                                  library=library)
                if example_test is None:
                    print(f'File {filepath} is no example.')
                else:
                    simulate_list.append(model)
                    simulate_list.append(ext)
        simulate_list = list(set(simulate_list))
        return simulate_list

    def _load_modelmanagement(self):
        if platform.system() == "Windows":
            self.dymola.ExecuteCommand(
                'cd("C:\Program Files\Dymola ' + str(
                    self.dymola_version) + '\Modelica\Library\ModelManagement 1.1.8\package.moe");')
        else:
            self.dymola.ExecuteCommand(
                'cd("/opt/dymola-' + str(
                    self.dymola_version) + '-x86_64/Modelica/Library/ModelManagement 1.1.8/package.moe");')

    @staticmethod
    def _filter_modelica_types(model_list: list,
                               type_list=None):
        if type_list is None:
            type_list = ["Modelica", "Real", "Integer", "Boolean", "String"]
        extended_list = list()
        if model_list is not None:
            for extended_model in model_list:
                for types in type_list:
                    if extended_model.find(f'{types}') > -1:
                        extended_list.append(extended_model)
                        continue
                    else:
                        continue
        extended_list = list(set(extended_list))
        for ext in extended_list:
            model_list.remove(ext)
        model_list = list(set(model_list))
        return model_list

    def _get_extended_examples(self, model: str = ""):
        model_list = self.dymola.ExecuteCommand(f'ModelManagement.Structure.AST.Classes.ExtendsInClass("{model}");')
        extended_list = self._filter_modelica_types(model_list=model_list)
        return extended_list

    def _get_used_models(self, model: str = ""):
        model_list = self.dymola.ExecuteCommand(f'ModelManagement.Structure.Instantiated.UsedModels("{model}");')
        extended_list = self._filter_modelica_types(model_list=model_list)
        return extended_list


class Check_openModelica(CI_config):

    def __init__(self, dymola: None, dymola_exception: None, dymola_version: int = 2022, package: str = "Airflow",
                 om_options: str = "OM_CHECK", library: str = "AixLib", simulate_examples: bool = False,
                 changed_model: bool = False, wh_library: str = "IBPSA", filter_whitelist: bool = False,
                 extended_example: bool = False, lib_dir_dict=None):
        """
        Args:

        """
        super().__init__()
        if lib_dir_dict is None:
            lib_dir_dict = {}
        self.dymola = dymola
        self.dymola_exception = dymola_exception
        self.dymola_version = dymola_version
        self.package = package
        self.om_options = om_options
        self.library = library
        self.simulate_examples = simulate_examples
        self.changed_model = changed_model
        self.wh_library = wh_library
        self.filter_whitelist = filter_whitelist
        self.extended_example = extended_example
        self.err_log = f'{self.library}{os.sep}{self.library}.{self.package}-errorlog.txt'
        self.root_package = f'..{os.sep}{self.library}{os.sep}{self.package}'

        self.all_sims_dir = pathlib.Path("")
        self.lib_path = f'..{os.sep}{self.library}{os.sep}package.mo'
        self.omc = None
        self.dym_api = None
        self.for_bes_mod = self.library == "BESMod"
        self.lib_dir_dict = lib_dir_dict

    def check_OM_workflow(self):
        self.check_ci_structure(folders_list="_temp_results")
        os.chdir("_temp_results")
        self.check_arguments_settings(argument_list=[self.package, self.library])
        self.check_structure_setting(path_list=[self.root_package])

        model_list = modelica_model().get_option_model(dymola=self.dymola,
                                                       dymola_exception=self.dymola_exception,
                                                       changed_model=self.changed_model,
                                                       library=self.library,
                                                       package=self.package,
                                                       simulate_examples=self.simulate_examples,
                                                       filter_whitelist=self.filter_whitelist,
                                                       wh_library=self.wh_library,
                                                       root_package=self.root_package,
                                                       extended_example=self.extended_example,
                                                       dymola_version=self.dymola_version
                                                       )
        self.omc = self._load_library()
        ERROR_DATA = {}
        STATS = None
        if self.om_options == "OM_SIM":
            result = self._simulate_examples(example_list=model_list)
            self._write_errorlog(error_model=result[0], error_message=result[1])
        elif self.om_options == "DYMOLA_SIM":
            self.sim_with_dymola(simulate_example_list=model_list)
        elif self.om_options == "OM_CHECK":  # Check all Models in a Package
            result = self._checkmodel(model_list=model_list)
            self._write_errorlog(error_model=result[0], error_message=result[1])
        elif self.om_options == "COMPARE":
            ERROR_DATA, STATS = self.compare_dym_to_om(simulate_example_list=model_list,
                                                       stats=STATS)
        else:
            raise ValueError(f"{self.om_options} not supported")

        self.prepare_data(del_flag=True,
                          path_list=[f'{self.result_check_result_dir}{os.sep}{self.package}'],
                          file_path_dict={self.err_log: f'{self.result_check_result_dir}{os.sep}{self.package}'})

        with open(self.all_sims_dir.parent.joinpath("error_data.json"), "w+") as f:
            import json
            json.dump(ERROR_DATA, f, indent=2)
        with open(self.all_sims_dir.parent.joinpath("stats.json"), "w+") as f:
            import json
            json.dump(STATS, f, indent=2)

    def _checkmodel(self, model_list: list):
        print(f'Check models')
        error_model = []
        error_message = []
        for model in model_list:
            error_msg = self._perform_omc_check(model=model)
            if error_msg is not None:
                error_model.append(model)
                error_message.append(error_msg)
        self.omc.sendExpression("quit()")
        return error_model, error_message

    def _write_errorlog(self, error_model, error_message):
        """
        Write an error log with all models, that don´t pass the check
        Args:
            error_model ():
            error_message ():
        """
        os.makedirs(pathlib.Path(self.err_log).parent, exist_ok=True)
        error_log = open(self.err_log, "w")
        for model, message in zip(error_model, error_message):
            error_log.write(f'\n \n Error in model:  {model} \n')
            for line in message.split("\n"):
                if "Warning: Conversion-annotation contains unknown element: nonFromVersion" not in line:
                    error_log.write(line + "\n")
        error_log.close()

    def _load_library(self):
        if self.omc is not None:
            return self.omc
        t0 = time.time()
        omc = OMCSessionZMQ()
        omc.sendExpression('installPackage(Modelica_DeviceDrivers, "2.0.0", exactMatch=true)')
        if self.for_bes_mod:
            if platform.system() == "Windows":
                omc.sendExpression(
                    f'loadFile("C://Program Files//Dymola {self.dymola_version}//Modelica//Library//SDF 0.4.2//package.mo")')
            # omc.sendExpression(f'loadFile("AixLib//package.mo")')
            for lib_dir in self.lib_dir_dict:
                omc.sendExpression(
                    f'loadFile("{lib_dir}//installed_dependencies//{self.lib_dir_dict[lib_dir]}//{self.lib_dir_dict[lib_dir]}//package.mo")')

            ''' 
            omc.sendExpression(f'loadFile("{self.library_dir}//installed_dependencies//{self.wh_library}//{self.wh_library}//package.mo")')
            omc.sendExpression(f'loadFile("{self.library_dir}//installed_dependencies//{self.library}//{self.library}//package.mo")')
            omc.sendExpression(f'loadFile("{self.library_dir}//installed_dependencies//Buildings//Buildings//package.mo")')
            omc.sendExpression(f'loadFile("{self.library_dir}//installed_dependencies//BuildingSystems//BuildingSystems//package.mo")')
            omc.sendExpression(f'loadFile("{self.library_dir}//BESMod//package.mo")')
            '''
        else:
            pack_check = omc.sendExpression(f'loadFile("{self.lib_path}")')
            if pack_check is False:
                print(f'Cant load {self.lib_path}')
            else:
                print(f'Load {self.lib_path}')

        print(omc.sendExpression("getErrorString()"))
        return omc

    def _simulate_examples(self, example_list: list):
        """
        Simulate examples or validations
        Args:
            example_list:
        Returns:
        """
        print(f'Simulate examples and validations')
        error_model = []
        error_message = []
        if len(example_list) == 0:
            print(f'{self.CRED}Error:{self.CEND} Found no examples')
            exit(0)
        else:
            for model in example_list:
                error_msg = self._perform_omc_simulation(model=model)
                if error_msg is not None:
                    error_model.append(model)
                    error_message.append(error_msg)
        self.omc.sendExpression("quit()")
        return error_model, error_message

    def _perform_omc_check(self, model):
        self.omc = self._load_library()
        if self.omc.isPackage(model).startswith("true") or self.omc.isFunction(model).startswith("true"):
            return
        print(f"checking model ", model)
        result = self.omc.sendExpression(f"checkModel({model})")
        success = "completed successfully" in result
        if success:
            print(f'{self.green} Successful: {self.CEND} {model}')
            return
        print(f'{self.CRED}  Error:   {self.CEND}  {model}')
        _err_msg = self.omc.sendExpression("getErrorString()")
        print(f'{result}')
        return _err_msg

    def _perform_omc_simulation(self, model):
        self.omc = self._load_library()
        print(f'Simulate model: {model}')
        result = self.omc.sendExpression(f"simulate({model})")
        success = "The simulation finished successfully" in result["messages"]
        if success:
            print(f'\n {self.green}Successful:{self.CEND} {model}\n')
            shutil.copy(result["resultFile"], self.all_sims_dir.joinpath(model + ".mat"))
            return
        print(f'\n {self.CRED} Error: {self.CEND} {model}\n')
        _err_msg = result["messages"]
        _err_msg += "\n" + self.omc.sendExpression("getErrorString()")
        print(f'{_err_msg}')
        return _err_msg

    def sim_with_dymola(self, simulate_example_list: list):
        if self.dym_api is None:
            self.dym_api = DymolaAPI(
                cd=os.getcwd(),
                model_name=simulate_example_list[0],
                packages=[self.lib_path],
                extract_variables=True,
                load_experiment_setup=True
            )
        for model in simulate_example_list:
            print(f'Simulate model: {model}')
            try:
                self.dym_api.model_name = model
                print("Setup", self.dym_api.sim_setup)
                result = self.dym_api.simulate(return_option="savepath")
            except Exception as err:
                print("Simulation failed: " + str(err))
                continue
            print(f'\n {self.green}Successful:{self.CEND} {model}\n')
            shutil.copy(
                result,
                self.all_sims_dir.parent.joinpath("dym", model + ".mat")
            )
        self.dym_api.close()

    def compare_dym_to_om(self, simulate_example_list, stats=None, with_plot=True):
        if stats is None:
            stats = {
                "om": {
                    "failed": 0,
                    "success": 0,
                    "to_big_to_compare": 0
                },
                "dymola": {
                    "failed": 0,
                    "success": 0,
                    "to_big_to_compare": 0
                }
            }
        errors = {}
        om_dir = self.all_sims_dir
        dym_dir = self.all_sims_dir.parent.joinpath("dym")
        plot_dir = self.all_sims_dir.parent.joinpath("plots", self.package)
        _tol = 0.0001
        for model in simulate_example_list:
            continue_after_for = False
            for tool, _dir in zip(["om", "dymola"], [om_dir, dym_dir]):
                path_mat = _dir.joinpath(model + ".mat")
                if not os.path.exists(path_mat):
                    stats[tool]["failed"] += 1
                    continue_after_for = True
                    continue
                if os.stat(path_mat).st_size / (1024 * 1024) > 400:
                    stats[tool]["to_big_to_compare"] += 1
                    continue_after_for = True
                stats[tool]["success"] += 1
            if continue_after_for:
                continue

            om_tsd = TimeSeriesData(om_dir.joinpath(model + ".mat")).to_df()
            dym_tsd = TimeSeriesData(dym_dir.joinpath(model + ".mat")).to_df()
            om_tsd_ref = om_tsd.copy()

            cols = {}
            for c in dym_tsd.columns:
                cols[c] = c.replace(" ", "")
            dym_tsd = dym_tsd.rename(columns=cols)
            dym_tsd_ref = dym_tsd.copy()
            # Round index, sometimes it's 0.99999999995 instead of 1 e.g.
            om_tsd.index = np.round(om_tsd.index, 4)
            dym_tsd.index = np.round(dym_tsd.index, 4)
            # Drop duplicate rows, e.g. last point is often duplicate.
            om_tsd = om_tsd.drop_duplicates()
            dym_tsd = dym_tsd.drop_duplicates()
            idx_to_remove = []
            _n_diff_idx = 0
            for idx in om_tsd.index:
                if idx not in dym_tsd.index:
                    idx_to_remove.append(idx)
            om_tsd = om_tsd.drop(idx_to_remove)
            _n_diff_idx += len(idx_to_remove)
            idx_to_remove = []
            for idx in dym_tsd.index:
                if idx not in om_tsd.index:
                    idx_to_remove.append(idx)
            dym_tsd = dym_tsd.drop(idx_to_remove)
            _n_diff_idx += len(idx_to_remove)
            _col_err = {}
            _n_diff_cols = 0
            cols_to_plot = []
            for col in om_tsd.columns:
                if col not in dym_tsd.columns:
                    _n_diff_cols += 1
                    continue
                dym = dym_tsd.loc[:, col].values
                om = om_tsd.loc[:, col].values
                if np.std(om) + np.std(dym) <= 1e-5:
                    continue  # Stationary
                cols_to_plot.append(col)
                try:
                    _col_err[col] = StatisticsAnalyzer.calc_rmse(dym, om)
                except ValueError as err:
                    print(f"Index still differs {model}: {err}")
                    break
            for c in dym_tsd.columns:
                if c not in _col_err:
                    _n_diff_cols += 1
            if with_plot:
                _dir = plot_dir.joinpath(model)
                if cols_to_plot:
                    os.makedirs(_dir, exist_ok=True)
                for col in cols_to_plot:
                    plt.plot(om_tsd_ref.loc[:, col], label="OM")
                    plt.plot(dym_tsd_ref.loc[:, col], label="Dymola")
                    plt.legend()
                    plt.xlabel("Time in s")
                    plt.savefig(_dir.joinpath(col + ".png"))
                    plt.cla()

            errors[model] = {
                "average": np.mean(list(_col_err.values())),
                "detailed": _col_err,
                "n_diff_events": _n_diff_idx,
                "n_different_cols": _n_diff_cols
            }

        return errors, stats


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
    check_test_group.add_argument("-SE", "--simulate-examples", help="Check and simulate examples in the package",
                                  action="store_true")
    check_test_group.add_argument("-DS", "--dymola-version", default="2022",
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
