import argparse
import multiprocessing
import os
import platform
import sys
import time
import buildingspy.development.validator as validate
import buildingspy.development.regressiontest as regression

sys.path.append('../Dymola_python_tests/CITests/CI_Configuration')
from configuration import CI_conf_class


class Buildingspy_Regression_Check(CI_conf_class):

    def __init__(self, buildingspy_regression, package, n_pro, tool, batch, show_gui, path):
        """
        Args:
            buildingspy_regression (): library buildingspy: use for regression tests
            package (): package to be checked
            n_pro (): number of processors
            tool (): dymola or Openmodelica
            batch (): boolean: - False: interactive with script (e.g. generate new regressiontests) - True: No interactive with script
            show_gui (): show_gui (): True - show dymola, false - dymola hidden.
            path (): Path where top-level package.mo of the library is located
        """
        self.package = package
        self.n_pro = n_pro
        self.tool = tool
        self.batch = batch
        self.show_gui = show_gui
        self.path = path
        super().__init__()
        self.wh_ref_file = f'..{os.sep}{self.wh_ref_file}'
        self.config_ci_exit_file = f'..{os.sep}{self.config_ci_exit_file}'
        self.config_ci_ref_file = f'..{os.sep}{self.config_ci_ref_file}'
        self.ut = buildingspy_regression.Tester(tool=self.tool)

    def _write_exit_file(self, err_list):
        """

        """
        try:
            ex_file = open(self.config_ci_exit_file, "w")
            if len(err_list) == 0:
                ex_file.write(f'successful')
            else:
                ex_file.write(f'FAIL')
            ex_file.close()
            print(f'{self.green}All Reference files exists, except the Models on WhiteList.{self.CEND}')
            exit(0)
        except IOError:
            print(f'Error: File {self.config_ci_exit_file} does not exist.')
            exit(0)

    def check_regression_test(self, package_list):
        """
        start regression test for a package
        Args:
            package_list ():
        Returns:
        """
        print(f'Test following packages: {package_list}')
        if package_list is None or len(package_list) == 0:
            print(f'{self.CRED}Error:{self.CEND} Package is missing! (e.g. Airflow)')
            exit(1)
        self.ut.batchMode(self.batch)
        self.ut.setLibraryRoot(self.path)
        self.ut.setNumberOfThreads(self.n_pro)
        self.ut.pedanticModelica(False)
        self.ut.showGUI(self.show_gui)
        err_list = []
        if package_list is not None:
            if len(package_list) > 0:
                for package in package_list:
                    if self.batch is False:
                        print(f'{self.green}Generate new reference results for package: {self.CEND} {package}')
                    else:
                        print(f'{self.green}Regression test for package:{self.CEND} {package}')
                    self.ut.setSinglePackage(package)
                    response = self.ut.run()
                    if response != 0:
                        err_list.append(package)
                        if self.batch is False:
                            print(f'{self.CRED}Error in package: {self.CEND} {package}')
                            continue
                        else:
                            print(f'{self.CRED}Regression test for model {package} was not successfully{self.CEND}')
                            continue
                    else:
                        if self.batch is False:
                            print(f'{self.green}New reference results in package: {self.CEND} {package}\n')
                            continue
                        else:
                            print(f'{self.green} Regression test for model {package} was successful {self.CEND}')
                            continue
            else:
                self._write_exit_file(err_list=err_list)
        if len(err_list) > 0:
            print(f'{self.CRED}Regression test failed{self.CEND}')
            print(f'The following packages{self.CRED} failed: {self.CEND}')
            for error in err_list:
                print(f'{self.CRED}Error:{self.CEND} {error}')
            return 1
        else:
            print(f'{self.green}Regression test was successful {self.CEND}')
            return 0


