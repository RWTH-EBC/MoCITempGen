import multiprocessing
import argparse
import os
import sys
import platform
from git import Repo
import time
import glob
from natsort import natsorted
from CITests.CI_Configuration.configuration import CI_configuration

class Git_Repository_Clone(object):

    def __init__(self, repo_dir, git_url, library):
        self.repo_dir = repo_dir
        self.git_url = git_url
        self.library = library

    def _clone_repository(self):  # pull git repo
        if os.path.exists(self.repo_dir):
            print(f'{self.library} folder exists already!')
        else:
            print(f'Clone {self.library} Repo')
            Repo.clone_from(self.git_url, self.repo_dir)


class ValidateTest(CI_configuration):
    """Class to Check Packages and run CheckModel Tests"""

    def __init__(self, single_package, number_of_processors, show_gui, simulate_examples, changedmodel, library, wh_library, filterwhitelist):
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
        super().__init__()
        self.err_log = f'{self.library}{os.sep}{self.library}.{self.single_package}-errorlog.txt'

        # Load modelica python interface
        from dymola.dymola_interface import DymolaInterface
        from dymola.dymola_exception import DymolaException
        print(f'1: Starting Dymola instance')
        if platform.system() == "Windows":
            dymola = DymolaInterface()
        else:
            dymola = DymolaInterface(dymolapath="/usr/local/bin/dymola")
        self.dymola = dymola
        self.dymola_exception = DymolaException()
        self.dymola.ExecuteCommand(
            "Advanced.TranslationInCommandLog:=true;")  # Writes all information in the log file, not only the

    def _dym_check_lic(self):  # check dymola license
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
        print(f'2: Using Dymola port {str(self.dymola._portnumber)} \n {self.green} Dymola License is available {self.CEND}')


    ## Check settings (packages, library, path) #######################################################################
    def _check_packages(self):
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

    def _library_path_check(self, pack_check):
        print(f'Library path: {self.lib_path}')
        if pack_check is True:
            print(f'Found {self.library} Library and start check model test.\nCheck Package {self.package} \n')
        elif pack_check is False:
            print(f'Library path is wrong. Please check the path of {self.library} library path.')
            exit(1)

    def _whitelist_library_check(self):
        if self.wh_library is None:
            print(f'{self.CRED}Error:{self.CEND} Whitelist library is missing!')
            exit(1)
        else:
            print(f'Setting: Whitelist library {self.wh_library}')

    def _check_result(self, error_model):
        if len(error_model) == 0:
            print(f'Test was {self.green}Successful!{self.CEND}')
            exit(0)
        if len(error_model) > 0:
            print(f'Test {self.CRED}failed!{self.CEND}')
            for model in error_model:
                print(f'{self.CRED}Error:{self.CEND} Check Model {model}')
            exit(1)
        if error_model is None:
            print(f'Don´t find models that failed.')
            exit(1)

    ###################################################################################################################
    ## Write logs (error logs)
    def _write_errorlog(self, error_model,
                        error_message):  # Write a Error log with all models, that don´t pass the check
        error_log = open(self.err_log, "w")
        for model, message in zip(error_model, error_message):
            error_log.write(f'\n \n Error in model:  {model} \n')
            error_log.write(str(message))
        error_log.close()

    ## Get Models to check or simulate
    def _get_model(self):  # list all models in package
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
        return model_list

    def _get_changed_models(self):
        print(f'Test only changed or new models')
        changed_model_file = open(self.ch_file, "r", encoding='utf8')
        lines = changed_model_file.readlines()
        modelica_models = []
        for line in lines:
            if line.rfind(".mo") > -1 and line.find("package") == -1:
                if line.find(f'{self.library}{os.sep}{self.single_package}') > -1 and line.find("ReferenceResults") == -1:
                    model_name = line.replace(os.sep, ".")
                    model_name = model_name.replace('/', ".")
                    modelica_models.append(model_name)
                    continue
        if len(modelica_models) == 0:
            print(f'No changed models in Package: {self.single_package}')
            exit(0)
        changed_model_file.close()
        return modelica_models

    def _get_icon_example(self, filepath):
        ex_file = open(filepath, "r", encoding='utf8', errors='ignore')
        lines = ex_file.readlines()
        for line in lines:
            if line.find("extends") > -1 and line.find("Modelica.Icons.Example") > -1:
                example = filepath.replace(os.sep, ".")
                example = example[example.rfind(self.mo_library):example.rfind(".mo")]
                ex_file.close()
                return example

    def _get_simulate_examples(self):  # list all examples in package
        example_list = []
        for subdir, dirs, files in os.walk(self.root_package):
            for file in files:
                filepath = subdir + os.sep + file
                if filepath.endswith(".mo") and file != "package.mo":
                    example = self._get_icon_example(filepath=filepath)
                    example_list.append(example)
        if len(example_list) == 0:
            print(f'No models in package {self.single_package}')
            exit(0)
        return example_list

    def _get_changed_simulate_examples(self):  # list all changed examples in package
        print(f'Test only changed or new models')
        changed_model_file = open(self.ch_file, "r", encoding='utf8',
                              errors='ignore')
        example_list = []
        lines = changed_model_file.readlines()
        for line in lines:
            if line.rfind(".mo") > -1 and line.find("package") == -1:
                if line.find(f'{self.library}{os.sep}{self.single_package}') > -1 and line.find("ReferenceResults") == -1:
                    model = line.lstrip()
                    model = model.strip().replace("\n", "")
                    model_name = model[model.rfind(self.library):]
                    example = self._get_icon_example(filepath=model_name)
                    example_list.append(example)
        changed_model_file.close()
        if len(example_list) == 0:
            print(f'No changed models in Package: {self.single_package}')
            exit(0)
        return example_list

    def _filter_wh_models(self, models, wh_list):
        wh_list_mo = []
        for element in models:
            for subelement in wh_list:
                if element == subelement:
                    wh_list_mo.append(element)
        wh_list_mo = list(set(wh_list_mo))
        for example in wh_list_mo:
            models.remove(example)
        return models

    def _get_wh_models(self):  # Return a List with all models from the Whitelist
        wh_file = open(self.wh_file, "r")
        lines = wh_file.readlines()
        wh_list_models = []
        for line in lines:
            model = line.lstrip()
            model = model.strip()
            model = model.replace("\n", "")
            if model.find(f'{self.wh_library}.{self.single_package}') > -1:
                print(f'Dont test {self.wh_library} model: {model}. Model is on the whitelist')
                wh_list_models.append(model.replace(self.wh_library, self.library))
            elif model.find(f'{self.library}.{self.single_package}') > -1:
                print(f'Dont test {self.library} model: {model}. Model is on the whitelist')
                wh_list_models.append(model)
        wh_file.close()
        return wh_list_models


    def _checkmodel(self, model_list):  # Check models and return a Error Log, if the check failed
        print(f'Check models')
        pack_check = self.dymola.openModel(self.lib_path)
        self._library_path_check(pack_check=pack_check)
        error_model = []
        error_message = []
        for model in model_list:
            result = self.dymola.checkModel(model)
            if result is True:
                print(f'\n {self.green} Successful: {self.CEND} {model} \n')
                continue
            if result is False:
                print(f'Check for Model {model}{self.CRED} failed!{self.CEND}\n\n{self.CRED}Error:{self.CEND} {model}\nSecond Check Test for model {model}')
                sec_result = self.dymola.checkModel(model)
                if sec_result is True:
                    print(f'\n {self.green} Successful: {self.CEND} {model} \n')
                    continue
                if sec_result is False:
                    print(f'\n   {self.CRED}  Error:   {self.CEND}  {model}  \n')
                    log = self.dymola.getLastError()
                    error_model.append(model)
                    error_message.append(log)
                    print(f'{log}')
                    continue
        self.dymola.savelog(self.mo_library + "." + self.package + "-log.txt")
        self.dymola.close()
        return error_model, error_message

    def _simulate_examples(self, example_list):  # Simulate examples or validations
        print(f'Simulate examples and validations')
        pack_check = self.dymola.openModel(self.lib_path)
        self._library_path_check(pack_check=pack_check)
        error_model = []
        error_message = []
        if len(example_list) == 0:
            print(f'{self.CRED}Error:{self.CEND} Found no examples')
            exit(0)
        else:
            for example in example_list:
                print(f'Simulate model: {example}')
                result = self.dymola.checkModel(example, simulate=True)
                if result is True:
                    print(f'\n {self.green}Successful:{self.CEND} {example}\n')
                if result is False:
                    print(f'Simulate model {example} {self.CRED} failed! {self.CEND} \n Second check test for model {example}')
                    sec_result = self.dymola.checkModel(example, simulate=True)
                    if sec_result is True:
                        print(f'\n {self.green} Successful: {self.CEND} {example} \n')
                    if sec_result is False:
                        print(f'\n {self.CRED} Error: {self.CEND} {example}\n')
                        log = self.dymola.getLastError()
                        print(f'{log}')
                        error_model.append(example)
                        error_message.append(log)
        self.dymola.savelog(self.mo_library + "." + self.package + "-log.txt")
        self.dymola.close()
        return error_model, error_message

    def check_model_workflow(self):
        self._check_packages()
        self._dym_check_lic()
        if self.changedmodel is True:  # Test only changed or new models
            model_list = self._get_changed_models()
        elif self.filterwhitelist is True:  # Filter model on whitelist
            self._whitelist_library_check()
            wh_list = self._get_wh_models()
            models = self._get_model()
            model_list = self._filter_wh_models(models=models, wh_list=wh_list)
        else:  # Check all models in package
            model_list = self._get_model()
        result = self._checkmodel(model_list=model_list)
        self._write_errorlog(error_model=result[0], error_message=result[1])
        self._check_result(error_model=result[0])

    def simulate_example_workflow(self):
        self._check_packages()
        self._dym_check_lic()
        if self.changedmodel is True:
            simulate_example_list = self._get_changed_simulate_examples()
        elif self.filterwhitelist is True:
            self._whitelist_library_check()
            wh_list = self._get_wh_models()
            models = self._get_simulate_examples()
            simulate_example_list = self._filter_wh_models(models=models, wh_list=wh_list)
        else:
            simulate_example_list = self._get_simulate_examples()
        result = self._simulate_examples(example_list=simulate_example_list)
        self._write_errorlog(error_model=result[0], error_message=result[1])
        self._check_result(error_model=result[0])

