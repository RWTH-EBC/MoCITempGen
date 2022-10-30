import argparse
import glob
import multiprocessing
import os
import platform
import sys
import time
from git import Repo
from natsort import natsorted

sys.path.append('Dymola_python_tests/CITests/CI_Configuration')
from configuration import CI_conf_class


class Git_Repository_Clone(object):

    def __init__(self, repo_dir, git_url):
        """
        Args:
            repo_dir ():  Folder of the cloned project.
            git_url (): Git url of the cloned project.
        """
        self.repo_dir = repo_dir
        self.git_url = git_url

    def _clone_repository(self):   
        """
        Pull git repository.
        """
        if os.path.exists(self.repo_dir):
            print(f'{self.repo_dir} folder already exists.')
        else:
            print(f'Clone {self.repo_dir} Repo')
            Repo.clone_from(self.git_url, self.repo_dir)



class ValidateTest(CI_conf_class):
    def __init__(self, dymola, dymola_exception, single_package, number_of_processors, show_gui, simulate_examples,
                 changedmodel, library,
                 wh_library, filterwhitelist):
        """
        The class check or simulate models. Return a error-log. Can filter models from a whitelist
        Args:
            dymola (): python_dymola_interface class.
            dymola_exception (): python_dymola_exception class.
            single_package (): Package to be testet.
            number_of_processors (): processors number.
            show_gui (): True - show dymola, false - dymola hidden.
            simulate_examples (): boolean - true: simulate examples
            changedmodel (): boolean - true: check or simulate only models in a commit .
            library (): library to test.
            wh_library (): whitelist library, filter failed models with a whitelist.
            filterwhitelist (): boolean - true: filter models from a whitelist.
        """
        self.single_package = single_package
        self.number_of_processors = number_of_processors
        self.show_gui = show_gui
        self.simulate_examples = simulate_examples
        self.changedmodel = changedmodel
        self.library = library
        self.wh_library = wh_library
        self.filterwhitelist = filterwhitelist
        self.lib_path = f'{self.library}{os.sep}package.mo'
        self.root_package = f'{self.library}{os.sep}{self.single_package}'
        self.err_log = f'{self.library}{os.sep}{self.library}.{self.single_package}-errorlog.txt'
        super().__init__()
        self.dymola = dymola
        self.dymola_exception = dymola_exception
        self.dymola.ExecuteCommand("Advanced.TranslationInCommandLog:=true;")  # Writes all information in the log file.

    def _dym_check_lic(self):
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

    def _check_packages(self):
        """
            Check CI variables
        """
        if self.single_package is None:
            print(f'{self.CRED}Error:{self.CEND} Package is missing!')
            exit(1)
        else:
            print(f'Setting: Package {self.single_package}')
        if self.library is None:
            print(f'{self.CRED}Error:{self.CEND} Library is missing!')
            exit(1)
        else:
            print(f'Setting: library {self.library}')

    def _library_path_check(self):
        """
        Open library in dymola and and checks if the library was opened correctly.
        """
        pack_check = self.dymola.openModel(self.lib_path)
        print(f'Library path: {self.lib_path}')
        if pack_check is True:
            print(f'Found {self.library} Library and start check model test.\nCheck Package {self.single_package} \n')
        elif pack_check is False:
            print(f'Library path is wrong. Please check the path of {self.library} library path.')
            exit(1)

    def _whitelist_library_check(self):   # Check arguments: whitelist library
        if self.wh_library is None:
            print(f'{self.CRED}Error:{self.CEND} Whitelist library is missing!')
            exit(1)
        else:
            print(f'Setting: Whitelist library {self.wh_library}')

    def _check_result(self, error_model_message_dic):
        """
        Args:
            error_model_message_dic ():  Dictionary with models and its error message.
        """
        if len(error_model_message_dic) == 0:
            print(f'Test was {self.green}Successful!{self.CEND}')
            exit(0)
        if len(error_model_message_dic) > 0:
            print(f'Test {self.CRED}failed!{self.CEND}')
            for model in error_model:
                print(f'{self.CRED}Error:{self.CEND} Check Model {model}')
            exit(1)
        if error_model_message_dic is None:
            print(f'Don´t find models that failed.')
            exit(1)

    def _write_errorlog(self, error_model_message_dic):
        """
        Write a Error log with all models, that don´t pass the check.
        Args:
            error_model_message_dic (): dictionary with models and its error message
        """
        try:
            error_log = open(self.err_log, "w")
            for model in error_model_message_dic:
                error_log.write(f'\n \n Error in model:  {model} \n')
                error_log.write(str(error_model_message_dic[model]))
            error_log.close()
        except IOError:
            print(f'Error: File {self.err_log} does not exist.')
            exit(0)

    def _get_model(self):
        """
        Get Models to check or simulate
          Returns: list of models from a package
        """
        model_list = []
        for subdir, dirs, files in os.walk(self.root_package):
            for file in files:
                filepath = subdir + os.sep + file
                if filepath.endswith(".mo") and file != "package.mo":
                    model = filepath.replace(os.sep, ".")
                    model = model[model.rfind(self.library):model.rfind(".mo")]
                    model_list.append(model)
        if len(model_list) == 0:
            print(f'No models in package {self.single_package}')
            exit(1)
        else:
            return model_list

    def _get_changed_models(self):
        """
        Returns: return a list with changed models
        """
        try:
            print(f'Test only changed or new models')
            changed_model_file = open(self.config_ci_changed_file, "r", encoding='utf8')
            lines = changed_model_file.readlines()
            modelica_models = []
            for line in lines:
                if line.rfind(".mo") > -1 and line.find("package") == -1:
                    if line.find(f'{self.library}{os.sep}{self.single_package}') > -1 and line.find(
                            "ReferenceResults") == -1:
                        model_name = line.replace(os.sep, ".")
                        model_name = model_name.replace('/', ".")
                        modelica_models.append(model_name)
                        continue
            if len(modelica_models) == 0:
                print(f'No changed models in Package: {self.single_package}')
                exit(0)
            changed_model_file.close()
            return modelica_models
        except IOError:
            print(f'Error: File {self.config_ci_changed_file} does not exist.')
            exit(0)

    def _get_icon_example(self, filepath):
        """
        Args:
            filepath (): file of a dymola model

        Returns:
            example: return examples that have the string extends Modelica.Icons.Examples
        """
        try:
            ex_file = open(filepath, "r", encoding='utf8', errors='ignore')
            lines = ex_file.readlines()
            for line in lines:
                if line.find("extends") > -1 and line.find("Modelica.Icons.Example") > -1:
                    example = filepath.replace(os.sep, ".")
                    example = example[example.rfind(self.library):example.rfind(".mo")]
                    ex_file.close()
                    return example
        except IOError:
            print(f'Error: File {filepath} does not exist.')
            exit(0)

    def _get_simulate_examples(self):
        """
        Returns: return example list that have the string extends Modelica.Icons.Examples
        """
        example_list = []
        for subdir, dirs, files in os.walk(self.root_package):
            for file in files:
                filepath = subdir + os.sep + file
                if filepath.endswith(".mo") and file != "package.mo":
                    example = self._get_icon_example(filepath=filepath)
                    if example is None:
                        print(
                            f'Model {filepath} is not a simulation example because it does not contain the following "Modelica.Icons.Example"')
                        continue
                    else:
                        example_list.append(example)
                        continue
        if example_list is None or len(example_list) == 0:
            print(f'No models in package {self.single_package}')
            exit(0)
        else:
            return example_list

    def _get_changed_simulate_examples(self):  # list all changed examples in package
        """
        Returns: return changed or new examples that have the string extends Modelica.Icons.Examples
        """
        print(f'Test only changed or new models')
        example_list = []
        try:
            changed_model_file = open(self.config_ci_changed_file, "r", encoding='utf8',
                                      errors='ignore')
            lines = changed_model_file.readlines()
            for line in lines:
                if line.rfind(".mo") > -1 and line.find("package") == -1:
                    if line.find(f'{self.library}{os.sep}{self.single_package}') > -1 and line.find(
                            "ReferenceResults") == -1:
                        model = line.lstrip()
                        model = model.strip().replace("\n", "")
                        model_name = model[model.rfind(self.library):]
                        example = self._get_icon_example(filepath=model_name)
                        example_list.append(example)
            changed_model_file.close()
            if len(example_list) == 0:
                print(f'No changed models in Package: {self.single_package}')
                exit(0)
            else:
                return example_list
        except IOError:
            print(f'Error: File {self.config_ci_changed_file} does not exist.')
            exit(1)

    def _filter_wh_models(self, models, wh_list):
        """
        Args:
            models (): models from library.
            wh_list (): model from whitelist.
        Returns:
            return models from library who are not on the whitelist.
        """
        wh_list_mo = []
        if len(models) == 0:
            print(f'No examples models in package: {self.single_package}')
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

    def _get_wh_models(self):
        """
        Returns: return models who are on the whitelist
        """
        wh_list_models = []
        try:
            wh_file = open(self.wh_model_file, "r")
            lines = wh_file.readlines()
            for line in lines:
                model = line.lstrip()
                model = model.strip().replace("\n", "")
                if model.find(f'{self.wh_library}.{self.single_package}') > -1:
                    print(f'Dont test {self.wh_library} model: {model}. Model is on the whitelist.')
                    wh_list_models.append(model.replace(self.wh_library, self.library))
                elif model.find(f'{self.library}.{self.single_package}') > -1:
                    print(f'Dont test {self.library} model: {model}. Model is on the whitelist.')
                    wh_list_models.append(model)
            wh_file.close()
            return wh_list_models
        except IOError:
            print(f'Error: File {self.wh_model_file} does not exist.')
            return wh_list_models

    def _checkmodel(self, model_list):
        """
        Check models and return a Error Log, if the check failed
        Args:
            model_list (): list of models to be checked
        Returns:
            error_model_message_dic (): dictionary with models and its error message
        """
        self._library_path_check()
        error_model_message_dic = {}
        if len(model_list) == 0:
            print(f'{self.CRED}Error:{self.CEND} Found no models in {self.single_package}.')
            exit(0)
        else:
            print(f'Check models')
            for model in model_list:
                result = self.dymola.checkModel(model)
                if result is True:
                    print(f'\n {self.green} Successful: {self.CEND} {model} \n')
                    continue
                if result is False:
                    print(
                        f'Check for Model {model}{self.CRED} failed!{self.CEND}\n\n{self.CRED}Error:{self.CEND} {model}\nSecond Check Test for model {model}')
                    sec_result = self.dymola.checkModel(model)
                    if sec_result is True:
                        print(f'\n {self.green} Successful: {self.CEND} {model} \n')
                        continue
                    if sec_result is False:
                        print(f'\n   {self.CRED}  Error:   {self.CEND}  {model}  \n')
                        log = self.dymola.getLastError()
                        error_model_message_dic[model] = log
                        print(f'{log}')
                        continue
            self.dymola.savelog(self.library + "." + self.single_package + "-log.txt")
            self.dymola.close()
            return error_model_message_dic

    def _simulate_examples(self, example_list):
        """
        Simulate examples or validations
        Args:
            example_list (): list of examples to be simulated
        Returns:
            error_model_message_dic (): dictionary with models and its error message
        """
        print(f'\n\nSimulate examples and validations')
        self._library_path_check()
        error_model_message_dic = {}
        if example_list is None or len(example_list) == 0:
            print(f'{self.CRED}Error:{self.CEND} Found no examples in {self.single_package}.')
            exit(0)
        else:
            for example in example_list:
                print(f'        Simulate model: {example}')
                result = self.dymola.checkModel(example, simulate=True)
                if result is True:
                    print(f'\n      {self.green}Successful:{self.CEND} {example}\n')
                if result is False:
                    print(
                        f'\n      Simulate model {example} {self.CRED} failed!{self.CEND}\n      Second check test '
                        f'for model {example}')
                    sec_result = self.dymola.checkModel(example, simulate=True)
                    if sec_result is True:
                        print(f'\n      {self.green}Successful:{self.CEND} {example}\n')
                    if sec_result is False:
                        print(f'\n      {self.CRED}Error: {self.CEND} {example}\n')
                        log = self.dymola.getLastError()
                        print(f'{log}')
                        error_model_message_dic[example] = log

        self.dymola.savelog(self.library + "." + self.single_package + "-log.txt")
        self.dymola.close()
        return error_model_message_dic


    def check_model_workflow(self):
        """
        Check models in package.
            changedmodel: boolean - true: Test only changed or new models
            filterwhitelist: boolean - true  Filter model on whitelist
        """
        self._check_packages()
        self._dym_check_lic()
        if self.changedmodel is True:
            CI_conf_class()._check_ci_folder_structure(folder_list=[self.config_ci_dir])
            CI_conf_class()._check_ci_file_structure(file_list=[self.config_ci_changed_file])
            model_list = self._get_changed_models()
        elif self.filterwhitelist is True:
            CI_conf_class()._check_ci_folder_structure(folder_list=[self.wh_ci_dir])
            CI_conf_class()._check_ci_file_structure(file_list=[self.wh_model_file])
            self._whitelist_library_check()
            wh_list = self._get_wh_models()
            models = self._get_model()
            model_list = self._filter_wh_models(models=models, wh_list=wh_list)
        else:
            model_list = self._get_model()
        if len(model_list) == 0:
            print(f'Find no models in package {self.single_package}')
            exit(0)
        else:
            error_model_message_dic = self._checkmodel(model_list=model_list)
            self._write_errorlog(error_model_message_dic=error_model_message_dic)
            self._check_result(error_model_message_dic=error_model_message_dic)

    def simulate_example_workflow(self):
        """
        Simulate examples in package.
            changedmodel: boolean - true: Test only changed or new models
            filterwhitelist: boolean - true  Filter model on whitelist
        """
        self._check_packages()
        self._dym_check_lic()
        if self.changedmodel is True:
            CI_conf_class()._check_ci_folder_structure(folder_list=[self.config_ci_dir])
            CI_conf_class()._check_ci_file_structure(file_list=[self.config_ci_changed_file])
            simulate_example_list = self._get_changed_simulate_examples()
        elif self.filterwhitelist is True:
            CI_conf_class()._check_ci_folder_structure(folder_list=[self.wh_ci_dir])
            CI_conf_class()._check_ci_file_structure(file_list=[self.wh_model_file])
            self._whitelist_library_check()
            wh_list = self._get_wh_models()
            models = self._get_simulate_examples()
            simulate_example_list = self._filter_wh_models(models=models, wh_list=wh_list)
        else:
            simulate_example_list = self._get_simulate_examples()
        if len(simulate_example_list) == 0:
            print(f'Find no examples in package {self.single_package}')
        else:
            error_model_message_dic = self._simulate_examples(example_list=simulate_example_list)
            self._write_errorlog(error_model_message_dic=error_model_message_dic)
            self._check_result(error_model_message_dic=error_model_message_dic)


