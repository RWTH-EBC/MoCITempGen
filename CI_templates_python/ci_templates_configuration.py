import os
from Dymola_python_tests.CI_test_config import CI_config
import toml
class CI_template_config(CI_config):

    def __init__(self):
        """
         ci_update_ref_commit                # Update reference results from list
        ci_show_ref_commit                   # show reference results from list
        ci_dif_ref_commit                    # Show difference in reference results
        ci_create_model_wh_commit            # create a whitelist with models that failed the check job
        ci_create_html_wh_commit             # create a whitelist with models that should not go through the html check
        ci_create_simulate_wh_commit         # create a whitelist with models that failed the simulate job
        ci_simulate_commit                   # trigger only to simulate job
        ci_check_commit                      # trigger only the check job
        ci_regression_test_commit            # trigger only the regression job
        ci_html_commit                       # trigger only the html job
        ci_setting_commit                    # trigger only the setting job
        ci_style_commit                      # trigger only the style check job
        ci_trigger_ibpsa_commit              # trigger only the (IBPSA)-merge job
        ci_merge_except_commit
        ci_correct_html_commit
        ci_build_structure_commit
        ci_build_whitelist_structure_commit

        """
        super().__init__()
        data = toml.load(f'Dymola_python_tests/CI_templates_python/ci_template_config.toml')

        # [CI non fixed Arguments]
        self.gitlab_page = data['arguments']['gitlab_page']
        self.image_name = data['arguments']['image_name']
        self.github_repo = data['arguments']['github_repo']
        self.wh_library = data['arguments']['wh_library']
        self.html_praefix = data['arguments']['html_praefix']
        self.expire_in_time = data['arguments']['expire_in_time']
        self.library = data['arguments']['library']
        self.dymola_version = data['arguments']['dymola_version']
        self.python_version = data['arguments']['python_version']
        self.git_url = data['arguments']['git_url']

        # [CI fixed arguments]
        self.bot_name = data['ci_fixed_arguments']['bot_name']
        self.xvfb_flag = data['ci_fixed_arguments']['xvfb_flag']

        # [Except branches]
        self.except_branch_list = data['except_branches']['except_branch_list']

        # [Stages]
        self.ci_stage_check_setting = data['ci_stages']['ci_stage_check_setting']
        self.ci_stage_build_templates = data['ci_stages']['ci_stage_build_templates']
        self.ci_stage_ref_check = data['ci_stages']['ci_stage_ref_check']
        self.ci_stage_lib_merge = f'{self.wh_library}_{data["ci_stages"]["ci_stage_lib_merge"]}'
        self.ci_stage_html_whitelist = data['ci_stages']['ci_stage_html_whitelist']
        self.ci_stage_create_whitelist = data['ci_stages']['ci_stage_create_whitelist']
        self.ci_stage_create_example_whitelist = data['ci_stages']['ci_stage_create_example_whitelist']
        self.ci_stage_html_check = data['ci_stages']['ci_stage_html_check']
        self.ci_stage_style_check = data['ci_stages']['ci_stage_style_check']
        self.ci_stage_model_check = data['ci_stages']['ci_stage_model_check']
        self.ci_stage_simulate = data['ci_stages']['ci_stage_simulate']
        self.ci_stage_regression_test = data['ci_stages']['ci_stage_regression_test']
        self.ci_stage_update_ref = data['ci_stages']['ci_stage_update_ref']
        self.ci_stage_plot_ref = data['ci_stages']['ci_stage_plot_ref']
        self.ci_stage_prepare = data['ci_stages']['ci_stage_prepare']
        self.ci_stage_open_PR = data['ci_stages']['ci_stage_open_PR']
        self.ci_stage_update_whitelist = data['ci_stages']['ci_stage_update_whitelist']
        self.ci_stage_build_ci_structure = data['ci_stages']['ci_stage_build_ci_structure']
        self.ci_stage_deploy = data['ci_stages']['ci_stage_deploy']
        self.ci_stage_whitelist_setting = data['ci_stages']['ci_stage_whitelist_setting']
        self.ci_stage_OM_model_check = data['ci_stages']['ci_stage_OM_model_check']
        self.ci_stage_OM_simulate = data['ci_stages']['ci_stage_OM_simulate']

        # [Buildingspy upgrade url]
        self.buildingspy_upgrade = data['Buildingspy_upgrade_url']['buildingspy_upgrade']

        # [CI_Setting]
        self.temp_ci_template_dir = f'{self.dymola_python_test_dir}{os.sep}{data["ci_setting"]["temp_ci_template_dir"].replace("/", os.sep)}'
        self.temp_toml_ci_setting_file = f'{self.temp_ci_template_dir}{os.sep}{data["ci_setting"]["temp_toml_ci_setting_file"].replace("/", os.sep)}'
        self.toml_ci_setting_file = f'{self.temp_ci_template_dir}{os.sep}{data["ci_setting"]["toml_ci_setting_file"].replace("/", os.sep)}'

        # [CI_Templates_file]
        self.temp_ci_dir = f'{data["ci_templates_file"]["temp_ci_dir"]}'
        self.temp_ci_regression_file = f'{data["ci_templates_file"]["temp_ci_regression_file"].replace("/", os.sep)}'
        self.temp_ci_check_file = f'{data["ci_templates_file"]["temp_ci_check_file"].replace("/", os.sep)}'
        self.temp_ci_simulate_file = f'{data["ci_templates_file"]["temp_ci_simulate_file"].replace("/", os.sep)}'
        self.temp_ci_page_file = f'{data["ci_templates_file"]["temp_ci_page_file"].replace("/", os.sep)}'
        self.temp_ci_ibpsa_merge_file = f'{data["ci_templates_file"]["temp_ci_ibpsa_merge_file"].replace("/", os.sep)}'
        self.temp_ci_html_file = f'{data["ci_templates_file"]["temp_ci_html_file"].replace("/", os.sep)}'
        self.temp_ci_style_check_file = f'{data["ci_templates_file"]["temp_ci_style_check_file"].replace("/", os.sep)}'
        self.temp_ci_structure_file = f'{data["ci_templates_file"]["temp_ci_structure_file"].replace("/", os.sep)}'
        self.temp_ci_main_yml_file = f'{data["ci_templates_file"]["temp_ci_main_yml_file"].replace("/", os.sep)}'
        self.temp_ci_setting_file = f'{data["ci_templates_file"]["temp_ci_setting_file"].replace("/", os.sep)}'
        self.temp_ci_deploy_test_file = f'{data["ci_templates_file"]["temp_ci_deploy_test_file"].replace("/", os.sep)}'
        self.temp_ci_build_whitelist_file = f'{data["ci_templates_file"]["temp_ci_build_whitelist_file"].replace("/", os.sep)}'
        self.temp_ci_OM_check_file = f'{data["ci_templates_file"]["temp_ci_OM_check_file"].replace("/", os.sep)}'
        self.temp_ci_OM_simulate_file = f'{data["ci_templates_file"]["temp_ci_OM_simulate_file"].replace("/", os.sep)}'
        # [Created CI_template_folder]
        self.temp_dir = f'{data["ci_template_folder"]["temp_dir"].replace("/", os.sep)}'

        # [Dymola test scripts]
        self.dymola_python_dir = f'{data["dymola_python_scripts"]["dymola_python_dir"].replace("/", os.sep)}'
        self.dymola_python_test_validate_file = f'{self.dymola_python_dir}{os.sep}{data["dymola_python_scripts"]["dymola_python_test_validate_file"].replace("/", os.sep)}'
        self.dymola_python_test_reference_file = f'..{os.sep}{self.dymola_python_dir}{os.sep}{data["dymola_python_scripts"]["dymola_python_test_reference_file"].replace("/", os.sep)}'
        self.dymola_python_google_chart_file = f'{self.dymola_python_dir}{os.sep}{data["dymola_python_scripts"]["dymola_python_google_chart_file"].replace("/", os.sep)}'
        self.dymola_python_api_github_file = f'{self.dymola_python_dir}{os.sep}{data["dymola_python_scripts"]["dymola_python_api_github_file"].replace("/", os.sep)}'
        self.dymola_python_deploy_artifacts_file = f'{self.dymola_python_dir}{os.sep}{data["dymola_python_scripts"]["dymola_python_deploy_artifacts_file"].replace("/", os.sep)}'
        self.dymola_python_html_tidy_file = f'{self.dymola_python_dir}{os.sep}{data["dymola_python_scripts"]["dymola_python_html_tidy_file"].replace("/", os.sep)}'
        self.dymola_python_syntax_test_file = f'{self.dymola_python_dir}{os.sep}{data["dymola_python_scripts"]["dymola_python_syntax_test_file"].replace("/", os.sep)}'
        self.dymola_python_configuration_file = f'{data["dymola_python_scripts"]["dymola_python_configuration_file"].replace("/", os.sep)}'

        # [Triggers different jobs specifically: Interact CI: User]
        self.ci_update_ref_commit = data["interactive_ci_commit"]["ci_update_ref_commit"]
        self.ci_show_ref_commit = data["interactive_ci_commit"]["ci_show_ref_commit"]
        self.ci_dif_ref_commit = data["interactive_ci_commit"]["ci_dif_ref_commit"]
        self.ci_create_model_wh_commit = data["interactive_ci_commit"]["ci_create_model_wh_commit"]
        self.ci_create_html_wh_commit = data["interactive_ci_commit"]["ci_create_html_wh_commit"]
        self.ci_create_simulate_wh_commit = data["interactive_ci_commit"]["ci_create_simulate_wh_commit"]
        self.ci_simulate_commit = data["interactive_ci_commit"]["ci_simulate_commit"]
        self.ci_OM_simulate_commit = data["interactive_ci_commit"]["ci_OM_simulate_commit"]

        self.ci_check_commit = data["interactive_ci_commit"]["ci_check_commit"]
        self.ci_OM_check_commit = data["interactive_ci_commit"]["ci_OM_check_commit"]

        self.ci_regression_test_commit = data["interactive_ci_commit"]["ci_regression_test_commit"]
        self.ci_html_commit = data["interactive_ci_commit"]["ci_html_commit"]
        self.ci_setting_commit = data["interactive_ci_commit"]["ci_setting_commit"]
        self.ci_style_commit = data["interactive_ci_commit"]["ci_style_commit"]
        self.ci_trigger_ibpsa_commit = data["interactive_ci_commit"]["ci_trigger_ibpsa_commit"]
        self.ci_merge_except_commit = data["interactive_ci_commit"]["ci_merge_except_commit"]
        self.ci_correct_html_commit = data["interactive_ci_commit"]["ci_correct_html_commit"]
        self.ci_build_structure_commit = data["interactive_ci_commit"]["ci_build_structure_commit"]
        self.ci_build_whitelist_structure_commit = data["interactive_ci_commit"]["ci_build_whitelist_structure_commit"]

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




    @staticmethod
    def create_except_commit_list():
        except_commit_list = []
        except_commit_dic = (vars(CI_template_config()))
        for commit in except_commit_dic:
            if commit.find("ci_") > -1 and commit.find("_commit") > -1:
                except_commit_list.append(except_commit_dic[commit])
        return except_commit_list

    def _create_except_branches(self):
        pass

    @staticmethod
    def _create_stage_list():
        stage_list = []
        stage_dic = (vars(CI_template_config()))
        for stage in stage_dic:
            if stage.find("_stage_") > -1:
                stage_list.append(stage_dic[stage])
        return stage_list