class Ref_model(CI_conf_class):

    def __init__(self, library):
        """

        """
        super().__init__()
        self.library = library

    def _compare_wh_mos(self, package_list, wh_list):
        """
        Filter model from whitelist.
        Args:
            package_list ():
            wh_list ():
        Returns:
        """
        err_list = []
        for package in package_list:
            for wh_package in wh_list:
                if package[:package.rfind(".")].find(wh_package) > -1:
                    print(
                        f'{self.green}Don´t Create reference results for model{self.CEND} {package} This package is '
                        f'on the whitelist')
                    err_list.append(package)
                else:
                    continue
        for err in err_list:
            package_list.remove(err)
        return package_list

    def get_update_model(self):
        mos_script_list = self._get_mos_scripts()  # Mos Scripts
        reference_list = self._get_check_ref()  # Reference files
        mos_list = self._compare_ref_mos(mos_script_list=mos_script_list, reference_list=reference_list)
        wh_list = self._get_whitelist_package()
        model_list = self._compare_wh_mos(package_list=mos_list, wh_list=wh_list)
        model_list = list(set(model_list))
        package_list = []
        for model in model_list:
            print(f'{self.green}Generate new reference results for model: {self.CEND} {model}')
            package_list.append(model[:model.rfind(".")])
        package_list = list(set(package_list))
        return package_list

    @staticmethod
    def get_update_package(ref_list):
        """
        Args:
            ref_list ():
        Returns:
        """
        ref_package_list = []
        for ref in ref_list:
            if ref.rfind("Validation") > -1:
                ref_package_list.append(ref[:ref.rfind("_Validation") + 11].replace("_", "."))
            elif ref.rfind("Examples") > -1:
                ref_package_list.append(ref[:ref.rfind("_Examples") + 9].replace("_", "."))
        ref_package_list = list(set(ref_package_list))
        return ref_package_list

    def _get_whitelist_package(self):
        """
         get and filter package from reference whitelist
        Returns:

        """
        try:
            ref_wh = open(self.wh_ref_file, "r")
            lines = ref_wh.readlines()
            wh_list = []
            for line in lines:
                if len(line.strip()) == 0:
                    continue
                else:
                    wh_list.append(line.strip())
            ref_wh.close()
            for wh_package in wh_list:
                print(
                    f'{self.CRED} Don´t create reference results for package{self.CEND} {wh_package}: This Package is '
                    f'on the whitelist')
            return wh_list
        except IOError:
            print(f'Error: File {self.wh_ref_file} does not exist.')
            exit(0)

    def _compare_ref_mos(self, mos_script_list, reference_list):
        """
        compares if both files exists:  mos_script == reference results
        remove all mos script for that a ref file exists
        Args:
            mos_script_list ():
            reference_list ():

        Returns:

        """
        err_list = []
        for mos in mos_script_list:
            for ref in reference_list:
                if mos.replace(".", "_") == ref:
                    err_list.append(mos)
                    break
        for err in err_list:
            mos_script_list.remove(err)  #
        for package in mos_script_list:
            print(f'{self.CRED}No Reference result for Model:{self.CRED} {package}')
        return mos_script_list

    def _get_check_ref(self):
        """
        Give a reference list.
        Returns:
            ref_list(): return a list of reference_result files
        """
        ref_list = []
        for subdir, dirs, files in os.walk(self.library_ref_results_dir):
            for file in files:
                filepath = subdir + os.sep + file
                if filepath.endswith(".txt"):
                    ref_file = filepath[filepath.rfind(self.library):filepath.find(".txt")]
                    ref_list.append(ref_file)
        if len(ref_list) == 0:
            print(
                f'No reference files in file {self.library_ref_results_dir}. Please add here your reference files you want to '
                f'update')
            exit(0)
        else:
            return ref_list

    def get_update_ref(self):
        """
        get a model to update
        Returns:
        """
        try:
            file = open(f'..{os.sep}{self.ci_interact_update_ref_file}', "r")
            lines = file.readlines()
            update_ref_list = []
            for line in lines:
                if len(line) == 0:
                    continue
                elif line.find(".txt") > -1:
                    update_ref_list.append(line.strip())
            file.close()
            if len(update_ref_list) == 0:
                print(
                    f'No reference files in file {self.ci_interact_update_ref_file}. Please add here your reference files you '
                    f'want to update')
                exit(0)
            return update_ref_list
        except IOError:
            print(f'Error: File ..{os.sep}{self.ci_interact_update_ref_file} does not exist.')
            exit(0)

    def write_regression_list(self):
        """
        Writes a list for feasible regression tests.
        """
        mos_list = self._get_mos_scripts()
        try:
            wh_file = open(self.config_ci_ref_file, "w")
            for mos in mos_list:
                wh_file.write(f'\n{mos}\n')
            wh_file.close()
            exit(0)
        except IOError:
            print(f'Error: File {self.config_ci_ref_file} does not exist.')
            exit(0)

    def _get_mos_scripts(self):
        """
        Obtain mos scripts that are feasible for regression testing
        Returns:
            mos_list (): return a list with .mos script that are feasible for regression testing
        """
        mos_list = []
        for subdir, dirs, files in os.walk(self.library_ref_results_dir):
            for file in files:
                filepath = subdir + os.sep + file
                if filepath.endswith(".mos"):
                    infile = open(filepath, "r")
                    lines = infile.read()
                    if lines.find("simulateModel") > -1:
                        mos_script = filepath[filepath.find("Dymola"):filepath.find(".mos")].replace("Dymola",
                                                                                                     self.library)
                        mos_script = mos_script.replace(os.sep, ".")
                        mos_list.append(mos_script)
                    if lines.find("simulateModel") == -1:
                        print(
                            f'{self.CRED}This mos script is not suitable for regression testing:{self.CEND} {filepath}')
                    infile.close()
                    continue
        if len(mos_list) == 0:
            print(f'No feasible mos script for regression test in {self.library_ref_results_dir}.')
            exit(0)
        else:
            return mos_list


