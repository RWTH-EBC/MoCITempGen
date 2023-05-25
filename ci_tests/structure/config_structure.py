from ci_test_config import ci_config
import inspect
import re
import os
import shutil
import glob
from pathlib import Path
import argparse
import distutils.dir_util

class data_structure(ci_config):

    def __init__(self):
        """

        """
        super().__init__()

    def check_arguments_settings(self, *args):
        """
        Checking structure
        Args:
            *args ():
        """
        frame = inspect.currentframe().f_back
        s = inspect.getframeinfo(frame).code_context[0]
        r = re.search(r"check_arguments_settings\((.*)\)", s).group(1)
        var_names = r.split(",")
        print(f'*** --- Argument setting --- ****')
        for i, (var, val) in enumerate(zip(var_names, args)):
            if val is None:
                print(f'{self.CRED}Error:{self.CEND} {self.blue}Variable "{var.strip()}"{self.CEND} has value '
                      f'{self.CRED}"{val}". "{var}"{self.CEND} is not set!')
                exit(1)
            else:
                print(f'{self.green}Setting:{self.CEND} {self.blue}Variable "{var.strip()}" {self.CEND} is set as: '
                      f'{self.blue}"{val}"{self.CEND}')

    def check_path_setting(self,  *args: Path, create_flag: bool = False):
        """

        Args:
            *args ():
            create_flag ():
        """
        frame = inspect.currentframe().f_back
        s = inspect.getframeinfo(frame).code_context[0]
        r = re.search(r"\((.*)\)", s).group(1)
        var_names = r.split(", ")
        print(f'*** --- Check path setting --- ****')
        for i, (var, path) in enumerate(zip(var_names, args)):
            if os.path.isdir(path) is True:
                print(f'{self.green}Setting:{self.CEND} {self.blue}Path variable "{var}"{self.CEND} is set as: '
                      f'{self.blue}"{path}"{self.CEND} and exists.')
            else:
                print(f'{self.CRED}Error:{self.CEND} {self.blue}Path variable "{var}"{self.CEND} in {self.blue}"{path}"'
                      f'{self.CEND} does not exist.')
                """if var == "self.wh_ci_dir":
                    print(f"If filter_wh_flag is True, a file must be stored under {path}.")
                    exit(1)"""
                if create_flag is True:
                    self.create_path(path)
                else:
                    exit(1)

    def check_file_setting(self, *args, create_flag: bool = False):
        """

        Args:
            *args ():
            create_flag ():
        """
        frame = inspect.currentframe().f_back
        s = inspect.getframeinfo(frame).code_context[0]
        r = re.search(r"\((.*)\)", s).group(1)
        var_names = r.split(", ")
        print(f'*** --- Check file setting --- ****')
        for i, (var, file) in enumerate(zip(var_names, args)):
            if os.path.isfile(file) is True:
                print(f'{self.green}Setting:{self.CEND} {self.blue}File "{var}"{self.CEND} is set as: '
                      f'{self.blue}"{file}"{self.CEND} and exists.')
            else:
                print(f'{self.CRED}Error:{self.CEND} {self.blue}File_variable "{var}"{self.CEND} in {self.blue}"{file}"'
                      f'{self.CEND} does not exist.')
                if create_flag is True:
                    self.create_files(file)
                else:
                    exit(1)

    def create_path(self, *args: Path):
        """
        Create Structure
        Args:
            *args ():
        """
        print(f'\n**** Create folder ****')
        for arg in args:
            print(f'{self.green}Create Folder:{self.CEND} {arg}')
            os.makedirs(arg, exist_ok=True)

    def create_files(self, *args: Path):
        """
        Args:
            files_list ():
        """
        for file in args:
            if os.path.exists(file):
                print(f'{self.green}File:{self.CEND} {file} does exist.')
            else:
                print(f'{self.CRED}File: {self.CEND}  {file} does not exist. Create a new one under {self.green}{file}{self.CEND}')
                with open(file, 'w') as write_file:
                    if os.path.basename(file) == os.path.basename(self.config_ci_eof_file):
                        write_file.write(f'y\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\n')

    def delete_files_in_path(self, *args: Path):
            """
            Remove Structure
            Args:
                *args ():
            """
            print(f'\n**** Delete folder ****\n')
            for arg in args:
                print(f'{self.green}Delete files:{self.CEND} {arg}')
                for filename in os.listdir(arg):
                    file_path = os.path.join(arg, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        print('Failed to delete %s. Reason: %s' % (file_path, e))

    @staticmethod
    def delete_spec_file(root: str = None, pattern: str = None):
        """

        Args:
            root ():
            pattern ():
        """
        if root is not None and pattern is not None:
            for filename in os.listdir(root):
                file = os.path.join(root, filename)
                if os.path.isfile(file) and filename.find(pattern) > -1:
                    os.remove(file)

    @staticmethod
    def delete_files_path(root: str = None, pattern: str = None, subfolder: bool = False):
        """

        Args:
            root ():
            pattern ():
            subfolder ():
        """
        if subfolder is True:
            files = glob.glob(f'{root}/**/*{pattern}', recursive=True)
        else:
            files = glob.glob(f'{root}/**/*{pattern}')
        print(f'Remove files path {root} with {pattern}')
        for file in files:
            os.remove(file)

    @staticmethod
    def remove_files(file_list: list = None):
        """

        Args:
            file_list ():
        """
        if file_list is not None:
            for file in file_list:
                if os.path.exists(file):
                    if os.path.isfile(file) is True:
                        os.remove(file)
                        print(f'Remove file: {file}')
                    else:
                        print(f'File {file} does not exist')

    @staticmethod
    def remove_path(path_list: list = None):
        """

        Args:
            path_list ():
        """
        if path_list is not None:
            for path in path_list:
                if os.path.isdir(path) is True:
                    os.rmdir(path)
                    print(f'Remove folder: {path}')
                else:
                    print(f'Path {path} does not exist.')

    def prepare_data(self,
                     source_target_dict: dict = None,
                     del_flag: bool = False):
        """
        Prepare Result:
            Args:
            file_path_dict (): {dst:src}
            del_flag (): True: delete files if True, dont delete files if False
        """
        print(f'\n{self.blue}**** Prepare Data ****{self.CEND}')
        if source_target_dict is not None:
            for source in source_target_dict:
                target_path = source_target_dict[source]
                if not os.path.exists(target_path):
                    print(f'Create path: {target_path}')
                    os.makedirs(target_path)
                if os.path.isfile(source) is True:
                    path, file_name = os.path.split(source)
                    target = os.path.join(target_path, file_name)
                    print(f'Result file {self.blue}{source}{self.CEND} was moved to {self.blue}{target}{self.CEND}')
                    shutil.copyfile(source, target)
                    if del_flag is True:
                        self.remove_files([source])
                if os.path.isdir(source) is True:
                    print(
                        f'Result Folder {self.blue}{source}{self.CEND} was moved to {self.blue}{target_path}{self.CEND}')
                    distutils.dir_util.copy_tree(source, str(target_path))
                    if del_flag is True:
                        self.remove_path([source])

    @staticmethod
    def return_file_list():
        """
        Returns:
        """
        files_list = []
        file_dic = (vars(ci_config()))
        for file in file_dic:
            if file.find("_file") > -1:
                files_list.append(file_dic[file])
        return files_list

    @staticmethod
    def return_file_dir():
        """

        Returns:

        """
        dir_list = []
        dir_dic = (vars(ci_config()))
        for dirs in dir_dic:
            if dirs.find("_dir") > -1:
                dir_list.append(dir_dic[dirs])
        return dir_list

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Set files or dictionaries")
    check_test_group = parser.add_argument_group("Arguments to build files or folders")
    check_test_group.add_argument("-CM", "--changed-model", default=False, action="store_true")
    check_test_group.add_argument("--ci-interactive", default=False, action="store_true")
    check_test_group.add_argument("--create-ref", default=False, action="store_true")
    check_test_group.add_argument("--create-whitelist", default=False, action="store_true")

    args = parser.parse_args()
    conf = ci_config()
    folder_list = []
    file_list = []
    if args.changed_model is True:
        data_structure().create_path(Path(conf.config_ci_dir))
        data_structure().create_files(Path(conf.config_ci_changed_file), Path(conf.config_ci_exit_file))
        pass
    if args.ci_interactive is True:
        data_structure().create_path(Path(conf.config_ci_dir))
        data_structure().create_files(Path(conf.config_ci_eof_file), Path(conf.config_ci_changed_file))
        pass
    if args.create_ref is True:
        data_structure().create_path(Path(conf.config_ci_dir))
        data_structure().create_files(Path(conf.config_ci_eof_file), Path(conf.config_ci_exit_file), Path(conf.config_ci_new_create_ref_file))
        pass
    if args.create_whitelist is True:
        data_structure().create_path(Path(conf.dymola_ci_test_dir), Path(conf.wh_ci_dir))
        data_structure().create_files(Path(conf.wh_model_file), Path(conf.wh_simulate_file), Path(conf.wh_html_file), Path(conf.wh_ref_file))
        pass

