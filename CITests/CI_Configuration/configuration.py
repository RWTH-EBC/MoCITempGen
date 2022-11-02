import os
import argparse

class CI_conf_class(object):

    def __init__(self):
        '''
        Dont change the self.<name>. But you can change the paths and file name
        '''
        self.dymola_ci_test_dir = f'dymola-ci-tests'
        # [Whitelist_files]
        self.wh_ci_dir = f'{self.dymola_ci_test_dir}{os.sep}ci_whitelist'
        self.wh_model_file = f'{self.wh_ci_dir}{os.sep}ci_model_whitelist.txt'
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
        self.chart_dir = f'{self.dymola_ci_test_dir}{os.sep}templates{os.sep}charts'
        self.temp_chart_dir = f'{self.dymola_ci_test_dir}{os.sep}templates{os.sep}google_templates'
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
        # [Color]
        self.CRED = '\033[91m'  # Colors
        self.CEND = '\033[0m'
        self.green = '\033[0;32m'

    def return_file_list(self):
        file_list = []
        file_dic = (vars(CI_conf_class()))
        for file in file_dic:
            if file.find("_file") > -1:
                file_list.append(file_dic[file])
        return file_list

    def return_file_dir(self):
        dir_list = []
        dir_dic = (vars(CI_conf_class()))
        for dir in dir_dic:
            if dir.find("_dir") > -1:
                dir_list.append(dir_dic[dir])
        return dir_list

    def _check_ci_folder_structure(self, folder_list):
        """
        Check CI Structure
        """
        for folder in folder_list:
            if not os.path.exists(folder):
                print(f'Create path: {folder}')
                os.makedirs(folder)
            else:
                print(f'Path "{folder}" exist.')

    def _check_ci_file_structure(self, file_list):
        for file in file_list:
            if os.path.exists(file):
                print(f'{file} does exist.')
            else:
                print(f'{file} does not exist. Create a new one under {file}')
                write_file = open(file, "w+")
                write_file.close()

    def _create_folder(self, path):
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

    conf = CI_conf_class()

    # conf.return_file_list()
