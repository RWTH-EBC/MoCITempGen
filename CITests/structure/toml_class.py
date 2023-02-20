from CI_test_config import CI_config
import toml
import os
from mako.template import Template
from pathlib import Path


class toml_class(CI_config):

    def __init__(self):
        super(toml_class, self).__init__()
        self.config_toml_file = Path(Path.cwd(), "Dymola_python_tests", "config.toml")
        self.config_file = os.path.join(Path.cwd(), "templates", "config_templates", "CITest_config.txt")
        self.config_python_file = os.path.join(Path.cwd(), "CITest_config2.py")


    def load_toml(self):
        data = toml.load(self.config_toml_file)
        config_list = []
        for d in data:
            toml_cont = data[d]
            docu = f"# [{d}]"
            config_list.append(docu)
            for var in toml_cont:
                conf = f'self.{var} = "{toml_cont[var]}"'
                config_list.append(conf)
        return config_list

    def write_python_CI_test_config(self, config_list):
        my_template = Template(filename=self.config_file)
        config_text = my_template.render(config_list=config_list)
        yml_tmp = open(self.config_python_file, "w")
        yml_tmp.write(config_text.replace('\n', ''))
        yml_tmp.close()




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


if __name__ == '__main__':
    to = toml_class()
    config = to.load_toml()
    to.write_python_CI_test_config(config_list=config)