class python_dymola_interface(CI_conf_class):

    def __init__(self, dymola, dymola_exception):
        super().__init__()
        self.dymola = dymola
        self.dymola_exception = dymola_exception
        self.dymola.ExecuteCommand("Advanced.TranslationInCommandLog:=true;")

    def library_check(self, library):
        """
        """

        library_check = self.dymola.openModel("package.mo")
        if library_check is True:
            print(f'Found {library}{os.sep}package.mo Library. Start regression test.')
        elif library_check is False:
            print(f'Library Path "{library}{os.sep}package.mo" is wrong. Please Check Path of {library} Library Path')
            exit(1)

    def dym_check_lic(self):
        """
        check dymola license.
        """
        dym_sta_lic_available = self.dymola.ExecuteCommand('RequestOption("Standard");')
        lic_counter = 0
        while dym_sta_lic_available is False:
            print(f'{self.CRED} No Dymola License is available {self.CEND} \n Check Dymola license after 180.0 seconds')
            self.dymola.close()
            time.sleep(180.0)
            dym_sta_lic_available = self.dymola.ExecuteCommand('RequestOption("Standard");')
            lic_counter += 1
            if lic_counter > 30:
                if dym_sta_lic_available is False:
                    print(f'There are currently no available Dymola licenses available. Please try again later.')
                    self.dymola.close()
                    exit(1)
        print(
            f'2: Using Dymola port   {str(self.dymola._portnumber)} \n {self.green} Dymola License is available {self.CEND}')


