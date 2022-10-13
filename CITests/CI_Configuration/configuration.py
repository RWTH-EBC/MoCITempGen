import os

class CI_conf_class(object):

    def __init__(self):
        '''
        Dont change the self.<name>. But you can change the paths and file name
        '''
        # Files
        self.ci_dir = f'dymola-ci-tests'

        self.wh_model_file = f'{self.ci_dir}{os.sep}ci_whitelist{os.sep}model_whitelist.txt'
        self.ref_whitelist_file = f'{self.ci_dir}{os.sep}ci_whitelist{os.sep}reference_check_whitelist.txt'
        self.wh_html_file = f'{self.ci_dir}{os.sep}ci_whitelist{os.sep}html_whitelist.txt'

        self.show_ref_file = f'{self.ci_dir}{os.sep}interact_CI{os.sep}show_ref.txt'
        self.update_ref_file = f'{self.ci_dir}{os.sep}interact_CI{os.sep}update_ref.txt'

        self.chart_temp_file = f'{self.ci_dir}{os.sep}templates{os.sep}google_templates{os.sep}google_chart.txt'
        self.index_temp_file = f'{self.ci_dir}{os.sep}templates{os.sep}google_templates{os.sep}index.txt'
        self.layout_temp_file = f'{self.ci_dir}{os.sep}templates{os.sep}google_templates{os.sep}layout_index.txt'

        self.exit_file = f'{self.ci_dir}{os.sep}Configfiles{os.sep}exit.sh'
        self.ref_file = f'{self.ci_dir}{os.sep}Configfiles{os.sep}ci_reference_list.txt'
        self.ch_file = f'{self.ci_dir}{os.sep}Configfiles{os.sep}ci_changed_model_list.txt'
        self.new_ref_file = f'{self.ci_dir}{os.sep}Configfiles{os.sep}ci_new_created_reference.txt'

        # Folders
        self.ci_whitelist_dir = f'{self.ci_dir}{os.sep}ci_whitelist'
        self.interact_ci_dir = f'{self.ci_dir}{os.sep}interact_CI'
        self.config_dir = f'{self.ci_dir}{os.sep}Configfiles'
        self.chart_temp_dir = f'{self.ci_dir}{os.sep}templates{os.sep}google_templates'
        self.artifacts_dir = f'{self.ci_dir}{os.sep}templates{os.sep}artifacts'
        self.chart_dir = f'{self.ci_dir}{os.sep}templates{os.sep}charts'  # path for layout index
        self.ref_results_dir = f'Resources{os.sep}ReferenceResults{os.sep}Dymola'
        self.resource_dir = f'Resources{os.sep}Scripts{os.sep}Dymola'

        # Color
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



if __name__ == '__main__':
    conf = CI_conf_class()
    conf.return_file_list()

