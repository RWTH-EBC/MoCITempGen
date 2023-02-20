#/bin/bash
import argparse
import os
import pathlib
import shutil
import toml
import inspect
import re
import fnmatch
from pathlib import Path

class CI_config(object):

    def __init__(self):
        """
        Don't change the self.<name>. But you can change the paths and file name
        [Whitelist_files]
        [Config_files]
        [templates for plots]
        [interact ci lists]
        [Folder]
        [Dymola_Python_Tests] + Parser Commands
        """
        toml_files = sorted(pathlib.Path('.').glob('**/**/config.toml'))
        toml_file = f'Dymola_python_tests{os.sep}config.toml'
        if len(toml_files) > 0:
            for l in toml_files:
                toml_file = l
                break
        else:
            toml_file = f'..{os.sep}Dymola_python_tests{os.sep}config.toml'
        data = toml.load(f'{toml_file}')
        self.dymola_ci_test_dir = data["CI_dir"]["dymola_ci_test_dir"].replace("/", os.sep)
        self.dymola_python_test_dir = data["CI_dir"]["dymola_python_test_dir"].replace("/", os.sep)
        # [Whitelist_files]
        self.wh_ci_dir = f'{data["whitelist"]["wh_ci_dir"].replace("/", os.sep)}'
        self.wh_model_file = f'{data["whitelist"]["wh_model_file"].replace("/", os.sep)}'
        self.wh_simulate_file = f'{data["whitelist"]["wh_simulate_file"].replace("/", os.sep)}'
        self.wh_html_file = f'{data["whitelist"]["wh_html_file"].replace("/", os.sep)}'
        self.wh_ref_file = f'{data["whitelist"]["wh_ref_file"].replace("/", os.sep)}'
        # [Config_files]
        self.config_ci_dir = f'{data["config_ci"]["config_ci_dir"].replace("/", os.sep)}'
        self.config_ci_exit_file = f'{data["config_ci"]["config_ci_exit_file"].replace("/", os.sep)}'
        self.config_ci_new_ref_file = f'{data["config_ci"]["config_ci_new_ref_file"].replace("/", os.sep)}'
        self.config_ci_new_create_ref_file = f'{data["config_ci"]["config_ci_new_create_ref_file"].replace("/", os.sep)}'
        self.config_ci_changed_file = f'{data["config_ci"]["config_ci_changed_file"].replace("/", os.sep)}'
        self.config_ci_ref_file = f'{data["config_ci"]["config_ci_ref_file"].replace("/", os.sep)}'
        self.config_ci_eof_file = f'{data["config_ci"]["config_ci_eof_file"].replace("/", os.sep)}'
        # [templates for plots]
        self.chart_dir = f'{data["plot"]["chart_dir"].replace("/", os.sep)}'
        self.temp_chart_dir = f'{data["plot"]["temp_chart_dir"].replace("/", os.sep)}'
        self.temp_chart_file = f'{data["plot"]["temp_chart_file"].replace("/", os.sep)}'
        self.temp_index_file = f'{data["plot"]["temp_index_file"].replace("/", os.sep)}'
        self.temp_layout_file = f'{data["plot"]["temp_layout_file"].replace("/", os.sep)}'
        # [interact ci lists]
        self.ci_interact_dir = f'{data["interact_ci_list"]["ci_interact_dir"].replace("/", os.sep)}'
        self.ci_interact_show_ref_file = f'{data["interact_ci_list"]["ci_interact_show_ref_file"].replace("/", os.sep)}'
        self.ci_interact_update_ref_file = f'{data["interact_ci_list"]["ci_interact_update_ref_file"].replace("/", os.sep)}'
        # [Folder]
        self.artifacts_dir = f'{data["artifcats"]["artifacts_dir"].replace("/", os.sep)}'
        self.library_ref_results_dir = f'{data["artifcats"]["library_ref_results_dir"].replace("/", os.sep)}'
        self.library_resource_dir = f'{data["artifcats"]["library_resource_dir"].replace("/", os.sep)}'
        # [Dymola_Python_Tests]
        self.dymola_python_test_url = f'{data["Dymola_Python_Tests"]["dymola_python_test_url"]}'
        # [result folder]
        self.result_dir = f'{data["result"]["result_dir"].replace("/", os.sep)}'
        self.result_whitelist_dir = f'{data["result"]["result_whitelist_dir"].replace("/", os.sep)}'
        self.result_config_dir = f'{data["result"]["result_config_dir"].replace("/", os.sep)}'
        self.result_plot_dir = f'{data["result"]["result_plot_dir"].replace("/", os.sep)}'
        self.result_syntax_dir = f'{data["result"]["result_syntax_dir"].replace("/", os.sep)}'
        self.result_regression_dir = f'{data["result"]["result_regression_dir"].replace("/", os.sep)}'
        self.result_interact_ci_dir = f'{data["result"]["result_interact_ci_dir"].replace("/", os.sep)}'
        self.result_ci_template_dir = f'{data["result"]["result_ci_template_dir"].replace("/", os.sep)}'
        self.result_check_result_dir = f'{data["result"]["result_check_result_dir"].replace("/", os.sep)}'
        self.result_OM_check_result_dir = f'{data["result"]["result_OM_check_result_dir"].replace("/", os.sep)}'
        # [Color]
        self.CRED = '\033[91m'
        self.CEND = '\033[0m'
        self.green = '\033[0;32m'
        self.yellow = '\033[33m'
        self.blue = '\033[44m'


    # *********** Checking structure *******************
    def check_arguments_settings(self, *args):
        frame = inspect.currentframe().f_back
        s = inspect.getframeinfo(frame).code_context[0]
        r = re.search(r"\((.*)\)", s).group(1)
        var_names = r.split(", ")
        print(f'***--- Argument setting---****')
        for i, (var, val) in enumerate(zip(var_names, args)):
            if val is None:
                print(f'{self.CRED}Error:{self.CEND} {self.blue}Variable "{var}"{self.CEND} has value {self.CRED}"{val}". "{var}"{self.CEND} is not set!')
                print(f'***------****')
                exit(1)
            else:
                print(f'{self.green}Setting:{self.CEND} {self.blue}Variable "{var}" {self.CEND} is set as: {self.blue}"{val}"{self.CEND}')
        print(f'***------****')

    def check_path_setting(self, *args: Path):
        frame = inspect.currentframe().f_back
        s = inspect.getframeinfo(frame).code_context[0]
        r = re.search(r"\((.*)\)", s).group(1)
        var_names = r.split(", ")
        print(f'***--- Check path setting---****')
        for i, (var, path) in enumerate(zip(var_names, args)):
            if os.path.isdir(path) is True:
                print(f'{self.green}Setting:{self.CEND} {self.blue}Path_variable "{var}"{self.CEND} is set as: {self.blue}"{path}"{self.CEND} and exists.')
            else:
                print(f'{self.CRED}Error:{self.CEND} {self.blue}Path_variable "{var}"{self.CEND} in {self.blue}"{path}"{self.CEND} does not exist.')
                print(f'***------****')
                exit(1)
        print(f'***------****')

    def check_file_setting(self, *args):
        frame = inspect.currentframe().f_back
        s = inspect.getframeinfo(frame).code_context[0]
        r = re.search(r"\((.*)\)", s).group(1)
        var_names = r.split(", ")
        print(f'***--- Check file setting---****')
        for i, (var, file) in enumerate(zip(var_names, args)):
            if os.path.isfile(file) is True:
                print(f'{self.green}Setting:{self.CEND} {self.blue}File "{var}"{self.CEND} is set as: {self.blue}"{file}"{self.CEND} and exists.')
            else:
                print(f'{self.CRED}Error:{self.CEND} {self.blue}File_variable "{var}"{self.CEND} in {self.blue}"{file}"{self.CEND} does not exist.')
                print(f'***------****')
                exit(1)
        print(f'***------****')

    ############# Create Structure ##############
    def create_path(self, path_list: list = None):
        if path_list is not None:
            print(f'\n**** Create folder ****\n')
            for path in path_list:
                print(f'{self.green}Create Folder:{self.CEND} {path}')
                os.makedirs(path, exist_ok=True)
            print(f'\n**** ----------- ****\n')

    def create_files(self, files_list: list = None):
        """
        Args:
            files_list ():
        """
        if folder_list is not None:
            print(f'\n**** Create file structure ****\n')
            for file in files_list:
                if os.path.exists(file):
                    print(f'{file} does exist.')
                else:
                    print(f'File {file} does not exist. Create a new one under {self.green}{file}{self.CEND}')
                    write_file = open(file, "w+")
                    if file is self.config_ci_eof_file:
                        write_file.write(f'y\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\n')
                    write_file.close()
            print(f'\n**********************\n')



    ############# Remove Structure ##############
    def delete_files_in_path(self, path_list: list = None):
        if path_list is not None:
            print(f'\n**** Delete folder ****\n')
            for path in path_list:
                print(f'{self.green}Delete files:{self.CEND} {path}')
                for filename in os.listdir(path):
                    file_path = os.path.join(path, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        print('Failed to delete %s. Reason: %s' % (file_path, e))
            print(f'\n**** ----------- ****\n')

    def delete_spec_file(self, root: str = None, pattern: str = None):
        if root is not None and pattern is not None:
            for filename in os.listdir(root):
                file = os.path.join(root, filename)
                if os.path.isfile(file) and filename.find(pattern) > -1:
                    os.remove(file)

    @staticmethod
    def remove_files(file_list: list = None):
        if file_list is not None:
            for file in file_list:
                if os.path.exists(file):
                    if os.path.isfile(file) is True:
                        os.remove(file)
                        print(f'Remove file: {file}')
                    else:
                        print(f'File {file} does not exist')


    def remove_path(self, path_list: list = None):
        if path_list is not None:
            for path in path_list:
                if os.path.isdir(path) is True:
                    os.rmdir(path)
                    print(f'Remove folder: {path}')
                else:
                    print(f'Path {path} does not exist.')

    ############# Prepare Result ##############

    def prepare_data(self,
                     source_target_dict: dict = None,
                     del_flag: bool = False):
        """
            Args:
            file_path_dict (): {dst:src,}
            del_flag (): True: delete file, False dont delete file
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
                    print(f'Result Folder {self.blue}{source}{self.CEND} was moved to {self.blue}{target_path}{self.CEND}')
                    shutil.copytree(source, target_path)
                    if del_flag is True:
                        self.remove_path([source])
        print(f'{self.blue}**********************{self.CEND}\n')


    # *******************************
    @staticmethod
    def return_file_list():
        """
        Returns:
        """
        files_list = []
        file_dic = (vars(CI_config()))
        for file in file_dic:
            if file.find("_file") > -1:
                files_list.append(file_dic[file])
        return files_list

    @staticmethod
    def return_file_dir():
        dir_list = []
        dir_dic = (vars(CI_config()))
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
    conf = CI_config()
    folder_list = list()
    file_list = list()
    if args.changed_model is True:
        folder_list = [conf.config_ci_dir]
        file_list = [conf.config_ci_changed_file, conf.config_ci_exit_file]
        pass
    if args.ci_interactive is True:
        folder_list = [conf.config_ci_dir]
        file_list = [conf.config_ci_eof_file, conf.config_ci_changed_file]
        pass
    if args.create_ref is True:
        folder_list = [conf.config_ci_dir]
        file_list = [conf.config_ci_eof_file, conf.config_ci_exit_file, conf.config_ci_new_create_ref_file]
        pass
    if args.create_whitelist is True:
        folder_list = [conf.dymola_ci_test_dir, conf.wh_ci_dir]
        file_list = [conf.wh_model_file, conf.wh_simulate_file, conf.wh_html_file, conf.wh_ref_file]
        pass
    conf.create_path(path_list=folder_list)
    conf.create_files(files_list=file_list)
    """check_log = os.path.join(os.path.abspath("."), "AixLib", "AixLib.Airflow-check_log.txt")
    err_log = os.path.join(os.path.abspath("."), "AixLib", "AixLib.Airflow-error_log.txt")
    conf.prepare_data(source_target_dict={
        check_log: os.path.join(conf.result_OM_check_result_dir, "AixLib.Airflow"),
        err_log: os.path.join(conf.result_OM_check_result_dir,  "AixLib.Airflow")}, del_flag=True)
    """