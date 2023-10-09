import os
import sys
from pathlib import Path

MoCITempGenPATH = Path(__file__).parents[1]
sys.path.append(str(MoCITempGenPATH.joinpath("CITests", "CI_Configuration")))

# TODO: Don't use this CI_conf_class structure. Use some correct dataclasses (e.g. pydantic, dataclasses, o.s.) instead
from configuration import CI_conf_class


class CI_template_config(CI_conf_class):

    def __init__(self):
        """

        """
        super().__init__()
        # [CI non fixed Arguments]
        self.gitlab_page = f'https://ebc.pages.rwth-aachen.de/EBC_all/github_ci/AixLib'
        self.image_name = f'registry.git.rwth-aachen.de/ebc/ebc_intern/dymola-docker:Dymola_2022-miniconda'
        self.github_repo = f'RWTH-EBC/AixLib'
        self.wh_library = f'IBPSA'  # TODO: Use extensive names, e.g. whitelist_library?!
        self.html_praefix = f'correct_HTML_'  # TODO: Fix typos
        self.expire_in_time = f'7h'  # TODO: Structure/Separate special settings for gitlab and important settings
        self.library = 'AixLib'
        self.dymola_version = f'2022'
        self.python_version = f'myenv'
        self.git_url = f'https://github.com/ibpsa/modelica-ibpsa.git'
        # [CI fixed arguments]
        self.bot_name = f'ebc-aixlib-bot'
        # [Except branches]
        self.except_branch_list = ['main']
        # [Stages]
        self.ci_stage_check_setting = f'check_setting'
        self.ci_stage_build_templates = f'build_templates'
        self.ci_stage_ref_check = f'Ref_Check'
        self.ci_stage_lib_merge = f'{self.wh_library}_merge'
        self.ci_stage_html_whitelist = f'create_html_whitelist'
        self.ci_stage_create_whitelist = f'create_model_whitelist'
        self.ci_stage_create_example_whitelist = f'create_example_whitelist'
        self.ci_stage_html_check = f'HTML_Check'
        self.ci_stage_style_check = f'Style_check'
        self.ci_stage_model_check = f'model_check'
        self.ci_stage_simulate = f'simulate'
        self.ci_stage_regression_test = f'RegressionTest'
        #self.ci_stage_update_ref = f'Update_Ref'
        self.ci_stage_plot_ref = f'plot_ref'
        self.ci_stage_prepare = f'prepare'
        self.ci_stage_open_PR = f'open_PR'
        self.ci_stage_update_whitelist = f'update_whiteList'
        self.ci_stage_build_ci_structure = f'build_ci_structure'
        self.ci_stage_deploy = f'deploy'
        self.ci_stage_whitelist_setting = f'build_ci_whitelist'
        # [Buildingspy upgrade url]
        self.buildingspy_upgrade = f'git+https://github.com/MichaMans/BuildingsPy@testexamplescoverage'
        # [CI_Setting]
        # TODO: Use pathlib, much more robust and readable
        self.ci_template_python_directory = MoCITempGenPATH.joinpath("CI_templates_python")
        self.temp_toml_ci_setting_file = self.ci_template_python_directory.joinpath("Setting", "CI_setting_template.txt")
        self.toml_ci_setting_file = self.ci_template_python_directory.joinpath("Setting", "CI_setting.toml")
        # [CI_Templates_file]
        self.templates_ci_directory = MoCITempGenPATH.joinpath("templates", "ci_templates")
        self.temp_ci_regression_file = self.templates_ci_directory.joinpath("UnitTests", "regression_test.txt")
        self.temp_ci_check_file = self.templates_ci_directory.joinpath("UnitTests", "check_model.txt")
        self.temp_ci_simulate_file = self.templates_ci_directory.joinpath("UnitTests", "simulate_model.txt")
        self.temp_ci_page_file = self.templates_ci_directory.joinpath("deploy", "gitlab_pages.txt")
        self.temp_ci_ibpsa_merge_file = self.templates_ci_directory.joinpath("deploy", "IBPSA_Merge.txt")
        self.temp_ci_html_file = self.templates_ci_directory.joinpath("syntaxtest", "html_check.txt")
        self.temp_ci_style_check_file = self.templates_ci_directory.joinpath("syntaxtest", "style_check.txt")
        self.temp_ci_structure_file = self.templates_ci_directory.joinpath("deploy", "create_CI_path.txt")
        self.temp_ci_main_yml_file = self.templates_ci_directory.joinpath(".gitlab-ci.txt")
        self.temp_ci_setting_file = self.templates_ci_directory.joinpath("cleanupscript", "ci_setting.txt")
        self.temp_ci_deploy_test_file = self.templates_ci_directory.joinpath("deploy", "deploy_ci_tests.txt")
        self.temp_ci_build_whitelist_file = self.templates_ci_directory.joinpath("cleanupscript", "ci_build_whitelist.txt")
        # [Created CI_template_folder]
        # TODO: Remove redundant lines
        #self.temp_dir = f'Dymola_python_tests{os.sep}gitlab_ci_templates'
        self.temp_dir = f'dymola-ci-tests{os.sep}ci_templates'
        # [Dymola test scripts]
        self.xvfb_flag = f'xvfb-run -n 77'
        self.dymola_python_dir = MoCITempGenPATH.joinpath("CITests")
        self.dymola_python_test_validate_file = self.dymola_python_dir.joinpath("UnitTests", "CheckPackages", "validatetest.py")
        self.dymola_python_test_reference_file = self.dymola_python_dir.joinpath("UnitTests", "reference_check.py")
        self.dymola_python_google_chart_file = self.dymola_python_dir.joinpath("Converter", "google_charts.py")
        self.dymola_python_api_github_file = self.dymola_python_dir.joinpath("api_script", "api_github.py")
        self.dymola_python_deploy_artifacts_file = self.dymola_python_dir.joinpath("deploy", "deploy_artifacts.py")
        self.dymola_python_html_tidy_file = self.dymola_python_dir.joinpath("SyntaxTests", "html_tidy_errors.py")
        self.dymola_python_syntax_test_file = self.dymola_python_dir.joinpath("SyntaxTests", "StyleChecking.py")
        self.dymola_python_configuration_file = self.dymola_python_dir.joinpath("CI_Configuration", "configuration.py")
        # TODO: Make these into separate structures with a TOML like: "interact-ci".
        # [Triggers different jobs specifically: Interact CI: User]
        #self.ci_update_ref_commit = "ci_update_ref"                 # Update reference results from list
        self.ci_show_ref_commit = "ci_show_ref"                     # show reference results from list
        #self.ci_dif_ref_commit = "ci_dif_ref"                       # Show difference in reference results
        self.ci_create_model_wh_commit = "ci_create_model_wh"       # create a whitelist with models that failed the check job
        self.ci_create_html_wh_commit = "ci_create_html_wh"         # create a whitelist with models that should not go through the html check
        self.ci_create_simulate_wh_commit = "ci_create_example_wh"  # create a whitelist with models that failed the simulate job
        self.ci_simulate_commit = "ci_simulate"                     # trigger only to simulate job
        self.ci_check_commit = "ci_check"                           # trigger only the check job
        self.ci_regression_test_commit = "ci_regression_test"       # trigger only the regression job
        self.ci_html_commit = "ci_html"                             # trigger only the html job
        self.ci_setting_commit = "ci_setting"                       # trigger only the setting job
        self.ci_style_commit = "ci_style_check"                     # trigger only the style check job
        self.ci_trigger_ibpsa_commit = "ci_trigger_ibpsa"           # trigger only the (IBPSA)-merge job
        self.ci_merge_except_commit = "ci_merge_except"
        self.ci_correct_html_commit = "ci_correct_html"
        self.ci_build_structure_commit = "ci_build_structure"
        self.ci_build_whitelist_structure_commit = "ci_build_whitelist"
        # [Commits from CI bot: Does not matter for the user, only ci_bot messages]
        self.bot_merge_commit = f'CI message from {self.bot_name}. Merge of {self.wh_library} library. Update files {self.wh_model_file} and {self.wh_html_file}'
        self.bot_push_commit = f'CI message from {self.bot_name}. Automatic push of CI with new regression reference files. Please pull the new files before push again.'
        self.bot_create_ref_message = f'CI message from {self.bot_name}. New reference files were pushed to this branch. The job was successfully and the newly added files are tested in another commit.'
        self.bot_update_wh_commit = f'CI message from {self.bot_name}. Update or created new whitelist. Please pull the new whitelist before push again.'
        self.bot_create_ref_commit = f'CI message from {self.bot_name}. Automatic push of CI with new regression reference files.Please pull the new files before push again. Plottet Results $GITLAB_Page/$CI_COMMIT_REF_NAME/plots/'
        self.bot_create_CI_template_commit = f'CI message from {self.bot_name}. Automatic push of CI with new created CI templates. Please pull the new files before push again.'
        self.bot_update_model_wh_commit = f'CI message from {self.bot_name}. Update file {self.wh_model_file}. Please pull the new files before push again.'
        self.bot_update_example_wh_commit = f'CI message from {self.bot_name}. Update file {self.wh_simulate_file}. Please pull the new files before push again.'
        self.bot_create_structure_commit = f'CI message from {self.bot_name}. Add files for ci structure'
        self.bot_create_html_file_commit = f'CI message from {self.bot_name}. Push new files with corrected html Syntax .'
        self.bot_build_whitelist_commit = f'CI message from {self.bot_name}. Push new created whitelists.'
        # [Colors]
        self.CRED = '\033[91m'
        self.CEND = '\033[0m'
        self.green = '\033[0;32m'


    # TODO: Don't use staticmethods for classes, just plain methods are enough
    # TODO: If using one dataclass for all except commits, it's much cleaner.
    @staticmethod
    def create_except_commit_list():
        except_commit_list = []
        except_commit_dic = (vars(CI_template_config()))
        for commit in except_commit_dic:
            if commit.find("ci_") > -1 and commit.find("_commit") > -1:
                except_commit_list.append(except_commit_dic[commit])
        return except_commit_list

    def _create_except_branches(self):
        pass  # TODO: Remove redundant

    @staticmethod
    def _create_stage_list():
        stage_list = []
        stage_dic = (vars(CI_template_config()))
        for stage in stage_dic:
            if stage.find("_stage_") > -1:
                stage_list.append(stage_dic[stage])
        return stage_list