class Create_whitelist(CI_conf_class):

    def __init__(self, dymola, dymola_exception, library, wh_library, repo_dir, git_url, simulate_examples):
        """
        The class creates a whitelist of faulty models based on wh_library.
        Args:
            dymola (): python_dymola_interface class.
            dymola_exception (): python_dymola_exception class.
            library (): library to be tested.
            wh_library ():  Library and its models that can be on the whitelist.
            repo_dir ():  Folder of the cloned project.
            git_url (): Git url of the cloned project.
        """
        self.library = library
        self.wh_library = wh_library
        self.repo_dir = repo_dir
        self.git_url = git_url
        self.simulate_examples = simulate_examples
        self.wh_lib_path = f'{self.wh_library}{os.sep}{self.wh_library}{os.sep}package.mo'
        self.err_log = f'{self.wh_library}{os.sep}{self.wh_library}-errorlog.txt'
        super().__init__()
        self.dymola = dymola
        self.dymola_exception = dymola_exception
        self.dymola.ExecuteCommand(
            "Advanced.TranslationInCommandLog:=true;")  # Writes all information in the log file

    def _write_whitelist_errorlog(self, error_model_message_dic):
        """
        Write an error log with all models, that don´t pass the check.
        Args:
            error_model_message_dic ():  Dictionary with models and its error message.
        """
        try:
            error_log = open(self.err_log, "w")
            for model in error_model_message_dic:
                error_log.write(f'\n \n Error in model:  {model} \n')
                error_log.write(str(error_model_message_dic[model]))
            error_log.close()
        except IOError:
            print(f'Error: File {self.err_log} does not exist.')
            exit(1)

    def _write_whitelist(self, error_model_message_dic, version, wh_file):
        """
        Write a new whitelist.
        Args:
            error_model_message_dic ():  dictionary with models and its error message.
            version (): version number of whitelist based on the latest Aixlib conversion script.
        """
        try:
            wh_file = open(wh_file, "w")
            wh_file.write(f'\n{version} \n \n')
            for model in error_model_message_dic:
                wh_file.write(f'\n{model} \n \n')
            print(
                f'Write new writelist for {self.wh_library} library\nNew whitelist was created with the version {version}')
            wh_file.close()
        except IOError:
            print(f'Error: File {wh_file} does not exist.')
            exit(1)

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
            version = (l_aixlib_conv[len(l_aixlib_conv) - 1])
            print(f'Latest {self.library} version: {version}')
            return version

    def _check_whitelist_version(self, version, wh_file):
        """
        Check the latest whitelist version with the latest version of Aixlib conversion script.
        Args:
            version (): Latest version number of aixlib conversion script.
        Returns:
            version_check (): Boolean - return true, if the whitelist version is equal to Aixlib conversion script version
        """
        try:
            vfile = open(wh_file, "r")  # Read the last version of whitelist
            lines = vfile.readlines()
            version_check = False
            for line in lines:
                line = line.strip()
                if line.strip("\n") == version.strip("\n"):
                    print(f'Whitelist is on version {version}. The whitelist is already up to date')
                    version_check = True
            vfile.close()
            return version_check
        except IOError:
            print(f'Error: File {wh_file} does not exist.')
            exit(1)

    def _get_icon_example(self, filepath):
        """
        Args:
            filepath (): file of a dymola model

        Returns:
            example: return examples that have the string extends Modelica.Icons.Examples
        """
        try:
            ex_file = open(filepath, "r", encoding='utf8', errors='ignore')
            lines = ex_file.readlines()
            for line in lines:
                if line.find("extends") > -1 and line.find("Modelica.Icons.Example") > -1:
                    example = filepath.replace(os.sep, ".")
                    example = example[example.rfind(self.library):example.rfind(".mo")]
                    ex_file.close()
                    return example
        except IOError:
            print(f'Error: File {filepath} does not exist.')
            exit(0)

    def _get_wh_examples(self, wh_path):
        """
            Args:
                wh_path (): whitelist library path
            Returns:
                model_list (): return a list with models to check
        """
        example_list = []
        for subdir, dirs, files in os.walk(wh_path):
            for file in files:
                filepath = subdir + os.sep + file
                if filepath.endswith(".mo") and file != "package.mo":
                    example = self._get_icon_example(filepath=filepath)
                    if example is None:
                        print(
                            f'Model {filepath} is not a simulation example because it does not contain the following "Modelica.Icons.Example"')
                        continue
                    else:
                        example_list.append(example)
                        continue
        if example_list is None or len(example_list) == 0:
            print(f'No models in package {self.single_package}')
            exit(0)
        else:
            return example_list

    def _get_wh_model(self, wh_path):
        """
        Args:
            wh_path (): whitelist library path
        Returns:
            model_list (): return a list with models to check
        """
        model_list = []
        for subdir, dirs, files in os.walk(wh_path):
            for file in files:
                filepath = subdir + os.sep + file
                if filepath.endswith(".mo") and file != "package.mo":
                    model = filepath.replace(os.sep, ".")
                    model = model[model.rfind(self.wh_library):model.rfind(".mo")]
                    model_list.append(model)
        if len(model_list) == 0:
            print(f'No Models')
            exit(1)
        return model_list

    def _dym_check_lic(self):
        """
        Check dymola license.
        """
        dym_sta_lic_available = self.dymola.ExecuteCommand('RequestOption("Standard");')
        lic_counter = 0
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
            f'2: Using Dymola port {str(self.dymola._portnumber)}\n{self.green}Dymola License is available{self.CEND}')

    def _check_whitelist_model(self, model_list):
        """
        Check whitelist_library models for creating whitelist.
        Args:
            model_list (): List of models that are being tested
        Returns:
            error_model_message_dic (): dictionary with models and its error message
        """
        package_check = self.dymola.openModel(self.wh_lib_path)
        print(f'Library path: {self.wh_lib_path}')
        if package_check is True:
            print(f'Found {self.wh_library} Library and check models in library {self.wh_library} \n')
        elif package_check is False:
            print(f'Library path is wrong. Please check path of {self.wh_library} library path.')
            exit(1)
        error_model_message_dic = {}
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
                continue
        self.dymola.savelog(f'{self.wh_library}-log.txt')
        self.dymola.close()
        return error_model_message_dic

    def _check_ci_var_settings(self):
        """
        Check CI variables
        """
        if self.wh_library is None:
            print(f'{self.CRED}Error:{self.CEND} Whitelist library is missing!')
            exit(1)
        else:
            print(f'Setting: Whitelist library {self.wh_library}')
        if self.library is None:
            print(f'{self.CRED}Error{self.CEND}: Library is missing!')
            exit(1)
        else:
            print(f'Setting: Library {self.library}')
        if self.git_url is None and self.wh_lib_path is None:
            print(f'{self.CRED}Error:{self.CEND} git url or whitelist path is missing!')
            exit(1)
        if self.git_url is not None:
            print(f'Setting: whitelist git url library {self.git_url}')
        if self.repo_dir is None:
            print(f'{self.CRED}Error:{self.CEND} Repository directory is missing!')
            exit(1)
        else:
            print(f'Setting: Repository url: {self.repo_dir}')



    def create_wh_workflow(self):
        """
        Workflow for creating the whitelist based on a library.
        """
        CI_conf_class()._check_ci_folder_structure(folder_list=[self.config_ci_dir, self.wh_ci_dir])
        self._check_ci_var_settings()
        if self.simulate_examples is False:
            CI_conf_class()._check_ci_file_structure(file_list=[self.wh_model_file, self.config_ci_exit_file])
            version = self.read_script_version()
            version_check = self._check_whitelist_version(version=version, wh_file=self.wh_model_file)
            self._write_exit_log(version_check=version_check)
            if version_check is False:
                model_list = []
                if self.git_url is not None:
                    Git_Class = Git_Repository_Clone(repo_dir=self.repo_dir,
                                                     git_url=self.git_url)
                    Git_Class._clone_repository()
                    model_list = self._get_wh_model(wh_path=self.repo_dir)
                elif self.wh_lib_path is not None:
                    print(f'Setting: Whitelist path library {self.wh_lib_path}')
                    model_list = self._get_wh_model(wh_path=self.wh_lib_path)
                self._dym_check_lic()
                error_model_message_dic = self._check_whitelist_model(model_list=model_list)
                self._write_whitelist(error_model_message_dic=error_model_message_dic, version=version, wh_file=self.wh_model_file)
                self._write_whitelist_errorlog(error_model_message_dic=error_model_message_dic)
                exit(0)
            else:
                exit(0)
        else:
            CI_conf_class()._check_ci_file_structure(file_list=[self.wh_simulate_file, self.config_ci_exit_file])
            version = self.read_script_version()
            version_check = self._check_whitelist_version(version=version, wh_file=self.wh_simulate_file)
            self._write_exit_log(version_check=version_check)
            if version_check is False:
                model_list = []
                if self.git_url is not None:
                    Git_Class = Git_Repository_Clone(repo_dir=self.repo_dir,
                                                     git_url=self.git_url)
                    Git_Class._clone_repository()
                    model_list = self._get_wh_examples(wh_path=self.repo_dir)
                elif self.wh_lib_path is not None:
                    print(f'Setting: Whitelist path library {self.wh_lib_path}')
                    model_list = self._get_wh_examples(wh_path=self.wh_lib_path)
                self._dym_check_lic()
                error_model_message_dic = self._check_whitelist_model(model_list=model_list)
                self._write_whitelist(error_model_message_dic=error_model_message_dic, version=version, wh_file=self.wh_simulate_file)
                self._write_whitelist_errorlog(error_model_message_dic=error_model_message_dic)
                exit(0)
            else:
                exit(0)



