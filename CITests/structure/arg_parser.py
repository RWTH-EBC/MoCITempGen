import argparse
from pathlib import Path
import sys
from CI_test_config import CI_config
import tomli_w
import os
from mako.template import Template
import glob
import tomli_w as tomlwriter
import importlib.util
import inspect
import toml

class CI_templates_structure(CI_config):

    def __init__(self):
        super().__init__()
        self.toml_file = Path(Path.cwd(), "python_arg_config.toml")
        pass





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


def _load_parser_arg():
    # module = OM_Check
    # import f'{module}'
    pass


def write_toml():
    from CITests.UnitTests.OM_Check import Parser
    from CITests.UnitTests.CheckPackages.validatetest import Parser
    import OM_Check
    import validatetest
    module_list = [OM_Check.Parser, validatetest.Parser]
    config_list = []
    for module in module_list:
        config_list.append(module)
        args = module.main(sys.argv[1:])
        for arg in vars(args):
            config_list.append(f'{arg} = {getattr(args, arg)}')
    print(config_list)
    return config_list


class argpaser_toml(object):

    def __init__(self,
                 f_path: Path = Path("CITests"),
                 toml_file: Path = Path("config", "toml_files", "parser.toml")):
        self.f_path = f_path
        self.toml_file = toml_file
        pass

    def load_python_modules(self):
        py_f = glob.glob(f'{self.f_path }/**/*.py', recursive=True)
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
                            pars_arg_dict[args] = str(getattr(arguments, args))
                        class_modul_dict["Parser"] = pars_arg_dict
                        modul_dict[filename] = class_modul_dict
            except Exception as err:
                print(f"Error in file {file}: {err}")
                exit(1)
                continue
        return modul_dict


    def load_argparser_toml(self):
          try:
              data = toml.load(self.toml_file)
              return data
          except Exception as err:
              print(err)

    def write_python_parser_config(self):
        path_list = ["CITests.UnitTests.OM_Check", "CITests.UnitTests.CheckPackages.validatetest",
                     "CITests.UnitTests.reference_check"]
        modul_list = ["OM_Check", "validatetest", "reference_check"]
        toml_txt = os.path.join("templates", "config_templates", "parser_toml.txt")
        toml_file = os.path.join("templates", "config_templates", "parser.toml")
        python_parser_script = os.path.join("templates", "config_templates", "CI_parser_config.txt")
        my_template = Template(filename=python_parser_script)
        python_cont = my_template.render(path_list=path_list,
                                         modul_list=modul_list,
                                         toml_txt=toml_txt,
                                         toml_file=toml_file)
        yml_tmp = open(python_parser_script.replace(".txt", ".py"), "w")
        yml_tmp.write(python_cont.replace('\n', ''))
        yml_tmp.close()




class Pars:
    def __init__(self, args):
        self.args = args
        pass

    def main(self):
        parser = argparse.ArgumentParser(description="Write or load toml")
        check_test_group = parser.add_argument_group("Arguments to set config")
        # [ bool - flag]
        check_test_group.add_argument("--create-par-toml",
                                      default=False,
                                      action="store_true")
        check_test_group.add_argument("--read-par-toml",
                                      default=False,
                                      action="store_true")
        check_test_group.add_argument("--file-path",
                                      default=Path("CITests"))
        check_test_group.add_argument("--par-toml-file",
                                      default=Path("config", "toml_files", "parser.toml"))

        args = parser.parse_args()
        return args


if __name__ == '__main__':
    arg = Pars(sys.argv[1:]).main()

    # CI_struc = CI_templates_structure()
    # CI_struc.read_argparser_argument()
    # CI_struc.write_python_toml()
    # _load_parser_arg()
    # write_toml()
    # write_python_parser_config()
    to = argpaser_toml(f_path=arg.file_path,
                       toml_file=arg.par_toml_file)
    if arg.create_par_toml is True:

        python_files = to.load_python_modules()
        parser_dict = to.read_python_modules(module_files=python_files)

        to.write_toml_arg_parser(parser_dict=parser_dict)
    if arg.read_par_toml is True:
        to.load_argparser_toml()