class Extended_model(CI_conf_class):

    def __init__(self, dymola, dymola_exception, package, library, dymola_version, path):
        """

        Args:
            dymola ():
            dymola_exception ():
            package ():
            library ():
            dymola_version ():
            path ():
        """
        self.package = package
        self.library = library
        self.dymola_version = dymola_version
        self.path = path
        super().__init__()
        self.resource_dir = f'{self.resource_dir}{os.sep}{self.package.replace(self.library + ".", "")}'

        self.dymola = dymola
        self.dymola_exception = dymola_exception
        self.dymola.ExecuteCommand("Advanced.TranslationInCommandLog:=true;")

    def _get_usedmodel(self, mo_list, lines):
        """
        get a list with all used models of regression models
        gives a list of regression models where submodels have been modified
        Args:
            mo_list ():
        Returns:
        """
        model_list = []
        type_list = ["Modelica", "Real", "Integer", "Boolean", "String"]
        if len(mo_list) > 0:
            if platform.system() == "Windows":  # Load ModelManagement
                self.dymola.ExecuteCommand('cd("C:\Program Files\Dymola ' + self.dymola_version + '\Modelica\Library\ModelManagement 1.1.8\package.moe");')
            else:
                self.dymola.ExecuteCommand('cd("/opt/dymola-' + self.dymola_version + '-x86_64/Modelica/Library/ModelManagement 1.1.8/package.moe");')
            for model in mo_list:
                use_model_list = []
                used_model_list = self.dymola.ExecuteCommand(f'ModelManagement.Structure.Instantiated.UsedModels("{model}");')
                if used_model_list is None:
                    continue
                else:
                    for use_model in used_model_list:
                        for types in type_list:
                            if use_model.find(f'{types}') > -1:
                                continue
                        use_model_list.append(use_model)

                extended_model_list = self.dymola.ExecuteCommand(f'ModelManagement.Structure.AST.ExtendsInClass("{model}");')
                if extended_model_list is None:
                    continue
                else:
                    for extended_model in extended_model_list:
                        for types in type_list:
                            if extended_model.find(f'{types}') > -1:
                                continue
                        use_model_list.append(extended_model)
                ch_model_list = self._get_changed_used_model(lines=lines, model_list=use_model_list)
                if len(ch_model_list) > 0:
                    model_list.append(model)
            self.dymola.close()
            model_list = list(set(model_list))
            return model_list

    def _get_changed_used_model(self, lines, model_list):
        """
        return all used models, that changed
        Args:
            lines ():
            model_list ():

        Returns:
        """
        ch_model_list = []
        for line in lines:
            for model in model_list:
                if line[line.find(self.library):line.rfind(".mo")].strip() == model:
                    ch_model_list.append(model)
        return ch_model_list

    @staticmethod
    def _insert_list(ref_list, mos_list, modelica_list,
                     ch_model_list):
        """
        return models, scripts, reference results and used models, that changed
        Args:
            ref_list ():
            mos_list ():
            modelica_list ():
            ch_model_list ():
        Returns:
        """
        changed_list = []
        if ref_list is not None:
            for ref in ref_list:
                print(f'Changed reference files: {ref}')
                changed_list.append(ref[:ref.rfind("_")].replace("_", "."))
        if mos_list is not None:
            for mos in mos_list:
                print(f'Changed mos script files: {mos}')
                changed_list.append(mos[:mos.rfind(".")])
        if modelica_list is not None:
            for model in modelica_list:
                print(f'Changed model files: {model}')
                changed_list.append(model[:model.rfind(".")])
        if ch_model_list is not None:
            for usedmodel in ch_model_list:
                print(f'Changed used model files: {usedmodel}')
                changed_list.append(usedmodel[:usedmodel.rfind(".")])
        changed_list = list(set(changed_list))
        return changed_list

    def get_changed_regression_models(self):
        """
        Returns:
        """
        try:
            changed_models = open(self.config_ci_changed_file, "r", encoding='utf8')
            ref_file = open(self.config_ci_ref_file, "r", encoding='utf8')
            changed_lines = changed_models.readlines()
            ref_lines = ref_file.readlines()
            changed_models.close()
            ref_file.close()
            mos_list = []
            modelica_list = []
            for line in changed_lines:
                if len(line) == 0:
                    continue
                else:
                    line = line.replace("/", ".")
                    line = line.replace(os.sep, ".")
                    if line.rfind(".mos") > -1 and line.rfind("Scripts") > -1 and line.find(
                            ".package") == -1 and line.rfind(self.package) > -1:
                        line = line.replace("Dymola", self.library)
                        mos_list.append(line[line.rfind(self.library):line.rfind(".mos")])
                    if line.rfind(".mo") > -1 and line.find("package.") == -1 and line.rfind(
                            self.package) > -1 and line.rfind("Scripts") == -1:
                        modelica_list.append(line[line.rfind(self.library):line.rfind(".mo")])
            mo_list = []
            for line in ref_lines:
                if line.find(self.package) > -1:
                    mo_list.append(line.strip())
            ref_list = []
            for model in modelica_list:
                for mo in mo_list:
                    if model == mo:
                        ref_list.append(model)
            ch_model_list = self._get_usedmodel(mo_list=mo_list, lines=changed_lines)
            changed_list = self._insert_list(ref_list=ref_list, mos_list=mos_list, modelica_list=modelica_list,
                                             ch_model_list=ch_model_list)
            if len(changed_list) == 0:
                print(f'No models to check and cannot start a regression test')
                exit(0)
            else:
                print(f'Number of checked packages: {str(len(changed_list))}')
                return changed_list
        except IOError:
            print(f'Error: File {self.config_ci_changed_file} does not exist.')
            exit(1)

    def delte_ref_file(self, ref_list):
        """
        Delete reference files.
        Args:
            ref_list (): list of reference_result files
        """
        ref_dir = f'{self.library}{os.sep}{self.library_ref_results_dir}'
        for ref in ref_list:
            print(f'Update reference file: {ref_dir}{os.sep}{ref}\n')
            if os.path.exists(f'..{os.sep}{ref_dir}{os.sep}{ref}') is True:
                os.remove(f'..{os.sep}{ref_dir}{os.sep}{ref}')
            else:
                print(f'File {ref_dir}{os.sep}{ref} does not exist\n')


