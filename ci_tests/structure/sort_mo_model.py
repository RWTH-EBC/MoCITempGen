import os
from ci_test_config import ci_config
from ci_tests.py_dym_interface.modelmanagement import ModelManagement
from pathlib import Path
from ci_tests.structure.config_structure import data_structure


class modelica_model(ci_config):

    def __init__(self, library: str = "AixLib", package: str = "Airflow"):
        self.library = library
        self.package = package
        super().__init__()

    def get_option_model(self,
                         library: str,
                         package: str,
                         dymola=None,
                         dymola_exception=None,
                         changed_flag: bool = False,
                         simulate_flag: bool = False,
                         filter_wh_flag: bool = False,
                         wh_library: str = "IBPSA",
                         extended_ex_flag: bool = False,
                         dymola_version: int = 2022,
                         path_dir: Path = Path.cwd(),
                         root_library: Path = None,
                         root_package: Path = None):
        # todo: flag mit einbauen: In zukunft sollen die pfade gegeben werden, nach wunsch auch in modelica form
        """
        Args:
            library ():
            package ():
            dymola ():
            dymola_exception ():
            changed_flag ():
            simulate_flag ():
            filter_wh_flag ():
            wh_library ():
            extended_ex_flag ():
            dymola_version ():
            path_dir ():
            root_library ():
            root_package ():
        Returns:
        """
        check = data_structure()
        check.check_arguments_settings(package, library, changed_flag, simulate_flag, filter_wh_flag, extended_ex_flag)
        if root_library is None:
            root_library = Path(path_dir, library, "package.mo")
        check.check_file_setting(root_library)
        if root_package is None:
            if package == ".":
                root_package = Path(Path(root_library).parent)
            else:
                root_package = Path(Path(root_library).parent, package.replace(".", os.sep))
        check.check_path_setting(root_package)
        if dymola is None:
            extended_ex_flag = False
        if changed_flag is True:
            # todo: ci_changed_file selbst im skript erschaffen, nicht in der gitlab pipeline selbst
            check.check_path_setting(self.config_ci_dir)
            check.check_file_setting(self.config_ci_changed_file)
            result = self.get_changed_models(ch_file=self.config_ci_changed_file,
                                             library=library,
                                             single_package=package,
                                             simulate_examples=simulate_flag)
            model_list = result[0]
            if extended_ex_flag is True:
                simulate_list = self.get_extended_model(dymola=dymola,
                                                        dymola_exception=dymola_exception,
                                                        model_list=result[1],
                                                        library=library,
                                                        dymola_version=dymola_version)
                model_list.extend(simulate_list)
                model_list = list(set(model_list))
        elif filter_wh_flag is True:
            if simulate_flag is True:
                ci_wh_file = self.wh_simulate_file
                file_list = self.wh_simulate_file
            else:
                ci_wh_file = self.wh_model_file
                file_list = self.wh_model_file
            check.check_path_setting(self.wh_ci_dir, create_flag=True)
            check.check_file_setting(file_list, create_flag=True)
            wh_list_models = self.get_wh_models(wh_file=ci_wh_file,
                                                wh_library=wh_library,
                                                library=library,
                                                single_package=package)
            result = self.get_models(path=root_package,
                                     library=library,
                                     simulate_flag=simulate_flag,
                                     extended_ex_flag=extended_ex_flag)
            model_list = result[0]
            if extended_ex_flag is True:
                simulate_list = self.get_extended_model(dymola=dymola,
                                                        dymola_exception=dymola_exception,
                                                        model_list=result[1],
                                                        library=library,
                                                        dymola_version=dymola_version)
                model_list.extend(simulate_list)
                model_list = list(set(model_list))
            model_list = self.filter_wh_models(models=model_list,
                                               wh_list=wh_list_models)
        else:
            result = self.get_models(path=root_package,
                                     library=library,
                                     simulate_flag=simulate_flag,
                                     extended_ex_flag=extended_ex_flag)
            model_list = result[0]
            if extended_ex_flag is True:
                simulate_list = self.get_extended_model(dymola=dymola,
                                                        dymola_exception=dymola_exception,
                                                        model_list=result[1],
                                                        library=library,
                                                        dymola_version=dymola_version)
                model_list.extend(simulate_list)
                model_list = list(set(model_list))
        if len(model_list) == 0 or model_list is None:
            print(f'Find no models in package {package}')
            exit(0)
        else:
            return model_list

    def get_changed_regression_models(self,
                                      dymola,
                                      dymola_exception,
                                      dymola_version: int,
                                      root_package: Path,
                                      library: str,
                                      ch_file: Path):
        """
        Returns:
        """
        changed_models = open(ch_file, "r", encoding='utf8')
        changed_lines = changed_models.readlines()
        changed_models.close()
        # List all type of files from changed file
        mos_script_list = self.get_ch_mos_script(ch_lines=changed_lines)
        modelica_model_list = self.get_ch_model(ch_lines=changed_lines)
        reference_list = self.ch_ref_files(ch_lines=changed_lines)
        # get all models from page package
        model_list, no_example_list = self.get_models(path=root_package,
                                                      library=library,
                                                      simulate_flag=True,
                                                      extended_ex_flag=False)
        extended_list = self.get_extended_model(dymola=dymola,
                                                dymola_exception=dymola_exception,
                                                model_list=model_list,
                                                dymola_version=dymola_version,
                                                library=library)

        ch_model_list = self.get_changed_used_model(ch_lines=changed_lines, extended_list=extended_list)

        changed_list = self.return_type_list(ref_list=reference_list,
                                             mos_list=mos_script_list,
                                             modelica_list=modelica_model_list,
                                             ch_model_list=ch_model_list)
        if len(changed_list) == 0:
            print(f'No models to check and cannot start a regression test')
            exit(0)
        else:
            print(f'Number of checked packages: {str(len(changed_list))}')
            return changed_list

    def get_extended_model(self,
                           dymola: object,
                           dymola_exception: object,
                           model_list: list,
                           dymola_version: int = 2022,
                           library: str = "AixLib"):

        mm = ModelManagement(dymola=dymola,
                             dymola_exception=dymola_exception,
                             dymola_version=dymola_version)

        mm.load_model_management()
        simulate_list = list()
        for model in model_list:
            print(f' **** Check structure of model {model} ****')
            extended_list = mm.get_extended_examples(model=model)
            used_list = mm.get_used_models(model=model)
            extended_list.extend(used_list)
            for ext in extended_list:
                print(f'Extended model {ext} ')
                filepath = f'{ext.replace(".", os.sep)}.mo'
                example_test = self._get_icon_example(filepath=filepath,
                                                      library=library)
                if example_test is None:
                    print(f'File {filepath} is no example.')
                else:
                    simulate_list.append(model)
                    simulate_list.append(ext)
        simulate_list = list(set(simulate_list))
        return simulate_list

    def get_ch_mos_script(self, ch_lines: list):
        _list = []
        for line in ch_lines:
            if line.rfind(".mos") > -1 and line.rfind("Scripts") > -1 and line.find(
                    ".package") == -1 and line.rfind(self.package) > -1:
                line = line.replace("Dymola", self.library)
                _list.append(line[line.rfind(self.library):line.rfind(".mos")])
        return _list

    def get_ch_model(self, ch_lines: list):
        _list = []
        for line in ch_lines:
            if line.rfind(".mo") > -1 and line.find("package.") == -1 and line.rfind(
                    self.package) > -1 and line.rfind("Scripts") == -1:
                _list.append(line[line.rfind(self.library):line.rfind(".mo")])
        return _list

    def ch_ref_files(self, ch_lines: list):
        _list = []
        for line in ch_lines:
            if line.rfind(".txt") > -1 and line.find("package.") == -1 and line.rfind(
                    self.package) > -1 and line.rfind("Scripts") == -1:
                _list.append(line[line.rfind(self.library):line.rfind(".txt")])
        return _list

    @staticmethod
    def get_wh_models(wh_file: str,
                      wh_library: str,
                      library: str,
                      single_package: str):
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

    def _model_to_ref_exist(self, ref_file):
        model_file = ref_file.replace("_", os.sep)
        for subdir, dirs, files in os.walk(self.package.replace(".", os.sep)):
            for file in files:
                filepath = f'{self.library}{os.sep}{subdir}{os.sep}{file}'
                if filepath.endswith(".mo") and filepath.find(self.package.replace(".", os.sep)) > -1:
                    if filepath.find(model_file) > -1:
                        return model_file.replace(os.sep, ".")

    def _mos_script_to_model_exist(self, model):
        test_model = model.replace(f'{self.library}.', "")
        test_model = test_model.replace(".", os.sep)
        for subdir, dirs, files in os.walk(self.library_resource_dir):
            for file in files:
                filepath = subdir + os.sep + file
                if filepath.endswith(".mos") and filepath.find(self.package.replace(".", os.sep)) > -1:
                    if filepath.find(test_model) > -1:
                        infile = open(filepath, "r")
                        lines = infile.read()
                        infile.close()
                        if lines.find("simulateModel") > -1:
                            return model
                        if lines.find("simulateModel") == -1:
                            return None

    def model_to_mos_script_exist(self, mos_script):
        model_file = mos_script.replace(".", os.sep)
        for subdir, dirs, files in os.walk(self.package.replace(".", os.sep)):
            for file in files:
                filepath = f'{self.library}{os.sep}{subdir}{os.sep}{file}'
                if filepath.endswith(".mo") and filepath.find(self.package.replace(".", os.sep)) > -1:
                    if filepath.find(model_file) > -1:
                        return mos_script

    def return_type_list(self,
                         ref_list,
                         mos_list,
                         modelica_list,
                         ch_model_list):
        """
        return models, scripts, reference results and used models, that changed
        Args:
            ref_list (): list of reference files
            mos_list (): list of .mos files
            modelica_list (): list of modelica files
            ch_model_list (): list of changed models
        Returns:
        """
        changed_list = []
        print(f'\n ------The last modified files ------\n')
        if ref_list is not None:
            for ref in ref_list:
                model_file = self._model_to_ref_exist(ref_file=ref)
                if model_file is not None:
                    model = self._mos_script_to_model_exist(model=model_file)
                    if model is not None:
                        print(f'Changed reference files: {ref}')
                        changed_list.append(ref[:ref.rfind("_")].replace("_", "."))
        if mos_list is not None:
            for mos in mos_list:
                mos_script = self.model_to_mos_script_exist(mos_script=mos)
                if mos_script is not None:
                    model = self._mos_script_to_model_exist(model=mos_script)
                    if model is not None:
                        print(f'Changed mos script files: {mos}')
                        changed_list.append(mos[:mos.rfind(".")])
        if modelica_list is not None:
            for model in modelica_list:
                model = self._mos_script_to_model_exist(model=model)
                if model is not None:
                    print(f'Changed model files: {model}')
                    changed_list.append(model[:model.rfind(".")])
        if ch_model_list is not None:
            for used_model in ch_model_list:
                model = self._mos_script_to_model_exist(model=used_model)
                if model is not None:
                    print(f'Changed used model files: {used_model}')
                    changed_list.append(used_model[:used_model.rfind(".")])
        print(f'\n -----------------------------------\n')
        changed_list = list(set(changed_list))
        return changed_list

    def get_changed_used_model(self, ch_lines: list, extended_list: list):
        """
        return all used models, that changed
        Args:
            ch_lines (): lines from changed models
            extended_list (): models to check
        Returns:
            ch_model_list () : return a list of changed models
        """

        ch_model_list = []
        for line in ch_lines:
            for model in extended_list:
                if line[line.find(self.library):line.rfind(".mo")].strip() == model:
                    ch_model_list.append(model)
        return ch_model_list

    def get_changed_models(self,
                           ch_file: Path,
                           library: str,
                           single_package: str,
                           simulate_examples: bool = False,
                           extended_ex_flag: bool = False):
        """
        Returns: return a list with changed models.
        """
        try:
            file = open(ch_file, "r", encoding='utf8', errors='ignore')
            lines = file.readlines()
            modelica_models = []
            no_example_list = []
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
                                if extended_ex_flag is True:
                                    no_example = line.replace(os.sep, ".")
                                    no_example = no_example[no_example.rfind(library):no_example.rfind(".mo")]
                                    no_example_list.append(no_example)
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
            return modelica_models, no_example_list
        except IOError:
            print(f'Error: File {ch_file} does not exist.')
            exit(0)

    def get_models(self,
                   path: Path,
                   library: str = "AixLib",
                   simulate_flag: bool = False,
                   extended_ex_flag: bool = False):
        """
            Args:
                simulate_flag ():
                extended_ex_flag ():
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
                    if simulate_flag is True:
                        example_test = self._get_icon_example(filepath=filepath,
                                                              library=library)
                        if example_test is None:
                            print(
                                f'Model {filepath} is not a simulation example because it does not contain the following "Modelica.Icons.Example"')
                            if extended_ex_flag is True:
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
            return model_list, no_example_list

        else:
            return model_list, no_example_list
