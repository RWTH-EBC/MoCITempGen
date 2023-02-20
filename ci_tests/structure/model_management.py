import os
import platform
from ci_test_config import ci_config


class Model_Management(ci_config):

    def __init__(self,
                 dymola,
                 dymola_exception,
                 dymola_version: int = 2022):
        super().__init__()
        self.dymola = dymola
        self.dymola_exception = dymola_exception
        self.dymola.ExecuteCommand("Advanced.TranslationInCommandLog:=true;")
        self.dymola_version = dymola_version

    def load_model_management(self):
        if platform.system() == "Windows":
            mm_path = f'cd("C:\Program Files\Dymola {str(self.dymola_version)}\Modelica\Library\ModelManagement 1.1.8\package.moe");'
            self.dymola.ExecuteCommand(mm_path)
        else:
            mm_path = f'cd("/opt/dymola-{str(self.dymola_version)}-x86_64/Modelica/Library/ModelManagement 1.1.8/package.moe");'
            self.dymola.ExecuteCommand(mm_path)
        print(f"Load Model Management from path: {mm_path}")

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
