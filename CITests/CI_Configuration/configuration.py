import os

class Config(object):

    def __init__(self):
        self.wh_file = f'dymola-ci-tests{os.sep}ci_whitelist{os.sep}model_whitelist.txt'
        self.ref_whitelist_file = f'dymola-ci-tests{os.sep}ci_whitelist{os.sep}reference_check_whitelist.txt'
        self.html_wh_file = f'dymola-ci-tests{os.sep}ci_whitelist{os.sep}html_whitelist.txt'
        self.show_ref_file = f'bin{os.sep}interact_CI{os.sep}show_ref.txt'
        self.update_ref_file = f'bin{os.sep}interact_CI{os.sep}update_ref.txt'
        self.chart_temp_file = f'dymola-ci-tests{os.sep}templates{os.sep}01_google_templates{os.sep}google_chart.txt'
        self.index_temp_file = f'dymola-ci-tests{os.sep}templates{os.sep}01_google_templates{os.sep}index.txt'
        self.layout_temp_file = f'dymola-ci-tests{os.sep}templates{os.sep}01_google_templates{os.sep}layout_index.txt'
        self.exit_file = f'dymola-ci-tests{os.sep}Configfiles{os.sep}exit.sh'
        self.ref_file = f'dymola-ci-tests{os.sep}Configfiles{os.sep}ci_reference_list.txt'
        self.ch_file = f'dymola-ci-tests{os.sep}Configfiles{os.sep}ci_changed_model_list.txt'
        self.new_ref_file = f'dymola-ci-tests{os.sep}Configfiles{os.sep}ci_new_created_reference.txt'

        self.artifacts_dir = f'dymola-ci-tests{os.sep}templates{os.sep}04_artifacts'
        self.chart_dir = f'dymola-ci-tests{os.sep}templates{os.sep}02_charts'  # path for layout index
        self.ref_file_dir = f'Resources{os.sep}ReferenceResults{os.sep}Dymola'
        self.resource_dir = f'Resources{os.sep}Scripts{os.sep}Dymola'

        # Color
        self.CRED = '\033[91m'  # Colors
        self.CEND = '\033[0m'
        self.green = '\033[0;32m'

    def test(self):
        return self.resource_dir

if __name__ == '__main__':
    conf = Config()
    conf.resource_dir

