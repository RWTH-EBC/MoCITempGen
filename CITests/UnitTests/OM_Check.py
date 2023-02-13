import os
import sys
from ebcpy import DymolaAPI, TimeSeriesData
from ebcpy.utils.statistics_analyzer import StatisticsAnalyzer
from OMPython import OMCSessionZMQ
from Dymola_python_tests.CI_test_config import CI_config
from Dymola_python_tests.CITests.structure.sort_mo_model import modelica_model

import shutil
import pathlib
import time
import platform
import numpy as np
import matplotlib.pyplot as plt
import argparse


class Check_OpenModelica(CI_config):

    def __init__(self,
                 package: str = "Airflow",
                 library: str = "AixLib",
                 om_options: str = "OM_CHECK",
                 simulate_flag: bool = False,
                 changed_flag: bool = False,
                 wh_library: str = "IBPSA",
                 filter_wh_flag: bool = False,
                 lib_dir_dict=None):
        """
        Args:

        """
        super().__init__()
        if lib_dir_dict is None:
            lib_dir_dict = {}
        self.package = package
        self.library = library
        self.wh_library = wh_library

        self.om_options = om_options
        self.simulate_flag = simulate_flag
        self.changed_flag = changed_flag
        self.filter_wh_flag = filter_wh_flag

        self.omc = OMCSessionZMQ()
        print(f'{self.green}OpenModelica Version number:{self.CEND} {self.omc.sendExpression("getVersion()")}')
        #load_modelica = self.omc.sendExpression("loadModel(Modelica)")
        load_modelica = self.omc.sendExpression(f'installPackage(Modelica, "4.0.0+maint.om", exactMatch=true)')
        if load_modelica is True:
            print(f'{self.green}Load library modelica in Openmodelica.{self.CEND}')
        else:
            print(f'Load of modelica has failed.')
            exit(1)
        self.check_log = os.path.join(os.path.abspath("."), library, f'{self.library}.{self.package}-check_log.txt')
        self.err_log = os.path.join(os.path.abspath("."), library, f'{self.library}.{self.package}-error_log.txt')
        self.all_sims_dir = os.path.join(os.path.abspath("."), self.result_OM_check_result_dir, self.library, self.package)
        self.temp_result_folder = os.path.join(os.path.abspath("."), "_temp_results")
        """
        self.lib_path = f'..{os.sep}{self.library}{os.sep}package.mo'
        self.omc = None
        self.dym_api = None
        self.for_bes_mod = self.library == "BESMod"
        self.lib_dir_dict = lib_dir_dict"""


    def check_OM_workflow(self,
                          model_list: list):
        self.check_ci_structure(folders_list="_temp_results")
        os.chdir("_temp_results")

        self.omc = self._load_library()
        ERROR_DATA = {}
        STATS = None
        if self.om_options == "OM_SIM":
            result = self.simulate_examples(example_list=model_list)
            self.write_errorlog(error_model=result[0],
                                error_message=result[1])
        elif self.om_options == "DYMOLA_SIM":
            self.sim_with_dymola(simulate_example_list=model_list)
        elif self.om_options == "OM_CHECK":  # Check all Models in a Package
            result = self._checkmodel(model_list=model_list)
            self.write_errorlog(error_model=result[0],
                                error_message=result[1])
        elif self.om_options == "COMPARE":
            ERROR_DATA, STATS = self.compare_dym_to_om(simulate_example_list=model_list,
                                                       stats=STATS)
        else:
            raise ValueError(f"{self.om_options} not supported")

        self.prepare_data(del_flag=True,
                          path_list=[f'{self.result_check_result_dir}{os.sep}{self.package}'],
                          file_path_dict={self.check_log: f'{self.result_check_result_dir}{os.sep}{self.package}'})

        with open(self.all_sims_dir.parent.joinpath("error_data.json"), "w+") as f:
            import json
            json.dump(ERROR_DATA, f, indent=2)
        with open(self.all_sims_dir.parent.joinpath("stats.json"), "w+") as f:
            import json
            json.dump(STATS, f, indent=2)



    def OM_check_model(self,
                       model_list: list,
                       exception_list: list = None):
        print(f'{self.green}Check models with OpenModelica{self.CEND}')
        error_model_dict = {}
        for model in model_list:
            err_list = []
            print(f'Check model {self.blue}{model}{self.CEND}')
            result = self.omc.sendExpression(f"checkModel({model})")
            if "completed successfully" in result:
                print(f'{self.green} Successful: {self.CEND} {model}')
            else:
                _err_msg = self.omc.sendExpression("getErrorString()")
                for line in _err_msg.split("\n"):
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
                    print(f'{self.CRED}  Error:   {self.CEND}  {model}')
                    print(f'{_err_msg}')
                else:
                    print(f'{self.yellow}  Warning:   {self.CEND}  {model}')
                    print(f'{_err_msg}')
                error_model_dict[model] = _err_msg

        self.omc.sendExpression("quit()")
        return error_model_dict


    """def _sort_error_warning(self):
        err_list = []
        warning_list = []
        for line in error_dict[model].split("\n"):
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
                err_list.append(line)"""


    def write_errorlog(self, error_dict: dict = None, exception_list: list = None):
        """
        Write an error log with all models, that don´t pass the check
        Args:
            error_dict ():
        """
        os.makedirs(pathlib.Path(self.check_log).parent, exist_ok=True)
        check_log = open(self.check_log, "w")
        err_log = open(self.err_log, "w")
        for model in error_dict:
            err_list = []
            warning_list = []
            for line in error_dict[model].split("\n"):
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
                check_log.write(f'\n\nError in model:  {model} \n')
                err_log.write(f'\n\nError in model:  {model} \n')
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
                check_log.write(f'\n\nWarning in model:  {model} \n')
                if len(warning_list) > 0:
                    for warning in warning_list:
                        check_log.write(warning + "\n")
        check_log.close()
        err_log.close()

    def read_error_log(self):
        error_log = open(self.err_log, "r")
        lines = error_log.readlines()
        error_log_list = []
        for line in lines:
            if "Error in model" in line:
                error_log_list.append(line)
                line = line.strip("\n")
                print(f'{self.CRED}{line}{self.CEND}')
        if len(error_log_list) > 0:
            print(f'{self.CRED}Open Modelica check failed{self.CEND}')
            exit_var = 1
        else:
            print(f'{self.green}Open Modelica check was successful{self.CEND}')
            exit_var = 0
        error_log.close()
        return exit_var




    def _install_library(self, libraries):
        for inst in libraries:
            lib_name = inst[0]
            version = inst[1]
            exact_match = inst[2]
            install_string = f'{lib_name}, "{version}", {exact_match} '
            inst_lib = self.omc.sendExpression(f'installPackage({install_string})')
            if inst_lib is True:
                print(f'{self.green}Install library "{lib_name}" with version "{version}"{self.CEND} ')
            else:
                print(f'{self.CRED}Error:{self.CEND} Load of "{lib_name}" with version "{version}" failed!')
                exit(1)


    def _load_library(self,
                      add_libraries: dict = None,
                      lib_path: str = os.path.abspath("."),
                      library: str = "AixLib",
                      root_library: str = None
                      ):
        if root_library is None:
            root_library = os.path.join(lib_path, library, "package.mo")
        load_bib = self.omc.sendExpression(f'loadFile("{root_library}")')
        if load_bib is True:
            print(f'{self.green}Load library {library}:{self.CEND} {root_library}')
        else:
            print(f'{self.CRED}Error:{self.CEND} Load of {root_library} failed!')
            exit(1)
        if add_libraries is not None:
            for lib in add_libraries:
                lib_path = os.path.join(add_libraries[lib], lib, "package.mo")
                load_add_bib = self.omc.sendExpression(f'loadFile("{lib_path}")')
                if load_add_bib is True:
                    print(f'{self.green}Load library {lib}:{self.CEND} {lib_path}')
                else:
                    print(f'{self.CRED}Error:{self.CEND} Load of library {lib} with path {lib_path} failed!')
                    exit(1)
        print(self.omc.sendExpression("getErrorString()"))



    def simulate_examples(self,
                          example_list: list,
                          exception_list: list = None):
        """
        Simulate examples or validations
        Args:
            example_list:
            exception_list:
        Returns:
        """
        self.create_path([self.all_sims_dir, self.temp_result_folder])
        self.delete_files_in_path([self.all_sims_dir])

        print(f'{self.green}Simulate examples and validations{self.CEND}')
        error_model_dict = {}
        for example in example_list:
            err_list = []
            print(f'Simulate example {self.blue}{example}{self.CEND}')
            result = self.omc.sendExpression(f"simulate({example})")
            if "The simulation finished successfully" in result["messages"]:
                print(f'\n {self.green}Successful:{self.CEND} {example}\n')
                #shutil.copy(result["resultFile"], self.all_sims_dir.joinpath(example + ".mat"))
                #shutil.copy(result["resultFile"], self.all_sims_dir)
                shutil.move(result["resultFile"], self.all_sims_dir)
            else:
                _err_msg = result["messages"]
                _err_msg += "\n" + self.omc.sendExpression("getErrorString()")
                for line in _err_msg.split("\n"):
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
                    print(f'{self.CRED}  Error:   {self.CEND}  {example}')
                    print(f'{_err_msg}')
                else:
                    print(f'{self.yellow}  Warning:   {self.CEND}  {example}')
                    print(f'{_err_msg}')
                error_model_dict[example] = _err_msg
            self.delete_spec_file(root=os.getcwd(), pattern=example)
        self.omc.sendExpression("quit()")
        return error_model_dict


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Check and validate single packages")
    check_test_group = parser.add_argument_group("Arguments to run check tests")
    check_test_group.add_argument("--package",
                                  metavar="AixLib.Package",
                                  help="Test the Modelica package")
    check_test_group.add_argument("--library",
                                  default="AixLib",
                                  help="Library to test")
    check_test_group.add_argument("--wh-library",
                                  default="IBPSA",
                                  help="Library on whitelist")
    check_test_group.add_argument("-WL", "--whitelist",
                                  help="Create a whitelist of a library with failed models.",
                                  action="store_true")
    check_test_group.add_argument("--simulate-flag",
                                  help="Check and simulate examples in the package",
                                  action="store_true")
    check_test_group.add_argument("--changed-flag",
                                  default=False,
                                  action="store_true")
    check_test_group.add_argument("--filter-wh-flag",
                                  default=False,
                                  action="store_true")
    check_test_group.add_argument("--extended-ex-flag",
                                  default=False,
                                  action="store_true")

    check_test_group.add_argument("--om-options",
                                  default="om_check",
                                  help="Chose between openmodelica check, compare or simulate")
    args = parser.parse_args()
    OM = Check_OpenModelica(package=args.package,
                            library=args.library,
                            wh_library=args.wh_library,
                            om_options=args.om_options,
                            simulate_flag=args.simulate_flag,
                            changed_flag=args.changed_flag,
                            filter_wh_flag=args.filter_wh_flag)

    model = modelica_model()
    install_libraries = [("Modelica_DeviceDrivers", "2.0.0", "exactMatch=true"),
                         ("SDF", "0.4.2", "exactMatch=false")]
    except_list = ["Warning: Conversion-annotation contains unknown element: nonFromVersion",
                   "failed with no error message."]

    #additional_libraries = {args.wh_library: os.path.join(os.path.abspath("."), "modelica-ibpsa")}
    additional_libraries = None
    if args.om_options == "OM_CHECK":
        OM._load_library(library=args.library, add_libraries=additional_libraries)
        OM._install_library(install_libraries)
        model_list = model.get_option_model(library=args.library,
                                            package=args.package,
                                            wh_library=args.wh_library,
                                            changed_flag=args.changed_flag,
                                            simulate_flag=False,
                                            filter_wh_flag=args.filter_wh_flag)
        error_model_dict = OM.OM_check_model(model_list=model_list,
                                             exception_list=except_list)

        OM.write_errorlog(error_dict=error_model_dict,
                          exception_list=except_list)
        exit_var = OM.read_error_log()
        exit(exit_var)
    if args.om_options == "OM_SIM":
        OM._load_library(library=args.library,
                         add_libraries=additional_libraries)
        OM._install_library(install_libraries)
        model_list = model.get_option_model(library=args.library,
                                            package=args.package,
                                            wh_library=args.wh_library,
                                            changed_flag=args.changed_flag,
                                            simulate_flag=True,
                                            filter_wh_flag=args.filter_wh_flag)
        error_model_dict = OM.simulate_examples(example_list=model_list,
                                                exception_list=except_list)
        OM.write_errorlog(error_dict=error_model_dict,
                          exception_list=except_list)
        exit_var = OM.read_error_log()
        exit(exit_var)
    else:
        raise ValueError(f"{args.om_options} not supported")


