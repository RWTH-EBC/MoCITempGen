import argparse
from pathlib import Path
import sys
from ci_test_config import ci_config
from gitlab_ci_templates.ci_templates_config import ci_template_config
import os
from mako.template import Template
import glob
import tomli_w as tomlwriter
import importlib.util
import inspect
import toml


class CI_templates_structure(ci_config):

    def __init__(self):
        super().__init__()
        self.toml_file = Path(Path.cwd(), "python_arg_config.toml")

class StoreDictKeyPair(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        self._nargs = nargs
        super(StoreDictKeyPair, self).__init__(option_strings, dest, nargs=nargs, **kwargs)

    def __call__(self, pars, namespace, values, option_string=None):
        my_dict = {}
        for kv in values:
            k, v = kv.split(":")
            if v == "":
                v = os.getcwd()
            else:
                v = Path(os.getcwd(), v)
            my_dict[k] = v
        setattr(namespace, self.dest, my_dict)


class StoreDictKeyPair_list(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        self._nargs = nargs
        super(StoreDictKeyPair_list, self).__init__(option_strings, dest, nargs=nargs, **kwargs)

    def __call__(self, pars, namespace, values, option_string=None):
        my_dict = {}
        for kv in values:
            k, v = kv.split(":")
            my_dict[k] = v.split(",")
        setattr(namespace, self.dest, my_dict)


class StoreDictKey(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        self._nargs = nargs
        super(StoreDictKey, self).__init__(option_strings, dest, nargs=nargs, **kwargs)

    def __call__(self, pars, namespace, values, option_string=None):
        my_dict = {}
        if values is not None:
            for kv in values:
                k, v = kv.split(":")
                my_dict[k] = v.split(",")
            setattr(namespace, self.dest, my_dict)
        else:
            return None

class argpaser_toml(ci_template_config):

    def __init__(self,
                 f_path: str = os.path.join("Modelica-GitLab-CI", "ci_tests"),
                 toml_file: str = os.path.join("Modelica-GitLab-CI", "gitlab_ci_templates", "ci_config", "toml_files", "parser.toml")):
        super().__init__()
        self.f_path = f_path
        self.toml_file = Path(self.dymola_python_test_dir, "gitlab_ci_templates", "ci_config", "toml_files", "parser.toml")
        pass

    def load_python_modules(self):
        py_f = glob.glob(f'{self.f_path}/**/*.py', recursive=True)
        mo_py_files = []
        for file in py_f:
            if file.find("__init__.py") == -1:
                mo_py_files.append(file)
        return mo_py_files

    def write_toml_arg_parser(self,
                              parser_dict: dict = None):
        if parser_dict is not None:
            with open(self.toml_file, "wb") as f:
                tomlwriter.dump(parser_dict, f)
            print(f"Write toml in {self.toml_file}")
        else:
            print("No toml content.")


    def overwrite_parser_toml(self, parser_data):
        """data = toml.load(self.toml_file)
        for parser in parser_dict:
            #data[file]["Parser"][parser_arg] = overwrite_arg
            data[file]["Parser"][parser] = parser_dict[parser]"""
        f = open(self.toml_file, 'w')
        toml.dump(parser_data, f)
        f.close()
        print(f"Overwrite of toml file {self.toml_file} successful")

    def read_python_modules(self, module_files):
        modul_dict = {}
        for files in module_files:
            file = Path(files)
            filename = file.name.replace(file.suffix, "")
            spec = importlib.util.spec_from_file_location(filename, file)
            foo = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(foo)
                for name, obj in inspect.getmembers(foo):
                    if inspect.isclass(obj) and name == "Parser":
                        pars_arg_dict = {}
                        class_modul_dict = {}
                        #arguments = obj.main(sys.argv[1:])
                        sys.argv[1:] = []
                        arguments = obj.main([])
                        for args in vars(arguments):
                            if getattr(arguments, args) is None or isinstance(getattr(arguments, args), Path):
                                pars_arg_dict[args] = str(getattr(arguments, args))
                            else:
                                pars_arg_dict[args] = getattr(arguments, args)
                        class_modul_dict["Parser"] = pars_arg_dict
                        modul_dict[filename] = class_modul_dict
            except Exception as err:
                print(f"Error in file {file}: {err}")
                #exit(1)
                continue
        return modul_dict


    def load_argparser_toml(self):
        data = toml.load(self.toml_file)
        return data





class Pars:
    def __init__(self, args):
        self.args = args
        pass

    def main(self):
        parser = argparse.ArgumentParser(description="Write or load toml")
        check_test_group = parser.add_argument_group("Arguments to set config")
        # [ bool - flag]
        check_test_group.add_argument("--write-parse-toml",
                                      default=False,
                                      action="store_true")
        check_test_group.add_argument("--read-parse-toml",
                                      default=False,
                                      action="store_true")
        check_test_group.add_argument("--overwrite-parse-toml",
                                      default=False,
                                      action="store_true")
        check_test_group.add_argument("--file-path",
                                      default=os.path.join("Dymola_python_tests", "ci_tests"))
        check_test_group.add_argument("--parse-toml-file",
                                      default=os.path.join("Dymola_python_tests", "gitlab_ci_templates", "ci_config", "toml_files", "parser.toml"))
        check_test_group.add_argument("--python-file",
                                      default="api_github")
        check_test_group.add_argument("--parser-arg",
                                      default="correct_branch")
        check_test_group.add_argument("--over_arg",
                                      default="test")

        args = parser.parse_args()
        return args


if __name__ == '__main__':
    arg = Pars(sys.argv[1:]).main()
    to = argpaser_toml(f_path=arg.file_path,
                       toml_file=arg.parse_toml_file)
    if arg.write_parse_toml is True:
        python_files = to.load_python_modules()
        parser_dict = to.read_python_modules(module_files=python_files)
        to.write_toml_arg_parser(parser_dict=parser_dict)
    if arg.read_parse_toml is True:
        to.load_argparser_toml()
    if arg.overwrite_parse_toml is True:
        parser_data = to.overwrite_argparser_toml()
        to.overwrite_parser_toml(parser_data=parser_data)



