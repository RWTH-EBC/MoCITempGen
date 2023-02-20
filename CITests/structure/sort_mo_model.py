import os
from CI_test_config import CI_config
from CITests.structure.model_management import Model_Management
from pathlib import Path


class modelica_model(CI_config):

    def __init__(self):
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
                         path_dir: str = Path.home(),
                         root_package: Path = None,
                         root_library: Path = None):

        self.check_arguments_settings(package, library, changed_flag, simulate_flag, filter_wh_flag, extended_ex_flag)
        if root_package is None:
            root_package = Path(path_dir, library, package.replace(".", os.sep))
        self.check_path_setting(root_package)
        if root_library is None:
            root_library = Path(path_dir, library, "package.mo")
        self.check_file_setting(root_library)

        if dymola is None:
            extended_ex_flag = False
        if changed_flag is True:
            self.check_path_setting(self.config_ci_dir)
            self.check_file_setting(self.config_ci_changed_file)
            model_list = self.get_changed_models(ch_file=self.config_ci_changed_file,
                                                 library=library,
                                                 single_package=package,
                                                 simulate_examples=simulate_flag)
        elif filter_wh_flag is True:
            if simulate_flag is True:
                ci_wh_file = self.wh_simulate_file
                file_list = self.wh_simulate_file
            else:
                ci_wh_file = self.wh_model_file
                file_list = self.wh_model_file
            self.check_path_setting(self.wh_ci_dir)
            self.check_file_setting(file_list)
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

    def get_extended_model(self,
                           dymola: object,
                           dymola_exception: object,
                           model_list: list,
                           dymola_version: int = 2022,
                           library: str = "AixLib") -> object:

        mm = Model_Management(dymola=dymola,
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
            exit(0)
        else:
            return model_list, no_example_list
