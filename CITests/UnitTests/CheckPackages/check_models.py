import argparse
import os
import pathlib
import sys
import platform
import time
from threading import Thread
import shutil

import matplotlib.pyplot as plt
import numpy as np
from ebcpy import DymolaAPI, TimeSeriesData
from ebcpy.utils.statistics_analyzer import StatisticsAnalyzer

from OMPython import OMCSessionZMQ


class ValidateTest:
    """Class to Check Packages and run CheckModel Tests"""

    def __init__(self, single_package, library, library_dir, ibpsa_dir, sim):
        # Color
        self.CRED = '\033[91m'  # Colors
        self.CEND = '\033[0m'
        self.green = '\033[0;32m'

        self.single_package = single_package
        self.library = library
        self.library_dir = library_dir

        self.all_sims_dir = pathlib.Path(r"D:\00_temp\compare_om_to_dymola\om")

        main_package_name = self.single_package.split(".")[0]

        self.lib_path = f'{self.library_dir}{os.sep}{self.library}{os.sep}package.mo'
        self.root_package = f'{self.library_dir}{os.sep}{self.library}{os.sep}{main_package_name}'
        self.root_package_ibpsa = f'{ibpsa_dir}{os.sep}IBPSA{os.sep}{main_package_name}'
        self.err_log = f'{os.getcwd()}{os.sep}{self.library}{os.sep}' \
                       f'{self.library}.{main_package_name}-errorlog_{"sim" if sim else "check"}.txt'
        os.makedirs("_temp_results", exist_ok=True)
        os.chdir("_temp_results")
        self.omc = None
        self.dym_api = None
        self.for_bes_mod = self.library == "BESMod"


    ###################################################################################################################
    ## Write logs (error logs)
    def _write_errorlog(self, error_model,
                        error_message):  # Write a Error log with all models, that don´t pass the check
        os.makedirs(pathlib.Path(self.err_log).parent, exist_ok=True)
        error_log = open(self.err_log, "w")
        for model, message in zip(error_model, error_message):
            error_log.write(f'\n \n Error in model:  {model} \n')
            for line in message.split("\n"):
                if "Warning: Conversion-annotation contains unknown element: nonFromVersion" not in line:
                    error_log.write(line + "\n")
        error_log.close()

    ## Get Models to check or simulate
    @staticmethod
    def _get_model(dir, library_name, single_package):  # list all models in package
        model_list = []
        for subdir, dirs, files in os.walk(dir):
            for file in files:
                filepath = subdir + os.sep + file
                if filepath.endswith(".mo") and file != "package.mo":
                    model = filepath.replace(os.sep, ".")
                    model = model[model.rfind(library_name):model.rfind(".mo")]
                    if model.startswith(single_package):
                        model_list.append(model)

        return model_list

    def _get_icon_example(self, filepath):
        ex_file = open(filepath, "r", encoding='utf8', errors='ignore')
        lines = ex_file.readlines()
        for line in lines:
            if line.find("extends") > -1 and line.find("Modelica.Icons.Example") > -1:
                example = filepath.replace(os.sep, ".")
                example = example[example.rfind(self.library):example.rfind(".mo")]
                ex_file.close()
                return example

    def _get_simulate_examples(self):  # list all examples in package
        example_list = []
        for subdir, dirs, files in os.walk(self.root_package):
            for file in files:
                filepath = subdir + os.sep + file
                if filepath.endswith(".mo") and file != "package.mo":
                    example = self._get_icon_example(filepath=filepath)
                    if example is not None and example.startswith(self.library + "." + self.single_package):
                        example_list.append(example)
        if len(example_list) == 0:
            print(f'No models in package {self.single_package}')
            exit(0)
        return example_list

    def _load_library(self):
        if self.omc is not None:
            return self.omc
        t0 = time.time()
        omc = OMCSessionZMQ()
        omc.sendExpression('installPackage(Modelica_DeviceDrivers, "2.0.0", exactMatch=true)')
        if self.for_bes_mod:
            omc.sendExpression('loadFile("C://Program Files//Dymola 2023//Modelica//Library//SDF 0.4.2//package.mo")')
            omc.sendExpression(f'loadFile("{self.library_dir}//installed_dependencies//IBPSA//IBPSA//package.mo")')
            omc.sendExpression(f'loadFile("{self.library_dir}//installed_dependencies//AixLib//AixLib//package.mo")')
            omc.sendExpression(f'loadFile("{self.library_dir}//installed_dependencies//Buildings//Buildings//package.mo")')
            omc.sendExpression(f'loadFile("{self.library_dir}//installed_dependencies//BuildingSystems//BuildingSystems//package.mo")')
            omc.sendExpression(f'loadFile("{self.library_dir}//BESMod//package.mo")')
        else:
            pack_check = omc.sendExpression(f'loadFile("{self.lib_path}")')
            self._library_path_check(pack_check=pack_check)
        print(omc.sendExpression("getErrorString()"))
        return omc

    def _checkmodel(self, model_list):  # Check models and return a Error Log, if the check failed
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

    def _simulate_examples(self, example_list):  # Simulate examples or validations
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
        # simulate(className, [startTime], [stopTime],
        # [numberOfIntervals], [tolerance],
        # [method], [fileNamePrefix], [options], [outputFormat],
        # [variableFilter], [cflags], [simflags])
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

    def _get_ibpsa_whitelist(self):
        ibpsa_model_list = self._get_model(
            dir=self.root_package_ibpsa,
            library_name="IBPSA",
            single_package="IBPSA." + self.single_package
        )
        _models = []
        for m in ibpsa_model_list:
            _models.append(m.replace("IBPSA", self.library))
        return _models

    def _filter_whitelist(self, model_list):
        models_causing_om_to_crash = [
            "AixLib.Fluid.Storage.Examples.TwoPhaseSeparator"
        ]
        ibpsa_models = self._get_ibpsa_whitelist()
        ibpsa_models.extend(models_causing_om_to_crash)
        return list(set(model_list).difference(ibpsa_models))

    def check_model_workflow(self):
        self._check_packages()
        model_list = self._get_model(
            dir=self.root_package,
            library_name=self.library,
            single_package=self.library + "." + self.single_package
        )
        model_list = self._filter_whitelist(model_list)
        model_list.sort()
        result = self._checkmodel(model_list=model_list)
        self._write_errorlog(error_model=result[0], error_message=result[1])
        #self._check_result(error_model=result[0])

    def simulate_example_workflow(self):
        self._check_packages()
        simulate_example_list = self._get_simulate_examples()
        simulate_example_list = self._filter_whitelist(simulate_example_list)
        simulate_example_list.sort()
        result = self._simulate_examples(example_list=simulate_example_list)
        self._write_errorlog(error_model=result[0], error_message=result[1])
        #self._check_result(error_model=result[0])

    def sim_with_dymola(self):
        self._check_packages()
        simulate_example_list = self._get_simulate_examples()
        simulate_example_list = self._filter_whitelist(simulate_example_list)
        simulate_example_list.sort()
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

    def compare_dym_to_om(self, stats=None, with_plot=True):
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
        simulate_example_list = self._get_simulate_examples()
        simulate_example_list = self._filter_whitelist(simulate_example_list)
        simulate_example_list.sort()
        om_dir = self.all_sims_dir
        dym_dir = self.all_sims_dir.parent.joinpath("dym")
        plot_dir = self.all_sims_dir.parent.joinpath("plots", self.single_package)
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
                    plt.savefig(_dir.joinpath(col+".png"))
                    plt.cla()

            errors[model] = {
                "average": np.mean(list(_col_err.values())),
                "detailed": _col_err,
                "n_diff_events": _n_diff_idx,
                "n_different_cols": _n_diff_cols
            }

        return errors, stats


