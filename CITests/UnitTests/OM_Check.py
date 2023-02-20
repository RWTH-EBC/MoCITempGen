import sys
from ebcpy import DymolaAPI, TimeSeriesData
from ebcpy.utils.statistics_analyzer import StatisticsAnalyzer
from OMPython import OMCSessionZMQ

from CI_test_config import CI_config
from CITests.structure.sort_mo_model import modelica_model
from CITests.structure.toml_class import Convert_types
from CITests.structure.arg_parser import StoreDictKeyPair, StoreDictKeyPair_list, StoreDictKey
# from Dymola_python_tests.CI_test_config import CI_config
# from Dymola_python_tests.CITests.structure.sort_mo_model import modelica_model
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import argparse
import toml
import os



class Check_OpenModelica(CI_config):

    def __init__(self,
                 lib_name: str = None,
                 working_path: Path = Path.home(),
                 add_libraries_loc: dict = None,
                 inst_libraries: list = None):
        """
        Args:
            add_libraries_loc ():
            inst_libraries ():
            lib_name ():
            working_path ():
        """
        super().__init__()
        self.check_arguments_settings(lib_name)
        root_library = Path(working_path, lib_name, "package.mo")
        self.check_file_setting(root_library)
        self.root_library = root_library
        if add_libraries_loc is not None:
            for lib in add_libraries_loc:
                add_lib_path = Path(add_libraries_loc[lib], lib, "package.mo")
                self.check_file_setting(add_lib_path)
        self.add_libraries_loc = add_libraries_loc
        self.install_libraries = inst_libraries

        self.library = lib_name
        self.working_path = working_path
        # [start openModelica]
        self.omc = OMCSessionZMQ()
        print(f'{self.green}OpenModelica Version number:{self.CEND} {self.omc.sendExpression("getVersion()")}')
        # [start dymola api]
        self.dym_api = None

    def __call__(self):
        self.load_library(root_library=self.root_library, add_libraries_loc=self.add_libraries_loc)
        self.install_library(libraries=self.install_libraries)

    def simulate_examples(self, example_list: list = None, exception_list: list = None):
        """
        Simulate examples or validations
        Args:
            example_list:
            exception_list:
        Returns:
        """

        all_sims_dir = Path(self.working_path, self.result_OM_check_result_dir, f'{self.library}.{package}')
        API_log = Path(self.working_path, "DymolaAPI.log")
        self.create_path([all_sims_dir])
        self.delete_files_in_path([all_sims_dir])
        if example_list is not None:
            print(f'{self.green}Simulate examples and validations{self.CEND}')
            error_model = {}
            for example in example_list:
                err_list = []
                print(f'Simulate example {self.blue}{example}{self.CEND}')
                result = self.omc.sendExpression(f"simulate({example})")
                if "The simulation finished successfully" in result["messages"]:
                    print(f'\n {self.green}Successful:{self.CEND} {example}\n')
                    self.prepare_data(source_target_dict={result["resultFile"]: all_sims_dir})
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
                    error_model[example] = _err_msg
                self.delete_spec_file(root=os.getcwd(), pattern=example)
            self.omc.sendExpression("quit()")
            self.prepare_data(source_target_dict={
                API_log: Path(self.result_OM_check_result_dir, f'{self.library}.{package}')},
                del_flag=True)
            return error_model
        else:
            print(f'No examples to check. ')
            exit(0)

    def OM_check_model(self,
                       check_model_list: list = None,
                       exception_list: list = None):
        """
        Args:
            check_model_list ():
            exception_list ():
        Returns:
        """
        print(f'{self.green}Check models with OpenModelica{self.CEND}')
        error_model = {}
        if check_model_list is not None:
            for m in check_model_list:
                err_list = []
                print(f'Check model {self.blue}{m}{self.CEND}')
                result = self.omc.sendExpression(f"checkModel({m})")
                if "completed successfully" in result:
                    print(f'{self.green} Successful: {self.CEND} {m}')
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
                        print(f'{self.CRED}  Error:   {self.CEND}  {m}')
                        print(f'{_err_msg}')
                    else:
                        print(f'{self.yellow}  Warning:   {self.CEND}  {m}')
                        print(f'{_err_msg}')
                    error_model[m] = _err_msg
            self.omc.sendExpression("quit()")
            return error_model
        else:
            print(f'No models to check')
            exit(0)

    def write_errorlog(self,
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
                ch_log = Path(self.working_path, self.result_OM_check_result_dir,
                              f'{self.library}.{pack}-check_log.txt')
                error_log = Path(self.working_path, self.result_OM_check_result_dir,
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
            print(f'{self.CRED}Open Modelica check failed{self.CEND}')
            var = 1
        else:
            print(f'{self.green}Open Modelica check was successful{self.CEND}')
            var = 0
        error_log.close()
        self.prepare_data(source_target_dict={
            check_log: Path(self.result_OM_check_result_dir, f'{self.library}.{pack}'),
            err_log: Path(self.result_OM_check_result_dir, f'{self.library}.{pack}')},
            del_flag=True)
        return var

    def install_library(self, libraries: list = None):
        load_modelica = self.omc.sendExpression(f'installPackage(Modelica, "4.0.0+maint.om", exactMatch=true)')
        if load_modelica is True:
            print(f'{self.green}Load library modelica in Openmodelica.{self.CEND}')
        else:
            print(f'Load of modelica has failed.')
            exit(1)
        if libraries is not None:
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
        print(self.omc.sendExpression("getErrorString()"))

    def load_library(self, root_library: Path = None, add_libraries_loc: dict = None):
        if root_library is not None:
            load_bib = self.omc.sendExpression(f'loadFile("{root_library}")')
            if load_bib is True:
                print(f'{self.green}Load library {library}:{self.CEND} {root_library}')
            else:
                print(f'{self.CRED}Error:{self.CEND} Load of {root_library} failed!')
                exit(1)
        else:
            print(f'Library path is not set.')
            exit(1)
        if add_libraries_loc is not None:
            for lib in add_libraries_loc:
                lib_path = Path(add_libraries_loc[lib], lib, "package.mo")
                load_add_bib = self.omc.sendExpression(f'loadFile("{lib_path}")')
                if load_add_bib is True:
                    print(f'{self.green}Load library {lib}:{self.CEND} {lib_path}')
                else:
                    print(f'{self.CRED}Error:{self.CEND} Load of library {lib} with path {lib_path} failed!')
                    exit(1)
        print(self.omc.sendExpression("getErrorString()"))

    def sim_with_dymola(self, pack: str = None, example_list: list = None):
        all_sims_dir = Path(self.working_path, self.result_OM_check_result_dir, f'{self.library}.{pack}')
        if example_list is not None:
            if self.dym_api is None:
                lib_path = Path(self.working_path, self.library, "package.mo")
                self.dym_api = DymolaAPI(
                    cd=os.getcwd(),
                    model_name=example_list[0],
                    packages=[lib_path],
                    extract_variables=True,
                    load_experiment_setup=True
                )

            for example in example_list:
                print(f'Simulate model: {example}')
                try:
                    self.dym_api.model_name = example
                    print("Setup", self.dym_api.sim_setup)
                    result = self.dym_api.simulate(return_option="savepath")
                except Exception as err:
                    print("Simulation failed: " + str(err))
                    continue
                print(f'\n {self.green}Successful:{self.CEND} {example}\n')
                self.prepare_data(source_target_dict={result: Path(all_sims_dir, "dym")})
            self.dym_api.close()
            API_log = Path(self.working_path, "DymolaAPI.log")
            self.prepare_data(source_target_dict={
                API_log: Path(self.result_OM_check_result_dir, f'{self.library}.{pack}')},
                del_flag=True)
        else:
            print(f'No examples to check. ')
            exit(0)

    def compare_dym_to_om(self,
                          example_list: list = None,
                          stats: dict = None,
                          with_plot: bool = True,
                          pack: str = None):
        if example_list is not None:
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
            all_sims_dir = Path(self.working_path, self.result_OM_check_result_dir, f'{self.library}.{pack}')
            om_dir = all_sims_dir
            dym_dir = Path(all_sims_dir, "dym")
            plot_dir = Path(all_sims_dir, "plots", pack)
            _tol = 0.0001
            for example in example_list:
                continue_after_for = False
                for tool, _dir in zip(["om", "dymola"], [om_dir, dym_dir]):
                    path_mat = Path(_dir, f'{example}.mat')
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

                om_tsd = TimeSeriesData(Path(om_dir, f'{example}.mat'))
                dym_tsd = TimeSeriesData(Path(dym_dir, f'{example}.mat'))
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
                        print(f"Index still differs {example}: {err}")
                        break
                for c in dym_tsd.columns:
                    if c not in _col_err:
                        _n_diff_cols += 1
                if with_plot:
                    _dir = Path(plot_dir, example)
                    if cols_to_plot:
                        os.makedirs(_dir, exist_ok=True)
                    for col in cols_to_plot:
                        plt.plot(om_tsd_ref.loc[:, col], label="OM")
                        plt.plot(dym_tsd_ref.loc[:, col], label="Dymola")
                        plt.legend()
                        plt.xlabel("Time in s")
                        plt.savefig(Path(_dir, f'{col}.png'))
                        plt.cla()

                errors[example] = {
                    "average": np.mean(list(_col_err.values())),
                    "detailed": _col_err,
                    "n_diff_events": _n_diff_idx,
                    "n_different_cols": _n_diff_cols
                }
            print(f'Compare finished.')
            return errors, stats
        else:
            print(f'No Models to compare.')
            exit(0)


class Parser:
    def __init__(self, args):
        self.args = args
        pass

    def main(self):
        parser = argparse.ArgumentParser(description="Check and validate single packages")
        check_test_group = parser.add_argument_group("Arguments to run check tests")
        # [Library - settings]
        check_test_group.add_argument("--library", dest="library_dict", action=StoreDictKeyPair, nargs="*",
                                      metavar="Library1=Path_Lib1 Library2=Path_Lib2")
        check_test_group.add_argument("--package", dest="package_dict", action=StoreDictKeyPair_list, nargs="*",
                                      metavar="Library1=Package1,Package2 Library2=Package3,Package4")
        check_test_group.add_argument("--wh-library",
                                      default="IBPSA",
                                      help="Library on whitelist")
        # [ bool - flag]
        check_test_group.add_argument("--changed-flag",
                                      default=False,
                                      action="store_true")
        check_test_group.add_argument("--filter-wh-flag",
                                      default=False,
                                      action="store_true")
        check_test_group.add_argument("--extended-ex-flag",
                                      default=False,
                                      action="store_true")
        check_test_group.add_argument("--load-setti"
                                      "ng-flag",
                                      default=True,

                                      action="store_true")
        # [OM - Options: OM_CHECK, OM_SIM, DYMOLA_SIM, COMPARE]
        check_test_group.add_argument("--om-options",
                                      default="om_check",
                                      help="Chose between openmodelica check, compare or simulate")
        args = parser.parse_args()
        return args



if __name__ == '__main__':
    args = Parser(sys.argv[1:]).main()
    # [Settings]
    if args.load_setting_flag is True:
        toml_file = f'test_config.toml'
        data = toml.load(f'{toml_file}')
        install_libraries = data["OM_Check"]["install_libraries"]
        except_list = data["OM_Check"]["except_list"]
        additional_libraries_local = data["OM_Check"]["additional_libraries_local"]
        additional_libraries_local = Convert_types().convert_list_to_dict_toml(convert_list=additional_libraries_local,
                                                                               wh_library=args.wh_library)
    else:
        install_libraries = None
        except_list = None
        additional_libraries_local = None

    if args.library_dict is not None:
        if args.package_dict is not None:
            for library in args.library_dict:
                try:
                    packages = args.package_dict[library]
                    OM = Check_OpenModelica(lib_name=library,
                                            working_path=args.library_dict[library],
                                            add_libraries_loc=additional_libraries_local,
                                            inst_libraries=install_libraries)
                    OM()
                    model = modelica_model()
                    for package in packages:
                        if args.om_options == "OM_CHECK":
                            model_list = model.get_option_model(library=library,
                                                                package=package,
                                                                wh_library=args.wh_library,
                                                                changed_flag=args.changed_flag,
                                                                simulate_flag=False,
                                                                filter_wh_flag=args.filter_wh_flag)
                            error_model_dict = OM.OM_check_model(check_model_list=model_list,
                                                                 exception_list=except_list)
                            exit_var = OM.write_errorlog(pack=package,
                                                         error_dict=error_model_dict,
                                                         exception_list=except_list)

                            exit(exit_var)
                        if args.om_options == "OM_SIM":
                            model_list = model.get_option_model(library=library,
                                                                package=package,
                                                                wh_library=args.wh_library,
                                                                changed_flag=args.changed_flag,
                                                                simulate_flag=True,
                                                                filter_wh_flag=args.filter_wh_flag)
                            error_model_dict = OM.simulate_examples(example_list=model_list,
                                                                    exception_list=except_list)
                            exit_var = OM.write_errorlog(pack=package,
                                                         error_dict=error_model_dict,
                                                         exception_list=except_list)
                            exit(exit_var)
                        if args.om_options == "DYMOLA_SIM":
                            model_list = model.get_option_model(library=library,
                                                                package=package,
                                                                wh_library=args.wh_library,
                                                                changed_flag=args.changed_flag,
                                                                simulate_flag=True,
                                                                filter_wh_flag=args.filter_wh_flag)
                            OM.sim_with_dymola(example_list=model_list, pack=package)
                        if args.om_options == "COMPARE":
                            ERROR_DATA = {}
                            STATS = None
                            model_list = model.get_option_model(library=library,
                                                                package=package,
                                                                wh_library=args.wh_library,
                                                                changed_flag=args.changed_flag,
                                                                simulate_flag=True,
                                                                filter_wh_flag=args.filter_wh_flag)
                            STATS = OM.compare_dym_to_om(pack=package,
                                                         example_list=model_list,
                                                         stats=STATS)
                        else:
                            raise ValueError(f"{args.om_options} not supported")

                except KeyError:
                    print(f"For library {library} is not Package set.")
        else:
            print("Package not set")