class Buildingspy_Validate_test(CI_conf_class):

    def __init__(self, validate, path):
        """

        Args:
            validate ():
            path ():
        """
        self.path = path
        self.validate = validate
        super().__init__()

    def validate_html(self):
        """
        validate the html syntax only
        """
        vald = self.validate.Validator()
        err_msg = vald.validateHTMLInPackage(self.path)
        n_msg = len(err_msg)
        for i in range(n_msg):
            if i == 0:
                print("The following malformed html syntax has been found:\n%s" % err_msg[i])
            else:
                print(err_msg[i])
        if n_msg == 0:
            exit(0)
        else:
            print(f'{self.CRED}html check failed.{self.CEND}')
            exit(1)

    def validate_experiment_setup(self):
        """
        validate regression test setup
        """
        vald = self.validate.Validator()
        ret_val = vald.validateExperimentSetup(self.path)
        exit(ret_val)

    def run_coverage_only(self, buildingspy_regression, batch, tool, package):
        """
        Specifies which models are tested
        Args:
            buildingspy_regression (): library buildingspy: use for regression tests
            batch (): boolean: - False: interactive with script (e.g. generate new regressiontests) - True: No interactive with script
            tool (): dymola or Openmodelica
            package (): package to be checked
        """
        ut = buildingspy_regression.Tester(tool=tool)
        ut.batchMode(batch)
        ut.setLibraryRoot(self.path)
        if package is not None:
            ut.setSinglePackage(package)
        ut.get_test_example_coverage()
        exit(0)


