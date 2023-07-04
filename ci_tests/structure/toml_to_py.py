import toml
import os
from mako.template import Template
from pathlib import Path
import argparse
import sys


class toml_to_py():

    def __init__(self):
        pass

    def load_toml(self, toml_file: Path):
        data = toml.load(toml_file)
        config_list = []
        for d in data:
            toml_cont = data[d]
            docu = f"# [{d}]"
            config_list.append(docu)
            for var in toml_cont:
                conf = ""
                if isinstance(toml_cont[var], str):
                    conf = f'self.{var} = f"{toml_cont[var]}"'
                if isinstance(toml_cont[var], list):
                    conf = f'self.{var} = {toml_cont[var]}'
                if isinstance(toml_cont[var], dict):
                    conf = f'self.{var} = {toml_cont[var]}'
                config_list.append(conf)
        return config_list

    def write_python_ci_test_config(self, config_list, temp_file: str, py_file: Path):
        my_template = Template(filename=temp_file)
        config_text = my_template.render(config_list=config_list)
        with  open(py_file, "w") as yml_tmp:
            yml_tmp.write(config_text.replace('\n', ''))
        print(f"Created file {py_file}.")


class Convert_types(object):

    def __init__(self):
        pass

    @staticmethod
    def convert_list_to_dict_toml(convert_list: list = None, wh_library: str = None):
        _dict = {}
        if convert_list is not None:
            for conv in convert_list:
                for lib in conv:
                    lib_dict = lib.split(":")
                    if lib_dict[0].find("wh_library") > -1 and wh_library is not None:
                        lib_dict[0] = lib_dict[0].replace("wh_library", wh_library)
                    lib_dict[1] = lib_dict[1].replace("os.getcwd()", os.getcwd())
                    full_path = lib_dict[1].split(",")
                    full_path = Path(full_path[0].strip(), full_path[1].strip())
                    _dict[lib_dict[0]] = full_path
            return _dict


class Pars:

    def __init__(self, args):
        self.args = args

    def main(self):
        parser = argparse.ArgumentParser(description="Write or load toml")
        check_test_group = parser.add_argument_group("Arguments to set config")
        # [ bool - flag]
        check_test_group.add_argument("--create-ci-test-config",
                                      default=False,
                                      action="store_true")
        check_test_group.add_argument("--create-ci-temp-config",
                                      default=False,
                                      action="store_true")
        args = parser.parse_args()
        return args


if __name__ == '__main__':
    arg = Pars(sys.argv[1:]).main()
    if arg.create_ci_test_config is True:
        to = toml_to_py()
        # todo: Anpassen der Pfade
        config = to.load_toml(toml_file=Path(Path.cwd(), "Modelica-CI" , "config", "toml_files", "ci_test_config.toml"))
        to.write_python_ci_test_config(config_list=config,
                                       temp_file=os.path.join(Path.cwd(), "Modelica-CI", "templates", "config_templates",
                                                              "ci_test_config.txt"),
                                       py_file=Path(Path.cwd(), "Modelica-CI", "ci_test_config.py"))
    if arg.create_ci_temp_config is True:
        to = toml_to_py()
        config = to.load_toml(toml_file=Path(Path.cwd(), "Modelica-CI", "gitlab_ci_templates", "ci_config", "toml_files",
                                             "ci_template_config.toml"))

        to.write_python_ci_test_config(config_list=config,
                                       temp_file=os.path.join(Path.cwd(),"Modelica-CI", "templates", "config_templates",
                                                              "ci_templates_config.txt"),
                                       py_file=Path(Path.cwd(),"Modelica-CI", "gitlab_ci_templates", "ci_templates_config.py"))