class Create_whitelist(CI_configuration):

    def __init__(self, library, wh_library, repo_dir, git_url):
        self.library = library
        self.wh_library = wh_library
        self.repo_dir = repo_dir
        self.git_url = git_url
        self.wh_lib_path = f'{self.wh_lib}{os.sep}{self.wh_lib}{os.sep}package.mo'
        super().__init__()

        from dymola.dymola_interface import DymolaInterface  # Load modelica python interface
        from dymola.dymola_exception import DymolaException
        print(f'1: Starting Dymola instance')
        if platform.system() == "Windows":
            dymola = DymolaInterface()
        else:
            dymola = DymolaInterface(dymolapath="/usr/local/bin/dymola")
        self.dymola = dymola
        self.dymola_exception = DymolaException()
        self.dymola.ExecuteCommand(
            "Advanced.TranslationInCommandLog:=true;")  # ## Writes all information in the log file, not only the

    def _write_whitelist(self, error_model_list, version):  # write a new whitelist
        wh_file = open(self.wh_model_file, "w")
        wh_file.write(f'\n{version} \n \n')
        for model in error_model_list:
            wh_file.write(f'\n{model} \n \n')
        print(f'Write new writelist for {self.wh_library} library\nNew whitelist was created with the version {version}')
        wh_file.close()

    def _write_exit_log(self, version_check):  # write entry in exit file
        exit = open(self.exit_file, "w")
        if version_check is False:
            exit.write(f'FAIL')
        else:
            exit.write(f'successful')
        exit.close()

    def read_script_version(self):
        dir = f'{self.library}{os.sep}Resources{os.sep}Scripts'
        filelist = (glob.glob(f'{dir}{os.sep}*.mos'))
        if len(filelist) == 0:
            print(f'Cannot find a Conversion Script in {self.wh_library} repository.')
            exit(0)
        else:
            l_aixlib_conv = natsorted(filelist)[(-1)]
            l_aixlib_conv = l_aixlib_conv.split(os.sep)
            version = (l_aixlib_conv[len(l_aixlib_conv) - 1])
            print(f'Latest {self.library} version: {version}')
            return version

    def _check_fileexist(self):
        if os.path.exists(self.wh_file):
            print(f'Whitelist does exist. Update the whitelist under {self.wh_file}')
        else:
            print(f' Whitelist does not exist. Create a new one under {self.wh_file}')
            file = open(self.wh_file, "w+")
            file.close()

    def _check_whitelist(self,
                         version):  # Write a new Whitelist with all models in IBPSA Library of those models who have not passed the Check Test
        vfile = open(self.wh_file, "r")  # Read the last version of whitelist
        lines = vfile.readlines()
        version_check = False
        for line in lines:
            line = line.strip()
            if line.strip("\n") == version.strip("\n"):
                print(f'Whitelist is on version {version}. The whitelist is already up to date')
                version_check = True
        vfile.close()
        return version_check

    def _get_wh_model(self, wh_path):
        model_list = []
        for subdir, dirs, files in os.walk(wh_path):
            for file in files:
                filepath = subdir + os.sep + file
                if filepath.endswith(".mo") and file != "package.mo":
                    model = filepath.replace(os.sep, ".")
                    model = model[model.rfind(self.wh_lib):model.rfind(".mo")]
                    model_list.append(model)
        if len(model_list) == 0:
            print(f'No Models')
            exit(1)
        return model_list

    def _dym_check_lic(self):  # check dymola license
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
        print(f'2: Using Dymola port {str(self.dymola._portnumber)}\n{self.green}Dymola License is available{self.CEND}')


    def _check_whitelist_model(self, model_list):  # check models for creating whitelist
        package_check = self.dymola.openModel(self.wh_lib_path)
        if package_check is True:
            print(f'Found {self.wh_lib} Library and check models in library {self.wh_lib} \n')
        elif package_check is False:
            print(f'Library path is wrong. Please check path of {self.wh_lib} library path.')
            exit(1)
        error_model = []
        error_message = []
        for model in model_list:
            result = self.dymola.checkModel(model)
            if result is True:
                print(f'\n{self.green}Successful:{self.CEND} {model}\n')
                continue
            if result is False:
                print(f'\n{self.CRED}Error:{self.CEND} {model}\n')
                log = self.dymola.getLastError()
                print(f'{log}')
                error_model.append(model)
                error_message.append(log)
                continue
        self.dymola.savelog(f'{self.wh_lib}-log.txt')
        self.dymola.close()
        return error_model, error_message

    def _check_library(self):
        if self.wh_library is None:
            print(f'{self.CRED}Error:{self.CEND} Whitelist library is missing!')
            exit(1)
        if self.library is None:
            print(f'{self.CRED}Error{self.CEND}: Library is missing!')
            exit(1)

    def _check_repo_dir(self):
        if self.repo_dir is None:
            print(f'{self.CRED}Error:{self.CEND} Repository directory is missing!')
            exit(1)
        else:
            print(f'Setting: Repository url: {self.repo_dir}')

    def _check_git_url(self):
        if self.git_url is None and self.wh_path is None:
            print(f'{self.CRED}Error:{self.CEND} git url or whitelist path is missing!')
            exit(1)
        if self.git_url is not None:
            print(f'Setting: whitelist git url library {self.git_url}')

    def create_wh_workflow(self):
        self._check_library()
        self._check_fileexist()
        version = self.read_script_version()
        version_check = self._check_whitelist(version)
        if version_check is False:
            self._write_exit_log(version_check)
            model_list = []
            self._check_repo_dir()
            self._check_git_url()
            if self.git_url is not None:
                Git_Class = Git_Repository_Clone(repo_dir=self.repo_dir,
                                                 git_url=self.git_url,
                                                 library=self.wh_library)
                Git_Class._clone_repository()
                model_list = self._get_wh_model(wh_path=self.repo_dir)
            elif self.wh_path is not None:
                print(f'Setting: whitelist path library {self.wh_path}')
                model_list = self._get_wh_model(wh_path=self.wh_path)
            self._dym_check_lic()
            result = self._check_whitelist_model(model_list=model_list)
            self._write_whitelist(error_model_list=result[0], version=version)
            exit(0)
        else:
            self._write_exit_log(version_check=version_check)
            exit(0)