def _setEnvironmentVariables(var, value):  # Add to the environment variable 'var' the value 'value'
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


def _setEnvironmentPath(dymolaversion):
    """
    Args:
        dymolaversion (): Version von dymola-docker image (e.g. 2022)
    Set path of python dymola interface for windows or linux
    """
    if platform.system() == "Windows":  # Checks the Operating System, Important for the Python-Dymola Interface
        _setEnvironmentVariables("PATH", os.path.join(os.path.abspath('.'), "Resources", "Library", "win32"))
        sys.path.insert(0, os.path.join('C:\\',
                                        'Program Files',
                                        'Dymola ' + dymolaversion,
                                        'Modelica',
                                        'Library',
                                        'python_interface',
                                        'dymola.egg'))
    else:
        _setEnvironmentVariables("LD_LIBRARY_PATH",
                                 os.path.join(os.path.abspath('.'), "Resources", "Library", "linux32") + ":" +
                                 os.path.join(os.path.abspath('.'), "Resources", "Library", "linux64"))
        sys.path.insert(0, os.path.join('opt',
                                        'dymola-' + dymolaversion + '-x86_64',
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
                                  help="Test only the Modelica package AixLib.Package")
    check_test_group.add_argument("-n", "--number-of-processors", type=int, default=multiprocessing.cpu_count(),
                                  help="Maximum number of processors to be used")
    check_test_group.add_argument("--show-gui", help="show the GUI of the simulator", action="store_true")
    check_test_group.add_argument("-WL", "--whitelist",
                                  help="Create a WhiteList of IBPSA Library.",
                                  action="store_true")
    check_test_group.add_argument("-SE", "--simulate-examples", help="Check and simulate examples in the package",
                                  action="store_true")
    check_test_group.add_argument("-DS", "--dymolaversion", default="2020",
                                  help="Version of dymola (Give the number e.g. 2020")
    check_test_group.add_argument("-CM", "--changedmodel", default=False, action="store_true")
    check_test_group.add_argument("-FW", "--filterwhitelist", default=False, action="store_true")
    check_test_group.add_argument("-l", "--library", default="AixLib", help="Library to test")
    check_test_group.add_argument("-wh-l", "--wh-library", help="Library to test")
    check_test_group.add_argument("--repo-dir", help="Library to test")
    check_test_group.add_argument("--git-url", default="https://github.com/ibpsa/modelica-ibpsa.git",
                                  help="url repository")
    check_test_group.add_argument("--wh-path", help="path of white library")
    args = parser.parse_args()
    _setEnvironmentPath(dymolaversion=args.dymolaversion)
    from dymola.dymola_interface import DymolaInterface  # Load dymola_python interface
    from dymola.dymola_exception import DymolaException  # Load dymola_python exception
    print(f'1: Starting Dymola instance')
    if platform.system() == "Windows":
        dymola = DymolaInterface()
        dymola_exception = DymolaException()
    else:
        dymola = DymolaInterface(dymolapath="/usr/local/bin/dymola")
        dymola_exception = DymolaException()
    if args.whitelist is True:  # Write a new whiteList
        wh = Create_whitelist(dymola=dymola,
                              dymola_exception=dymola_exception,
                              library=args.library,
                              wh_library=args.wh_library,
                              repo_dir=args.repo_dir,
                              git_url=args.git_url,
                              simulate_examples=args.simulate_examples)
        wh.create_wh_workflow()
    else:
        CheckModelTest = ValidateTest(dymola=dymola,
                                      dymola_exception=dymola_exception,
                                      single_package=args.single_package,
                                      number_of_processors=args.number_of_processors,
                                      show_gui=args.show_gui,
                                      simulate_examples=args.simulate_examples,
                                      changedmodel=args.changedmodel,
                                      library=args.library,
                                      wh_library=args.wh_library,
                                      filterwhitelist=args.filterwhitelist)
        if args.simulate_examples is True:  # Simulate models
            CheckModelTest.simulate_example_workflow()
        else:  # Check all models in a package
            CheckModelTest.check_model_workflow()
