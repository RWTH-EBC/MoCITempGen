import argparse
import codecs
import os
import platform
import sys
import time

sys.path.append('Dymola_python_tests/CITests/CI_Configuration')
from configuration import CI_conf_class


class StyleCheck(CI_conf_class):

    def __init__(self, dymola, dymola_exception, package, library, dymola_version, changed_models):
        """
        Class to Check the style of packages and models.
        Export HTML-Log File.
        Args:
            dymola (): dymola_python interface class
            dymola_exception (): dymola_exception class
            package (): package to test
            library (): library to test
            dymola_version (): dymola version (e.g. 2022)
            changed_models (): boolean - True: Check only changed models, False: Check library
        """
        self.package = package
        self.library = library
        self.dymola_version = dymola_version
        self.changed_models = changed_models
        super().__init__()
        self.dymola = dymola
        self.dymola_exception = dymola_exception
        self.dymola.ExecuteCommand("Advanced.TranslationInCommandLog:=true;")

    def dym_check_lic(self):
        """
        Check the dymola license.
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
            f'2: Using Dymola port {str(self.dymola._portnumber)} \n {self.green} Dymola License is available {self.CEND}')

    def _check_library(self):
        """
        Load AixLib and check library
        """
        library_check = self.dymola.openModel(self.library)
        if library_check:
            print(f'Found {self.library} library and start style check')
        elif not library_check:
            print(f'Path of library {self.library} is wrong. Please Check Path.')
            exit(1)

    def _set_library_model_management(self):
        """
        Load ModelManagement
        """
        if platform.system() == "Windows":
            self.dymola.ExecuteCommand(
                'cd("C:\Program Files\Dymola ' + self.dymola_version + '\Modelica\Library\ModelManagement 1.1.8\package.moe");')
        else:
            self.dymola.ExecuteCommand(
                'cd("/opt/dymola-' + self.dymola_version + '-x86_64/Modelica/Library/ModelManagement 1.1.8/package.moe");')

    def style_check(self, models_list):
        """
        Start CheckLibrary in ModelManagement
        Returns:
        """
        print(f'Start Style Check. Check package or model: {models_list}')
        self._check_library()
        self._set_library_model_management()
        if len(models_list) == 1 or len(models_list) > 100:
            self.dymola.ExecuteCommand('ModelManagement.Check.checkLibrary(false, false, false, true, "' + self.package + '", translationStructure=false);')
            log_file = self.library.replace("package.mo", self.package + "_StyleCheckLog.html")
        else:
            changed_model_list = []
            path = self.library.replace("package.mo", "")
            for model in models_list:
                print(f'Check package or model {model}')
                self.dymola.ExecuteCommand('ModelManagement.Check.checkLibrary(false, false, false, true, "' + model + '", translationStructure=false);')
                log = codecs.open(f'{path}{model}_StyleCheckLog.html', "r", encoding='utf8')
                for line in log:
                    changed_model_list.append(line)
                log.close()
                os.remove(f'{path}{model}_StyleCheckLog.html')
            all_logs = codecs.open(f'{path}ChangedModels_StyleCheckLog.html', "w", encoding='utf8')
            for model in changed_model_list:
                all_logs.write(model)
            all_logs.close()
            log_file = f'{path}ChangedModels_StyleCheckLog.html'

        self.dymola.close()
        return log_file


    def changed_style_check(self, models_list):
        """
        Args:
            models_list ():

        Returns:

        """
        self._check_library()
        self._set_library_modelmanagement()
        if len(models_list) > 100:
            print(
                f'Over 100 changed models. Check all models in AixLib Library\n Check {self.library} Library: {self.package}')
            self.dymola.ExecuteCommand(
                'ModelManagement.Check.checkLibrary(false, false, false, true, "' + self.package + '", translationStructure=false);')
            log_file = self.library.replace("package.mo", self.package + "_StyleCheckLog.html")
        else:
            changed_model_list = []
            path = self.library.replace("package.mo", "")
            for model in models_list:
                print(f'Check package or model {model}')
                self.dymola.ExecuteCommand(
                    'ModelManagement.Check.checkLibrary(false, false, false, true, "' + model + '", translationStructure=false);')
                log = codecs.open(f'{path}{model}_StyleCheckLog.html', "r", encoding='utf8')
                for line in log:
                    changed_model_list.append(line)
                log.close()
                os.remove(f'{path}{model}_StyleCheckLog.html')
            all_logs = codecs.open(f'{path}ChangedModels_StyleCheckLog.html', "w", encoding='utf8')
            for model in changed_model_list:
                all_logs.write(model)
            all_logs.close()
            log_file = f'{path}ChangedModels_StyleCheckLog.html'
        self.dymola.close()
        return log_file

    def sort_mo_models(self):
        """
        Returns:
        """
        try:
            models_list = []
            changed_file = codecs.open(self.config_ci_changed_file, "r", encoding='utf8')
            lines = changed_file.readlines()
            for line in lines:
                if line.rfind(".mo") > -1:
                    model = line[line.rfind(self.package):line.rfind(".mo")].replace(os.sep, ".").lstrip()
                    models_list.append(model)
                    continue
            changed_file.close()
            if len(models_list) == 0:
                print("No Models to check")
                exit(0)
            else:
                return models_list
        except IOError:
            print(f'Error: File {self.config_ci_changed_file} does not exist.')
            exit(0)

    def Style_Check_Log(self, inputfile):
        """
        Args:
            inputfile ():
        """
        outputfile = inputfile.replace("_StyleCheckLog.html", "_StyleErrorLog.html")
        log_file = codecs.open(inputfile, "r", encoding='utf8')
        error_log = codecs.open(outputfile, "w", encoding='utf8')
        error_count = 0
        for line in log_file:
            line = line.strip()
            if line.find("Check ok") > -1 or line.find("Library style check log") > -1 or len(line) == 0:
                continue
            if self.changed_models is False:
                if line.find(f'HTML style check log for {self.package}') > -1:
                    continue
            else:
                print(f'{self.CRED}Error in model:\n{self.CEND}{line.lstrip()}')
                error_count = error_count + 1
                error_log.write(line)
        log_file.close()
        error_log.close()
        if error_count == 0:
            print(f'{self.green}Style check of model or package {self.package} was successful{self.CEND}')
            exit(0)
        elif error_count > 0:
            print(f'{self.CRED}Test failed. Look in {self.package}_StyleErrorLog.html{self.CEND}')
            exit(1)


def _setEnvironmentVariables(var, value):
    """
    Add to the environment variable 'var' the value 'value'
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
        dymola_version ():
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
    print(f'operating system {platform.system()}')
    sys.path.append(os.path.join(os.path.abspath('.'), "..", "..", "BuildingsPy"))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Check the Style of Packages")
    check_test_group = parser.add_argument_group("arguments to run check tests")
    check_test_group.add_argument('-s', "--single-package", metavar="AixLib.Package",
                                  help="Test only the Modelica package AixLib.Package")
    check_test_group.add_argument("-p", "--path", default=".",
                                  help="Path where top-level package.mo of the library is located")
    check_test_group.add_argument("-DS", "--dymola-version", default="2020",
                                  help="Version of Dymola(Give the number e.g. 2020")
    check_test_group.add_argument("-CM", "--changed_models", default=False, action="store_true")
    args = parser.parse_args()
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
    CheckStyle = StyleCheck(dymola=dymola,
                            dymola_exception=dymola_exception,
                            package=args.single_package,
                            library=args.path,
                            dymola_version=args.dymola_version,
                            changed_models=args.changed_models)
    CheckStyle.dym_check_lic()
    model_list = []
    if args.changed_models is False:
        model_list = [args.single_package]
    if args.changed_models is True:
        model_list = CheckStyle.sort_mo_models()
    logfile = CheckStyle.style_check(models_list=model_list)
    CheckStyle.Style_Check_Log(inputfile=logfile)