def _setEnvironmentVariables(var, value):  # Add to the environment variable 'var' the value 'value'
    import os
    import platform
    if var in os.environ:
        if platform.system() == "Windows":
            os.environ[var] = value + ";" + os.environ[var]
        else:
            os.environ[var] = value + ":" + os.environ[var]
    else:
        os.environ[var] = value

def _setEnvironmentPath(dymolaversion):
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
    print(f'operating system {platform.system()}')
    sys.path.append(os.path.join(os.path.abspath('.'), "..", "..", "BuildingsPy"))

if __name__ == '__main__':
    from validatetest import ValidateTest
    parser = argparse.ArgumentParser(description="Check and Validate single Packages")  # Configure the argument parser
    check_test_group = parser.add_argument_group("arguments to run check tests")
    check_test_group.add_argument('-s', "--single-package", metavar="AixLib.Package",
                                  help="Test only the Modelica package AixLib.Package")
    check_test_group.add_argument("-n", "--number-of-processors", type=int, default=multiprocessing.cpu_count(),
                                  help="Maximum number of processors to be used")
    check_test_group.add_argument("--show-gui", help="show the GUI of the simulator", action="store_true")
    check_test_group.add_argument("-WL", "--whitelist",
                                  help="Create a WhiteList of IBPSA Library: y: Create WhiteList, n: Don´t create WhiteList",
                                  action="store_true")
    check_test_group.add_argument("-SE", "--simulate-examples", help="Check and Simulate Examples in the Package",
                                  action="store_true")
    check_test_group.add_argument("-DS", "--dymolaversion", default="2020",
                                  help="Version of Dymola(Give the number e.g. 2020")
    check_test_group.add_argument("-V", "--check-version", default=False, action="store_true")
    check_test_group.add_argument("-CM", "--changedmodel", default=False, action="store_true")
    check_test_group.add_argument("-FW", "--filterwhitelist", default=False, action="store_true")
    check_test_group.add_argument("-l", "--library", default="AixLib", help="Library to test")
    check_test_group.add_argument("-wh-l", "--wh-library", help="Library to test")
    check_test_group.add_argument("--repo-dir", help="Library to test")
    check_test_group.add_argument("--git-url", default="https://github.com/ibpsa/modelica-ibpsa.git", help="url repository")
    check_test_group.add_argument("--wh-path", help="path of white library")
    args = parser.parse_args()  # Parse the arguments
    _setEnvironmentPath(dymolaversion=args.dymolaversion)


    if args.whitelist is True:  # Write a new WhiteList
        wh = Create_whitelist(library=args.library,
                              wh_library=args.wh_library,
                              repo_dir=args.repo_dir,
                              git_url=args.git_url)
        wh.create_wh_workflow()
    else:
        CheckModelTest = ValidateTest(single_package=args.single_package,
                                  number_of_processors=args.number_of_processors,
                                  show_gui=args.show_gui,
                                  simulate_examples=args.simulate_examples,
                                  changedmodel=args.changedmodel,
                                  library=args.library,
                                  wh_library=args.wh_library,
                                  filterwhitelist=args.filterwhitelist)
        if args.simulateexamples is True:  # Simulate Models
            CheckModelTest.simulate_example_workflow()
        else:  # Check all Models in a Package
            CheckModelTest.check_model_workflow()
