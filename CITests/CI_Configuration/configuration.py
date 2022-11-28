import os
import argparse

class CI_conf_class(object):

    def __init__(self):
        """
        Don't change the self.<name>. But you can change the paths and file name
        """
        self.dymola_ci_test_dir = f'dymola-ci-tests'
        self.dymola_python_test_dir = f'Dymola_python_tests'
        # [Whitelist_files]
        self.wh_ci_dir = f'{self.dymola_ci_test_dir}{os.sep}ci_whitelist'
        self.wh_model_file = f'{self.wh_ci_dir}{os.sep}ci_check_whitelist.txt'
        self.wh_simulate_file = f'{self.wh_ci_dir}{os.sep}ci_simulate_whitelist.txt'
        self.wh_html_file = f'{self.wh_ci_dir}{os.sep}ci_html_whitelist.txt'
        self.wh_ref_file = f'{self.wh_ci_dir}{os.sep}ci_reference_check_whitelist.txt'
        # [Config_files]
        self.config_ci_dir = f'{self.dymola_ci_test_dir}{os.sep}Configfiles'
        self.config_ci_exit_file = f'{self.config_ci_dir}{os.sep}exit.sh'
        self.config_ci_new_ref_file = f'{self.config_ci_dir}{os.sep}ci_new_ref_file.txt'
        self.config_ci_new_create_ref_file = f'{self.config_ci_dir}{os.sep}ci_new_created_reference.txt'
        self.config_ci_changed_file = f'{self.config_ci_dir}{os.sep}ci_changed_model_list.txt'
        self.config_ci_ref_file = f'{self.config_ci_dir}{os.sep}ci_reference_list.txt'
        self.config_ci_eof_file = f'{self.config_ci_dir}{os.sep}EOF.sh'
        # [templates for plots]
        self.chart_dir = f'{self.dymola_ci_test_dir}{os.sep}charts'
        self.temp_chart_dir = f'{self.dymola_python_test_dir}{os.sep}templates{os.sep}google_templates'
        self.temp_chart_file = f'{self.temp_chart_dir}{os.sep}google_chart.txt'
        self.temp_index_file = f'{self.temp_chart_dir}{os.sep}index.txt'
        self.temp_layout_file = f'{self.temp_chart_dir}{os.sep}layout_index.txt'
        # [interact ci lists]
        self.ci_interact_dir = f'{self.dymola_ci_test_dir}{os.sep}interact_CI'
        self.ci_interact_show_ref_file = f'{self.ci_interact_dir}{os.sep}show_ref.txt'
        self.ci_interact_update_ref_file = f'{self.ci_interact_dir}{os.sep}update_ref.txt'
        # [Folder]
        self.artifacts_dir = f'{self.dymola_ci_test_dir}{os.sep}templates{os.sep}artifacts'
        self.library_ref_results_dir = f'Resources{os.sep}ReferenceResults{os.sep}Dymola'
        self.library_resource_dir = f'Resources{os.sep}Scripts{os.sep}Dymola'
        # [Dymola_Python_Tests] + Parser Commands
        self.dymola_python_test_url = f'https://$CI_TEST_Name:$CI_TEST_TOKEN@git.rwth-aachen.de/EBC/EBC_all/gitlab_ci/Dymola_python_tests.git'
        # [Color]
        self.CRED = '\033[91m'  # Colors
        self.CEND = '\033[0m'
        self.green = '\033[0;32m'

    @staticmethod
    def return_file_list():
        files_list = []
        file_dic = (vars(CI_conf_class()))
        for file in file_dic:
            if file.find("_file") > -1:
                files_list.append(file_dic[file])
        return files_list

    @staticmethod
    def return_file_dir():
        dir_list = []
        dir_dic = (vars(CI_conf_class()))
        for dirs in dir_dic:
            if dirs.find("_dir") > -1:
                dir_list.append(dir_dic[dirs])
        return dir_list

    @staticmethod
    def check_ci_folder_structure(folders_list):
        """
        Check CI Structure
        """
        for folder in folders_list:
            if not os.path.exists(folder):
                print(f'Create path: {folder}')
                os.makedirs(folder)
            else:
                print(f'Path "{folder}" exist.')


    def check_ci_file_structure(self, files_list):
        for file in files_list:
            if os.path.exists(file):
                print(f'{file} does exist.')
            else:
                print(f'File {file} does not exist. Create a new one under {file}')
                write_file = open(file, "w+")
                if file is self.config_ci_eof_file:
                    write_file.write(f'y\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\n')
                write_file.close()

    @staticmethod
    def create_folder(path):
        try:
            if not os.path.exists(path):
                print(f'Create path: {path}')
                os.makedirs(path)
            else:
                print(f'Path "{path}" exist.')
        except FileExistsError:
            print(f'Find no folder')
            pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Set files or dictionaries")
    check_test_group = parser.add_argument_group("Arguments to build files or folders")
    check_test_group.add_argument("-CM", "--changed-model", default=False, action="store_true")
    check_test_group.add_argument("--ci-interactive", default=False, action="store_true")
    check_test_group.add_argument("--create-ref", default=False, action="store_true")

    args = parser.parse_args()
    conf = CI_conf_class()
    folder_list = []
    file_list = []
    if args.changed_model is True:
        folder_list = [conf.config_ci_dir]
        file_list = [conf.config_ci_changed_file]
        pass
    if args.ci_interactive is True:
        folder_list = [conf.config_ci_dir]
        file_list = [conf.config_ci_eof_file, conf.config_ci_changed_file]
        pass
    if args.create_ref is True:
        folder_list = [conf.config_ci_dir]
        file_list = [conf.config_ci_eof_file, conf.config_ci_exit_file, conf.config_ci_new_create_ref_file]
        pass
    conf.check_ci_folder_structure(folders_list=folder_list)
    conf.check_ci_file_structure(files_list=file_list)