if __name__ == '__main__':
    PATH_TO_AIXLIB = r"D:\04_git\AixLib"
    LIBRARY_NAME = "AixLib"
    PATH_TO_AIXLIB = r"D:\04_git\BESMod"
    LIBRARY_NAME = "BESMod"

    PATH_TO_IBPSA = r"D:\04_git\modelica-ibpsa"
    PACKAGES_TO_TEST = [
        "DataBase",
        "Airflow",
        "BoundaryConditions",
        "Electrical",
        "Fluid",
        "Controls",
        "Systems",
        "Utilities",
        "ThermalZones",
    ]
    PACKAGES_TO_TEST = [
        "Examples",
        "Systems",
        "Tutorial",
        "Utilities",
    ]
    OPTIONS = [
        #"OM_CHECK",
        "OM_SIM",
        #"COMPARE",
        #"DYMOLA_SIM",
    ]
    ERROR_DATA = {}
    STATS = None

    for PACKAGE in PACKAGES_TO_TEST:
        for CHECK_SIM in OPTIONS:
            os.chdir(os.path.dirname(__file__))

            check_model_test = ValidateTest(
                single_package=PACKAGE,
                library=LIBRARY_NAME,
                library_dir=PATH_TO_AIXLIB,
                ibpsa_dir=PATH_TO_IBPSA,
                sim=CHECK_SIM == "OM_SIM"
            )

            if CHECK_SIM == "OM_SIM":  # Simulate Models
                check_model_test.simulate_example_workflow()
            elif CHECK_SIM == "DYMOLA_SIM":
                check_model_test.sim_with_dymola()
            elif CHECK_SIM == "OM_CHECK":  # Check all Models in a Package
                check_model_test.check_model_workflow()
            elif CHECK_SIM == "COMPARE":
                ERROR_DATA[PACKAGE], STATS = check_model_test.compare_dym_to_om(stats=STATS)
            else:
                raise ValueError(f"{CHECK_SIM} not supported")

    with open(check_model_test.all_sims_dir.parent.joinpath("error_data.json"), "w+") as f:
        import json
        json.dump(ERROR_DATA, f, indent=2)
    with open(check_model_test.all_sims_dir.parent.joinpath("stats.json"), "w+") as f:
        import json
        json.dump(STATS, f, indent=2)
