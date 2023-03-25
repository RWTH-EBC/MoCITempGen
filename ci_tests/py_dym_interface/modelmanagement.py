import os
import platform
from ci_test_config import ci_config
from pathlib import Path
import codecs

class ModelManagement(ci_config):

    def __init__(self,
                 dymola,
                 dymola_exception,
                 dymola_version: int = 2022):
        super().__init__()
        self.dymola = dymola
        self.dymola_exception = dymola_exception
        self.dymola.ExecuteCommand("Advanced.TranslationInCommandLog:=true;")
        self.dymola_version = dymola_version

    #def __call__(self):

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
        extended_list = list(set(extended_list))
        for ext in extended_list:
            model_list.remove(ext)
        model_list = list(set(model_list))
        return model_list

    def mm_style_check(self, library: str, models_list: list = None, changed_flag: bool = False):
        log_file = Path(Path.cwd(), library, f'{library}_StyleCheckLog.html')
        if changed_flag is True:
            if len(models_list) > 100:
                print(f'Check all models in {library} library\n')
                sm = f'ModelManagement.Check.checkLibrary(false, false, false, true, "{library}", translationStructure=false);'
                self.dymola.ExecuteCommand(sm)
                self.dymola.close()
            else:
                changed_model_list = []
                for model in models_list:
                    print(f'Check model {model} \n')
                    sm = f'ModelManagement.Check.checkLibrary(false, false, false, true, "{model}", translationStructure=false);'
                    self.dymola.ExecuteCommand(sm)
                    log = codecs.open(str(Path(Path.cwd(), library, f'{model}_StyleCheckLog.html')), "r", encoding='utf8')
                    for line in log:
                        changed_model_list.append(line)
                    log.close()
                    os.remove(Path(Path.cwd(), library, f'{model}_StyleCheckLog.html'))
                all_logs = codecs.open(str(log_file), "w", encoding='utf8')
                for model in changed_model_list:
                    all_logs.write(model)
                all_logs.close()

        else:
            print(f'Check all models in {library} library\n')
            sm = f'ModelManagement.Check.checkLibrary(false, false, false, true, "{library}", translationStructure=false);'
            self.dymola.ExecuteCommand(sm)
            self.dymola.close()
        return log_file

    def get_extended_examples(self, model: str = ""):
        model_list = self.dymola.ExecuteCommand(f'ModelManagement.Structure.AST.Classes.ExtendsInClass("{model}");')
        extended_list = self._filter_modelica_types(model_list=model_list)
        return extended_list

    def get_used_models(self, model: str = ""):
        model_list = self.dymola.ExecuteCommand(f'ModelManagement.Structure.Instantiated.UsedModels("{model}");')
        extended_list = self._filter_modelica_types(model_list=model_list)
        return extended_list