def _setEnvironmentVariables(var, value):  # Add to the environment variable `var` the value `value`
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
    Checks the Operating System, Important for the Python-Dymola Interface
    Args:
        dymola_version ():
    """
    if platform.system() == "Windows":
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
    parser = argparse.ArgumentParser(description='Run the unit tests or the html validation only.')
    unit_test_group = parser.add_argument_group("arguments to run unit tests")
    unit_test_group.add_argument("-b", "--batch",
                                 action="store_true",
                                 help="Run in batch mode without user interaction")
    unit_test_group.add_argument("--show-gui",
                                 help='Show the GUI of the simulator',
                                 action="store_true")
    unit_test_group.add_argument('-s', "--single-package",
                                 metavar="Modelica.Package",
                                 help="Test only the Modelica package Modelica.Package")
    unit_test_group.add_argument("-p", "--path",
                                 default=".",
                                 help="Path where top-level package.mo of the library is located")
    unit_test_group.add_argument("-L", "--library", default="AixLib", help="Library to test")
    unit_test_group.add_argument("-n", "--number-of-processors", type=int, default=multiprocessing.cpu_count(),
                                 help='Maximum number of processors to be used')
    unit_test_group.add_argument('-t', "--tool", metavar="dymola", default="dymola",
                                 help="Tool for the regression tests. Set to dymola or jmodelica")
    unit_test_group.add_argument("-DS", "--dymola-version", default="2020",
                                 help="Version of Dymola(Give the number e.g. 2020")
    unit_test_group.add_argument("--coverage-only",
                                 help='Only run the coverage test',
                                 action="store_true")
    unit_test_group.add_argument("--create-ref",
                                 help='checks if all reference files exist',
                                 action="store_true")
    unit_test_group.add_argument("--ref-list",
                                 help='checks if all reference files exist',
                                 action="store_true")
    unit_test_group.add_argument("--update-ref",
                                 help='update all reference files',
                                 action="store_true")
    unit_test_group.add_argument("--modified-models",
                                 help='Regression test only for modified models',
                                 default=False,
                                 action="store_true")
    unit_test_group.add_argument("--validate-html-only", action="store_true")
    unit_test_group.add_argument("--validate-experiment-setup", action="store_true")
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

    if args.validate_html_only:
        Buildingspy_Validate_test(validate=validate, path=args.path).validate_html()
    elif args.validate_experiment_setup:  # Match the mos file parameters with the mo files only, and then exit
        Buildingspy_Validate_test(validate=validate, path=args.path).validate_experiment_setup()
    elif args.coverage_only:
        Buildingspy_Validate_test(validate=validate, path=args.path).run_coverage_only(
            buildingspy_regression=regression,
            batch=args.batch,
            tool=args.tool,
            package=args.single_package)
    else:
        dym_interface = python_dymola_interface(dymola=dymola, dymola_exception=dymola_exception)
        dym_interface.library_check(library=args.library)
        dym_interface.dym_check_lic()
        ref_check = Buildingspy_Regression_Check(buildingspy_regression=regression,
                                                 package=args.single_package,
                                                 n_pro=args.number_of_processors,
                                                 tool=args.tool,
                                                 batch=args.batch,
                                                 show_gui=args.show_gui,
                                                 path=args.path)

        conf = CI_conf_class()
        ref_model = Ref_model(library=args.library)
        if args.ref_list:
            ref_model.write_regression_list()
        elif args.create_ref:  # cd AixLib && python ../bin/02_CITests/UnitTests/reference_check.py --create-ref
            package_list = ref_model.get_update_model()
            val = ref_check.check_regression_test(package_list=package_list)
            exit(val)
        elif args.update_ref:  # cd AixLib && python ../bin/02_CITests/UnitTests/reference_check.py --update-ref --single-package
            ref_list = ref_model.get_update_ref()
            ref_model.delte_ref_file(ref_list=ref_list)
            package_list = ref_model.get_update_package(ref_list=ref_list)
            val = ref_check.check_regression_test(package_list=package_list)
            exit(val)
        else:
            if args.modified_models is False:
                val = ref_check.check_regression_test(package_list=[args.single_package])
                exit(val)
            '''
            elif args.modified_models is True:
                conf.check_ci_folder_structure(folder_list=[conf.config_ci_dir])
                conf.check_ci_file_structure(file_list=[conf.config_ci_changed_file])
                ref_model.write_regression_list()
                package = args.single_package[args.single_package.rfind(".") + 1:]
                list_reg_model = Extended_model(dymola=dymola,
                                                dymola_exception=dymola_exception,
                                                package=package,
                                                library=args.library,
                                                dymola_version=args.dymola_version,
                                                path="package.mo")
                package_list = list_reg_model.get_changed_regression_models()
                val = ref_check.check_regression_test(package_list=package_list)
                exit(val)
    '''
