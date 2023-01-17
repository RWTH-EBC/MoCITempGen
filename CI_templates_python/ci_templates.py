import os
from mako.template import Template
import argparse
import toml
from ci_templates_configuration import CI_template_config


class CI_yml_templates(CI_template_config):

    def __init__(self, library, package_list, dymola_version, wh_library, git_url, wh_path, python_version, github_repo,
                 image_name, gitlab_page):
        super().__init__()
        self.except_commit_list = CI_template_config().create_except_commit_list()
        self.stage_list = CI_template_config()._create_stage_list()
        self.library = library
        self.package_list = package_list
        self.dymola_version = dymola_version
        self.wh_library = wh_library
        self.git_url = git_url
        self.wh_path = wh_path
        self.python_version = python_version
        self.merge_branch = f'{self.wh_library}_Merge'
        self.github_repo = github_repo
        self.image_name = image_name
        self.gitlab_page = gitlab_page
        self.variable_main_list = [f'Github_Repository: {self.github_repo}', f'GITLAB_Page: {self.gitlab_page}']

    def _write_ci_structure_template(self):
        """

        """
        my_template = Template(filename=self.temp_ci_structure_file)
        yml_text = my_template.render(ci_stage_build_ci_structure=self.ci_stage_build_ci_structure,
                                      python_version=self.python_version,
                                      dymola_python_test_url=self.dymola_python_test_url,
                                      bot_create_structure_commit=self.bot_create_structure_commit,
                                      ci_build_structure_commit=self.ci_build_structure_commit,
                                      wh_model_file=self.wh_model_file,
                                      wh_html_file=self.wh_html_file,
                                      wh_ref_file=self.wh_ref_file,
                                      ci_interact_show_ref_file=self.ci_interact_show_ref_file,
                                      ci_interact_update_ref_file=self.ci_interact_update_ref_file,
                                      expire_in_time=self.expire_in_time,
                                      dymola_python_dir=self.dymola_python_dir.replace(os.sep, "/"))
        ci_folder = f'{self.temp_dir}{os.sep}{self.temp_ci_structure_file.split(os.sep)[-2]}'
        self.check_ci_folder_structure([ci_folder])
        yml_file = f'{ci_folder}{os.sep}{self.temp_ci_structure_file.split(os.sep)[-1]}'
        yml_tmp = open(yml_file.replace(".txt", ".gitlab-ci.yml"), "w")
        yml_tmp.write(yml_text.replace('\n', ''))
        yml_tmp.close()

    '''
    def _write_dymola_ci_temp(self):
        mytemplate = Template(filename=self.dymola_ci_temp_file)
        yml_text = mytemplate.render()
        yml_file = f'{self.temp_dir}{os.sep}{self.dymola_ci_temp_file.split(os.sep)[-2]}{os.sep}{self.self.dymola_ci_temp_file.split(os.sep)[-1]}'
        yml_tmp = open(yml_file.replace(".txt", ".gitlab-ci.yml"), "w")
        yml_tmp.write(yml_text)
        yml_tmp.close()
    '''

    def _write_page_template(self):
        """
        Write page template, deploy artifacts, plots, reference results
        """
        my_template = Template(filename=self.temp_ci_page_file)
        yml_text = my_template.render(ci_stage_deploy=self.ci_stage_deploy,
                                      expire_in_time=self.expire_in_time,
                                      except_branch_list=self.except_branch_list,
                                      dymola_python_dir=self.dymola_python_dir.replace(os.sep, "/"),
                                      result_dir=self.result_dir.replace(os.sep, "/"))
        ci_folder = f'{self.temp_dir}{os.sep}{self.temp_ci_page_file.split(os.sep)[-2]}'
        self.check_ci_folder_structure([ci_folder])
        yml_file = f'{ci_folder}{os.sep}{self.temp_ci_page_file.split(os.sep)[-1]}'
        yml_tmp = open(yml_file.replace(".txt", ".gitlab-ci.yml"), "w")
        yml_tmp.write(yml_text.replace('\n', ''))
        yml_tmp.close()

    def _write_setting_template(self):
        """
        Write setting template, create template with own Syntax
        """
        my_template = Template(filename=self.temp_ci_setting_file)
        yml_text = my_template.render(github_repo=self.github_repo,
                                      ci_setting_commit=self.ci_setting_commit,
                                      python_version=self.python_version,
                                      ci_stage_check_setting=self.ci_stage_check_setting,
                                      ci_stage_build_templates=self.ci_stage_build_templates,
                                      bot_create_CI_template_commit=self.bot_create_CI_template_commit,
                                      temp_dir=self.temp_dir,
                                      dymola_python_test_url=self.dymola_python_test_url,
                                      dymola_python_dir=self.dymola_python_dir.replace(os.sep, "/"))
        ci_folder = f'{self.temp_dir}{os.sep}{self.temp_ci_setting_file.split(os.sep)[-2]}'
        print(ci_folder)
        print(self.temp_ci_setting_file.split(os.sep)[-2])
        self.check_ci_folder_structure([ci_folder])
        yml_file = f'{ci_folder}{os.sep}{self.temp_ci_setting_file.split(os.sep)[-1]}'
        print(yml_file)
        yml_tmp = open(yml_file.replace(".txt", ".gitlab-ci.yml"), "w")
        yml_tmp.write(yml_text.replace('\n', ''))
        yml_tmp.close()

    def _write_html_template(self):
        """
         Write HTML template
        """
        if self.wh_library is not None:
            merge_branch = f'- {self.wh_library}_Merge'
            git = f'--git-url {self.git_url} --wh-library {self.wh_library}'
        else:
            git = ""
            merge_branch = ""
        my_template = Template(filename=self.temp_ci_html_file)
        yml_text = my_template.render(ci_stage_html_check=self.ci_stage_html_check,
                                      ci_stage_html_whitelist=self.ci_stage_html_whitelist,
                                      ci_stage_open_PR=self.ci_stage_open_PR,
                                      python_version=self.python_version,
                                      dymola_python_test_url=self.dymola_python_test_url,
                                      config_ci_exit_file=self.config_ci_exit_file.replace(os.sep, "/"),
                                      ci_correct_html_commit=self.ci_correct_html_commit,
                                      library=self.library,
                                      except_commit_list=self.except_commit_list,
                                      except_branch_list=self.except_branch_list,
                                      html_praefix=self.html_praefix,
                                      merge_branch=merge_branch,
                                      ci_html_commit=self.ci_html_commit,
                                      git=git,
                                      bot_update_wh_commit=self.bot_update_wh_commit,
                                      wh_html_file=self.wh_html_file.replace(os.sep, "/"),
                                      ci_create_html_wh_commit=self.ci_create_html_wh_commit,
                                      dymola_python_html_tidy_file=self.dymola_python_html_tidy_file.replace(os.sep,
                                                                                                             "/"),
                                      dymola_python_api_github_file=self.dymola_python_api_github_file.replace(os.sep,
                                                                                                               "/"),
                                      bot_create_html_file_commit=self.bot_create_html_file_commit,
                                      expire_in_time=self.expire_in_time,
                                      result_dir=self.result_dir.replace(os.sep, "/"),
                                      dymola_python_dir=self.dymola_python_dir.replace(os.sep, "/"))
        ci_folder = f'{self.temp_dir}{os.sep}{self.temp_ci_html_file.split(os.sep)[-2]}'
        self.check_ci_folder_structure([ci_folder])
        yml_file = f'{ci_folder}{os.sep}{self.temp_ci_html_file.split(os.sep)[-1]}'
        yml_tmp = open(yml_file.replace(".txt", ".gitlab-ci.yml"), "w")
        yml_tmp.write(yml_text.replace('\n', ''))
        yml_tmp.close()

    def _write_style_template(self):
        """
        Write Style Check template
        """
        merge_branch = f'- {self.wh_library}_Merge'
        mytemplate = Template(filename=self.temp_ci_style_check_file)
        yml_text = mytemplate.render(ci_stage_style_check=self.ci_stage_style_check,
                                     python_version=self.python_version,
                                     dymola_python_test_url=self.dymola_python_test_url,
                                     dymola_version=self.dymola_version,
                                     library=self.library,
                                     except_commit_list=self.except_commit_list,
                                     except_branch_list=self.except_branch_list,
                                     config_ci_changed_file=self.config_ci_changed_file.replace(os.sep, "/"),
                                     merge_branch=merge_branch,
                                     expire_in_time=self.expire_in_time,
                                     xvfb_flag=self.xvfb_flag,
                                     ci_style_commit=self.ci_style_commit,
                                     dymola_python_syntax_test_file=self.dymola_python_syntax_test_file.replace(os.sep,
                                                                                                                "/"),
                                     dymola_python_configuration_file=self.dymola_python_configuration_file.replace(
                                         os.sep, "/"),
                                     html_praefix=self.html_praefix,
                                     result_dir=self.result_dir.replace(os.sep, "/"),
                                     dymola_python_dir=self.dymola_python_dir.replace(os.sep, "/"))
        ci_folder = f'{self.temp_dir}{os.sep}{self.temp_ci_style_check_file.split(os.sep)[-2]}'
        self.check_ci_folder_structure([ci_folder])
        yml_file = f'{ci_folder}{os.sep}{self.temp_ci_style_check_file.split(os.sep)[-1]}'
        yml_tmp = open(yml_file.replace(".txt", ".gitlab-ci.yml"), "w")
        yml_tmp.write(yml_text.replace('\n', ''))
        yml_tmp.close()

    def _write_CI_Whitelist_Setting_template(self):
        """

        """
        if self.wh_library is not None:
            wh_library = self.wh_library
            filter_flag = "--filter-whitelist"
            wh_flag = "--wh-library " + self.wh_library
            merge_branch = f'- {self.wh_library}_Merge'
            if self.wh_path is not None:
                wh_path = "--wh-path " + self.wh_path
                git_url = ""
            elif self.git_url is not None:
                git_url = "--git-url " + self.git_url
                wh_path = ""
            else:
                wh_path = ""
                git_url = ""
        else:
            wh_library = self.library
            wh_flag = ""
            git_url = ""
            filter_flag = ""
            wh_path = ""
            merge_branch = ""

        my_template = Template(filename=self.temp_ci_build_whitelist_file)
        yml_text = my_template.render(ci_stage_whitelist_setting=self.ci_stage_whitelist_setting,
                                      python_version=self.python_version,
                                      dymola_python_test_url=self.dymola_python_test_url,
                                      dymola_python_configuration_file=self.dymola_python_configuration_file.replace(os.sep, "/"),
                                      dymola_python_test_validate_file=self.dymola_python_test_validate_file.replace(os.sep, "/"),
                                      dymola_version=self.dymola_version,
                                      git_url=git_url,
                                      library=self.library,
                                      bot_build_whitelist_commit=self.bot_build_whitelist_commit,
                                      dymola_ci_test_dir=self.dymola_ci_test_dir,
                                      ci_build_whitelist_structure_commit=self.ci_build_whitelist_structure_commit,
                                      expire_in_time=self.expire_in_time,
                                      xvfb_flag=self.xvfb_flag,
                                      wh_library=wh_library,
                                      wh_path=wh_path,
                                      dymola_python_dir=self.dymola_python_dir.replace(os.sep, "/"))

        ci_folder = f'{self.temp_dir}{os.sep}{self.temp_ci_build_whitelist_file.split(os.sep)[-2]}'
        self.check_ci_folder_structure([ci_folder])
        yml_file = f'{ci_folder}{os.sep}{self.temp_ci_build_whitelist_file.split(os.sep)[-1]}'
        yml_tmp = open(yml_file.replace(".txt", ".gitlab-ci.yml"), "w")
        yml_tmp.write(yml_text.replace('\n', ''))
        yml_tmp.close()

    def _write_merge_template(self):
        """
        Write (IBPSA) Merge template
        """
        merge_branch = f'{self.wh_library}_Merge'
        my_template = Template(filename=self.temp_ci_ibpsa_merge_file)
        yml_text = my_template.render(ci_stage_lib_merge=self.ci_stage_lib_merge,
                                      ci_stage_update_whitelist=self.ci_stage_update_whitelist,
                                      ci_stage_open_PR=self.ci_stage_open_PR,
                                      python_version=self.python_version,
                                      dymola_python_test_url=self.dymola_python_test_url,
                                      merge_branch=merge_branch,
                                      git_url=self.git_url,
                                      library=self.library,
                                      ci_trigger_ibpsa_commit=self.ci_trigger_ibpsa_commit,
                                      expire_in_time=self.expire_in_time,
                                      dymola_version=self.dymola_version,
                                      wh_library=self.wh_library,
                                      bot_merge_commit=self.bot_merge_commit,
                                      wh_model_file=self.wh_model_file,
                                      xvfb_flag=self.xvfb_flag,
                                      dymola_python_test_validate_file=self.dymola_python_test_validate_file.replace(
                                          os.sep, "/"),
                                      dymola_python_dir=self.dymola_python_dir.replace(os.sep, "/"))
        ci_folder = f'{self.temp_dir}{os.sep}{self.temp_ci_ibpsa_merge_file.split(os.sep)[-2]}'
        self.check_ci_folder_structure([ci_folder])
        yml_file = f'{ci_folder}{os.sep}{self.temp_ci_ibpsa_merge_file.split(os.sep)[-1]}'
        yml_tmp = open(yml_file.replace(".txt", ".gitlab-ci.yml"), "w")
        yml_tmp.write(yml_text.replace('\n', ''))
        yml_tmp.close()

    def _write_regression_template(self):
        if self.merge_branch is not None:
            merge_branch = f'- {self.wh_library}_Merge'
        else:
            merge_branch = ""
        mytemplate = Template(filename=self.temp_ci_regression_file)
        yml_text = mytemplate.render(ci_stage_regression_test=self.ci_stage_regression_test,
                                     ci_stage_ref_check=self.ci_stage_ref_check,
                                     ci_stage_plot_ref=self.ci_stage_plot_ref,
                                     ci_stage_prepare=self.ci_stage_prepare,
                                     python_version=self.python_version,
                                     buildingspy_upgrade=self.buildingspy_upgrade,
                                     config_ci_exit_file=self.config_ci_exit_file.replace(os.sep, "/"),
                                     dymola_python_test_url=self.dymola_python_test_url,
                                     library=self.library,
                                     dymola_version=self.dymola_version,
                                     chart_dir=self.chart_dir.replace(os.sep, "/"),
                                     package_list=self.package_list,
                                     ci_regression_test_commit=self.ci_regression_test_commit,
                                     expire_in_time=self.expire_in_time,
                                     except_branch_list=self.except_branch_list,
                                     except_commit_list=self.except_commit_list,
                                     config_ci_changed_file=self.config_ci_changed_file.replace(os.sep, "/"),
                                     merge_branch=merge_branch,
                                     config_ci_eof_file=self.config_ci_eof_file.replace(os.sep, "/"),
                                     bot_create_ref_commit=self.bot_create_ref_commit,
                                     config_ci_new_create_ref_file=self.config_ci_new_create_ref_file.replace(os.sep,
                                                                                                              "/"),
                                     xvfb_flag=self.xvfb_flag,
                                     ci_show_ref_commit=self.ci_show_ref_commit,
                                     dymola_python_test_reference_file=self.dymola_python_test_reference_file.replace(
                                         os.sep, "/"),
                                     dymola_python_google_chart_file=self.dymola_python_google_chart_file.replace(
                                         os.sep, "/"),
                                     dymola_python_deploy_artifacts_file=self.dymola_python_deploy_artifacts_file.replace(
                                         os.sep, "/"),
                                     dymola_python_api_github_file=self.dymola_python_api_github_file.replace(os.sep,
                                                                                                              "/"),
                                     dymola_python_configuration_file=self.dymola_python_configuration_file.replace(
                                         os.sep, "/"),
                                     html_praefix=self.html_praefix,
                                     result_dir=self.result_dir.replace(os.sep,  "/"),
                                     dymola_python_dir=self.dymola_python_dir.replace(os.sep, "/")
                                     )
        ci_folder = f'{self.temp_dir}{os.sep}{self.temp_ci_regression_file.split(os.sep)[-2]}'
        self.check_ci_folder_structure([ci_folder])
        yml_file = f'{ci_folder}{os.sep}{self.temp_ci_regression_file.split(os.sep)[-1]}'
        yml_tmp = open(yml_file.replace(".txt", ".gitlab-ci.yml"), "w")
        yml_tmp.write(yml_text.replace('\n', ''))
        yml_tmp.close()


    def _write_OM_simulate_template(self):
        if self.wh_library is not None:
            filter_flag = "--filter-whitelist"
            wh_flag = "--wh-library " + self.wh_library
            merge_branch = "- " + self.merge_branch
            if self.wh_path is not None:
                wh_path = "--wh-path " + self.wh_path
                git_url = ""
            elif self.git_url is not None:
                git_url = "--git-url " + self.git_url
                wh_path = ""
            else:
                wh_path = ""
                git_url = ""
        else:
            merge_branch = ""
            filter_flag = ""
            wh_flag = ""
            wh_path = ""
            git_url = ""
        my_template = Template(filename=self.temp_ci_OM_simulate_file)
        yml_text = my_template.render(ci_stage_OM_simulate=self.ci_stage_OM_simulate,
                                      python_version=self.python_version,
                                      dymola_python_test_url=self.dymola_python_test_url,
                                      dymola_python_dir=self.dymola_python_dir.replace(os.sep, "/"),
                                      xvfb_flag=self.xvfb_flag,
                                      dymola_python_test_validate_file=self.dymola_python_test_validate_file.replace(os.sep, "/"),
                                      library=self.library,
                                      dymola_version=self.dymola_version,
                                      result_dir=self.result_dir.replace(os.sep, "/"),
                                      except_branch_list=self.except_branch_list,
                                      html_praefix=self.html_praefix,
                                      except_commit_list=self.except_commit_list,
                                      package_list=self.package_list,
                                      expire_in_time=self.expire_in_time,
                                      merge_branch=merge_branch,
                                      dymola_python_configuration_file=self.dymola_python_configuration_file.replace(os.sep,"/"),
                                      config_ci_changed_file=self.config_ci_changed_file.replace(os.sep,"/"),
                                      ci_simulate_commit=self.ci_OM_simulate_commit,
                                      wh_flag=wh_flag,
                                      filter_flag=filter_flag        )
        ci_folder = f'{self.temp_dir}{os.sep}{self.temp_ci_OM_simulate_file.split(os.sep)[-2]}'
        self.check_ci_folder_structure([ci_folder])
        yml_file = f'{ci_folder}{os.sep}{self.temp_ci_OM_simulate_file.split(os.sep)[-1]}'
        yml_tmp = open(yml_file.replace(".txt", ".gitlab-ci.yml"), "w")
        yml_tmp.write(yml_text.replace('\n', ''))
        yml_tmp.close()


    def _write_OM_check_template(self):
        if self.wh_library is not None:
            wh_library = self.wh_library
            filter_flag = "--filter-whitelist"
            wh_flag = "--wh-library " + self.wh_library
            merge_branch = f'- {self.wh_library}_Merge'
            if self.wh_path is not None:
                wh_path = "--wh-path " + self.wh_path
                git_url = ""
            elif self.git_url is not None:
                git_url = "--git-url " + self.git_url
                wh_path = ""
            else:
                wh_path = ""
                git_url = ""
        else:
            wh_library = self.library
            wh_flag = ""
            git_url = ""
            filter_flag = ""
            wh_path = ""
            merge_branch = ""
        my_template = Template(filename=self.temp_ci_OM_check_file)
        yml_text = my_template.render(ci_stage_OM_model_check=self.ci_stage_OM_model_check,
                                      xvfb_flag=self.xvfb_flag,
                                      python_version=self.python_version,
                                      dymola_python_test_url=self.dymola_python_test_url,
                                      dymola_python_dir=self.dymola_python_dir.replace(os.sep, "/"),
                                      library=self.library,
                                      dymola_version=self.dymola_version,
                                      wh_flag=wh_flag,
                                      merge_branch=merge_branch,
                                      ci_check_commit=self.ci_OM_check_commit,
                                      filter_flag=filter_flag,
                                      result_dir=self.result_dir.replace(os.sep, "/"),
                                      except_commit_list=self.except_commit_list,
                                      except_branch_list=self.except_branch_list,
                                      package_list=self.package_list,
                                      expire_in_time=self.expire_in_time,
                                      config_ci_changed_file=self.config_ci_changed_file.replace(os.sep, "/"),
                                      html_praefix=self.html_praefix,
                                      dymola_python_test_validate_file=self.dymola_python_test_validate_file.replace(os.sep, "/"),
                                      dymola_python_configuration_file=self.dymola_python_configuration_file.replace(os.sep, "/")
                                      )
        ci_folder = f'{self.temp_dir}{os.sep}{self.temp_ci_OM_check_file.split(os.sep)[-2]}'
        self.check_ci_folder_structure([ci_folder])
        yml_file = f'{ci_folder}{os.sep}{self.temp_ci_OM_check_file.split(os.sep)[-1]}'
        yml_tmp = open(yml_file.replace(".txt", ".gitlab-ci.yml"), "w")
        yml_tmp.write(yml_text.replace('\n', ''))
        yml_tmp.close()

    def _write_check_template(self):
        if self.wh_library is not None:
            wh_library = self.wh_library
            filter_flag = "--filter-whitelist"
            wh_flag = "--wh-library " + self.wh_library
            merge_branch = f'- {self.wh_library}_Merge'
            if self.wh_path is not None:
                wh_path = "--wh-path " + self.wh_path
                git_url = ""
            elif self.git_url is not None:
                git_url = "--git-url " + self.git_url
                wh_path = ""
            else:
                wh_path = ""
                git_url = ""
        else:
            wh_library = self.library
            wh_flag = ""
            git_url = ""
            filter_flag = ""
            wh_path = ""
            merge_branch = ""
        my_template = Template(filename=self.temp_ci_check_file)
        yml_text = my_template.render(ci_stage_model_check=self.ci_stage_model_check,
                                      ci_stage_create_whitelist=self.ci_stage_create_whitelist,
                                      python_version=self.python_version,
                                      dymola_python_test_url=self.dymola_python_test_url,
                                      except_commit_list=self.except_commit_list,
                                      except_branch_list=self.except_branch_list,
                                      library=self.library,
                                      package_list=self.package_list,
                                      dymola_version=self.dymola_version,
                                      wh_flag=wh_flag,
                                      filter_flag=filter_flag,
                                      config_ci_changed_file=self.config_ci_changed_file.replace(os.sep, "/"),
                                      expire_in_time=self.expire_in_time,
                                      merge_branch=merge_branch,
                                      ci_check_commit=self.ci_check_commit,
                                      config_ci_exit_file=self.config_ci_exit_file.replace(os.sep, "/"),
                                      git_url=git_url,
                                      wh_path=wh_path,
                                      wh_library=wh_library,
                                      bot_update_model_wh_commit=self.bot_update_model_wh_commit,
                                      wh_model_file=self.wh_model_file.replace(os.sep, "/"),
                                      ci_create_model_wh_commit=self.ci_create_model_wh_commit,
                                      xvfb_flag=self.xvfb_flag,
                                      dymola_python_test_validate_file=self.dymola_python_test_validate_file.replace(
                                          os.sep, "/"),
                                      dymola_python_configuration_file=self.dymola_python_configuration_file.replace(
                                          os.sep, "/"),
                                      html_praefix=self.html_praefix,
                                      result_dir=self.result_dir.replace(os.sep, "/"),
                                      dymola_python_dir=self.dymola_python_dir.replace(os.sep, "/"))
        ci_folder = f'{self.temp_dir}{os.sep}{self.temp_ci_check_file.split(os.sep)[-2]}'
        self.check_ci_folder_structure([ci_folder])
        yml_file = f'{ci_folder}{os.sep}{self.temp_ci_check_file.split(os.sep)[-1]}'
        yml_tmp = open(yml_file.replace(".txt", ".gitlab-ci.yml"), "w")
        yml_tmp.write(yml_text.replace('\n', ''))
        yml_tmp.close()

    def _write_simulate_template(self):
        if self.wh_library is not None:
            filter_flag = "--filter-whitelist"
            wh_flag = "--wh-library " + self.wh_library
            merge_branch = "- " + self.merge_branch
            if self.wh_path is not None:
                wh_path = "--wh-path " + self.wh_path
                git_url = ""
            elif self.git_url is not None:
                git_url = "--git-url " + self.git_url
                wh_path = ""
            else:
                wh_path = ""
                git_url = ""
        else:
            merge_branch = ""
            filter_flag = ""
            wh_flag = ""
            wh_path = ""
            git_url = ""
        my_template = Template(filename=self.temp_ci_simulate_file)
        yml_text = my_template.render(ci_stage_simulate=self.ci_stage_simulate,
                                      python_version=self.python_version,
                                      dymola_python_test_url=self.dymola_python_test_url,
                                      library=self.library,
                                      wh_library=self.wh_library,
                                      git_url=git_url,
                                      dymola_version=self.dymola_version,
                                      wh_flag=wh_flag,
                                      wh_path=wh_path,
                                      filter_flag=filter_flag,
                                      ci_simulate_commit=self.ci_simulate_commit,
                                      expire_in_time=self.expire_in_time,
                                      package_list=self.package_list,
                                      except_commit_list=self.except_commit_list,
                                      except_branch_list=self.except_branch_list,
                                      config_ci_changed_file=self.config_ci_changed_file.replace(os.sep, "/"),
                                      merge_branch=merge_branch,
                                      ci_stage_create_exampeL_whitelist=self.ci_stage_create_example_whitelist,
                                      bot_update_example_wh_commit=self.bot_update_example_wh_commit,
                                      config_ci_exit_file=self.config_ci_exit_file.replace(os.sep, "/"),
                                      wh_simulate_file=self.wh_simulate_file.replace(os.sep, "/"),
                                      ci_create_simulate_wh_commit=self.ci_create_simulate_wh_commit,
                                      xvfb_flag=self.xvfb_flag,
                                      dymola_python_test_validate_file=self.dymola_python_test_validate_file.replace(
                                          os.sep, "/"),
                                      dymola_python_configuration_file=self.dymola_python_configuration_file.replace(
                                          os.sep, "/"),
                                      html_praefix=self.html_praefix,
                                      result_dir=self.result_dir.replace(os.sep, "/"),
                                      dymola_python_dir=self.dymola_python_dir.replace(os.sep, "/"))
        ci_folder = f'{self.temp_dir}{os.sep}{self.temp_ci_simulate_file.split(os.sep)[-2]}'
        self.check_ci_folder_structure([ci_folder])
        yml_file = f'{ci_folder}{os.sep}{self.temp_ci_simulate_file.split(os.sep)[-1]}'
        yml_tmp = open(yml_file.replace(".txt", ".gitlab-ci.yml"), "w")
        yml_tmp.write(yml_text.replace('\n', ''))
        yml_tmp.close()

    def write_toml_settings(self, stage_list, file_list, config_list):
        """
        Write CI setting.
        @param stage_list:
        @type stage_list:
        @param file_list:
        @type file_list:
        @param config_list:
        @type config_list:
        @param git_url:
        @type git_url:
        """
        my_template = Template(filename=self.temp_toml_ci_setting_file)
        yml_text = my_template.render(library=self.library,
                                      wh_library=self.wh_library,
                                      dymola_version=self.dymola_version,
                                      package_list=self.package_list,
                                      stage_list=stage_list,
                                      merge_branch=self.merge_branch,
                                      image_name=self.image_name,
                                      variable_main_list=self.variable_main_list,
                                      except_commit_list=self.except_commit_list,
                                      file_list=file_list,
                                      config_list=config_list,
                                      git_url=self.git_url,
                                      python_version=self.python_version,
                                      wh_path=self.wh_path,
                                      github_repo_name=self.github_repo,
                                      gitlab_page_name=self.gitlab_page,
                                      dymola_python_dir=self.dymola_python_dir.replace(os.sep, "/"))
        yml_tmp = open(self.toml_ci_setting_file, "w")
        yml_tmp.write(yml_text.replace('\n', ''))
        yml_tmp.close()
        print(f'The CI settings are saved in file {self.toml_ci_setting_file}')

    def write_main_yml(self, stage_list, ci_template_list):
        """

        @param stage_list:
        @type stage_list:
        @param ci_template_list:
        @type ci_template_list:
        """
        my_template = Template(filename=self.temp_ci_main_yml_file)
        yml_text = my_template.render(image_name=self.image_name,
                                      stage_list=stage_list,
                                      variable_list=self.variable_main_list,
                                      file_list=ci_template_list)
        ci_folder = f'{self.temp_dir}'
        self.check_ci_folder_structure([ci_folder])
        yml_file = f'{ci_folder}{os.sep}{self.temp_ci_main_yml_file.split(os.sep)[-1]}'
        yml_tmp = open(yml_file.replace(".gitlab-ci.txt", ".gitlab-ci.yml"), "w")
        yml_tmp.write(yml_text.replace('\n', ''))
        yml_tmp.close()

    def _get_variables(self):
        """

        @return:
        @rtype:
        """
        variable_list = self.variable_main_list
        print(f'Setting variables: {variable_list}')
        return variable_list

    def _get_image_name(self):
        """

        @return:
        @rtype:
        """
        image_name = self.image_name
        print(f'Setting image: {image_name}')
        return image_name

    def get_yml_templates(self):
        """
        @return:
        @rtype:
        """
        ci_template_list = []
        print("hallo")
        for subdir, dirs, files in os.walk(self.temp_dir):
            for file in files:
                filepath = f'{subdir}{os.sep}{file}'
                if filepath.endswith(".yml") and file != ".gitlab-ci.yml":
                    print("hallo")
                    print(filepath)
                    filepath = filepath.replace(os.sep, "/")
                    ci_template_list.append(filepath)
        if len(ci_template_list) == 0:
            print(f'No templates')
            exit(1)
        else:
            for yml_files in ci_template_list:
                print(f'Setting yml files: {yml_files}')
            return ci_template_list

    def get_stages(self, file_list):
        """

        @param file_list:
        @type file_list:
        @return:
        @rtype:
        """
        stage_list = []
        for file in file_list:
            infile = open(file, "r")
            lines = infile.readlines()
            stage_content = False
            for line in lines:
                line = line.strip()
                if len(line.strip()) == 0:
                    continue
                elif line.find("stages:") > -1:
                    stage_content = True
                elif line.find(":") > -1 and line.find("stages:") == -1:
                    stage_content = False
                elif stage_content is True:
                    line = line.replace("-", "")
                    line = line.replace(" ", "")
                    stage_list.append(line)
                else:
                    continue
        if len(stage_list) == 0:
            print(f'No stages')
            exit(1)
        stage_list = list(set(stage_list))
        new_list = []
        for stage in self.stage_list:
            for st in stage_list:
                if stage == st:
                    new_list.append(stage)
        for stage in new_list:
            print(f'Setting stages: {stage}')
        return new_list

    def write_ci_templates(self, config_list):
        """
        @param config_list:
        @type config_list:
        """
        self._write_setting_template()
        for temp in config_list:
            if temp == "check":
                self._write_check_template()
                self._write_OM_check_template()
            if temp == "simulate":
                self._write_simulate_template()
                self._write_OM_simulate_template()
            if temp == "regression":
                self._write_regression_template()
            if temp == "html":
                self._write_html_template()
            if temp == "style":
                self._write_style_template()
            if temp == "Merge" and self.wh_library is not None:
                self._write_merge_template()
        self._write_CI_Whitelist_Setting_template()
        self._write_page_template()
        self._write_ci_structure_template()


class Read_config_data(CI_template_config):

    def __init__(self):
        """
        """
        super().__init__()

    def delte_yml_files(self):
        """

        """
        for subdir, dirs, files in os.walk(self.temp_dir):
            for file in files:
                filepath = f'{subdir}{os.sep}{file}'
                if filepath.endswith(".yml") and file != ".gitlab-ci.yml":
                    os.remove(filepath)

    def call_toml_data(self):
        """

        @return:
        @rtype:
        """
        data = toml.load(self.toml_ci_setting_file)
        library = self._read_library(data=data)
        package_list = self._read_package_list(data=data)
        dymola_version = self._read_dymola_version(data=data)
        wh_library = self._read_wh_library(data=data)
        git_url = self._read_git_url(data=data)
        wh_path = self._read_wh_path(data=data)
        python_version = self._read_pythonversion(data=data)
        config_list = self._read_config_list(data=data)
        ci_template_list = self._read_file_list(data=data)
        stage_list = self._read_stages(data=data)
        github_repo = self._read_github_repo(data=data)
        image_name = self._read_image_name(data=data)
        gitlab_page = self._read_gitlab_page(data=data)
        return library, package_list, dymola_version, wh_library, git_url, wh_path, python_version, config_list, stage_list, ci_template_list, github_repo, image_name, gitlab_page

    @staticmethod
    def _read_gitlab_page(data):
        """

        @param data:
        @type data:
        @return:
        @rtype:
        """
        gitlab_page = data["gitlab_page"]
        gitlab_page = gitlab_page["gitlab_page"]
        print(f'Setting library: {gitlab_page}')
        return gitlab_page

    @staticmethod
    def _read_github_repo(data):
        """

        @param data:
        @type data:
        @return:
        @rtype:
        """
        github_repo = data["github_repo"]
        github_repo = github_repo["github_repo"]
        print(f'Setting library: {github_repo}')
        return github_repo

    @staticmethod
    def _read_library(data):
        """
        @param data:
        @type data:
        @return:
        @rtype:
        """
        library = data["library"]
        library = library["library_name"]
        print(f'Setting library: {library}')
        return library

    @staticmethod
    def _read_wh_library(data):
        """

        @param data:
        @type data:
        @return:
        @rtype:
        """
        wh_library = data["whitelist_library"]
        wh_library = wh_library["wh_library_name"]
        if wh_library == "None":
            wh_library = None
        print(f'Setting whitelist_library: {wh_library}')
        return wh_library

    @staticmethod
    def _read_package_list(data):
        """

        @param data:
        @type data:
        @return:
        @rtype:
        """
        package_list = data["Package"]
        package_list = package_list["package_list"]
        for package in package_list:
            print(f'Setting package: {package}')
        return package_list

    @staticmethod
    def _read_dymola_version(data):
        """

        @param data:
        @type data:
        @return:
        @rtype:
        """
        dymola_version = data["dymola_version"]
        dymola_version = dymola_version["dymola_version"]
        print(f'Setting dymola_version: {dymola_version}')
        return dymola_version

    @staticmethod
    def _read_pythonversion(data):
        """

        @param data:
        @type data:
        @return:
        @rtype:
        """
        pythonversion = data["python_version"]
        pythonversion = pythonversion["python_version"]
        print(f'Setting python version: {pythonversion}')
        return pythonversion

    @staticmethod
    def _read_stages(data):
        """

        @param data:
        @type data:
        @return:
        @rtype:
        """
        stages = data["stages"]
        stages = stages["stage_list"]
        for stage in stages:
            print(f'Setting stage: {stage}')
        return stages

    @staticmethod
    def _read_merge_branch(data):
        """

        @param data:
        @type data:
        @return:
        @rtype:
        """
        Merge_Branch = data["Merge_Branch"]
        Merge_Branch = Merge_Branch["merge_branch"]
        print(f'Setting merge branch: {Merge_Branch}')
        return Merge_Branch

    @staticmethod
    def _read_image_name(data):
        """

        @param data:
        @type data:
        @return:
        @rtype:
        """
        image_name = data["image_name"]
        image_name = image_name["image"]
        print(f'Setting image: {image_name}')
        return image_name

    @staticmethod
    def _read_variable_list(data):
        """

        @param data:
        @type data:
        @return:
        @rtype:
        """
        variable_list = data["variable_list"]
        variable_list = variable_list["variablelist"]
        print(f'Setting variables: {variable_list}')
        return variable_list

    @staticmethod
    def _read_ci_commands(data):
        """

        @param data:
        @type data:
        @return:
        @rtype:
        """
        ci_commit_commands = data["ci_commit_commands"]
        ci_commit_commands = ci_commit_commands["commitlist"]
        print(f'Setting ci commands: {ci_commit_commands}')
        return ci_commit_commands

    @staticmethod
    def _read_file_list(data):
        """

        @param data:
        @type data:
        @return:
        @rtype:
        """
        file_list = data["File_list"]
        file_list = file_list["filelist"]
        for file in file_list:
            print(f'Setting yaml file list: {file}')
        return file_list

    @staticmethod
    def _read_config_list(data):
        """

        @param data:
        @type data:
        @return:
        @rtype:
        """
        config_list = data["config_list"]
        config_list = config_list["configlist"]
        print(f'Setting config list: {config_list}')
        return config_list

    @staticmethod
    def _read_git_url(data):
        """

        @param data:
        @type data:
        @return:
        @rtype:
        """
        git_url = data["git_url"]
        git_url = git_url["git_url"]
        if git_url == "None":
            git_url = None
        print(f'Setting git whitelist url: {git_url}')
        return git_url

    @staticmethod
    def _read_wh_path(data):
        """

        @param data:
        @type data:
        @return:
        @rtype:
        """
        wh_path = data["wh_library_path"]
        wh_path = wh_path["wh_path"]
        if wh_path == "None":
            wh_path = None
        print(f'Setting git whitelist url: {wh_path}')
        return wh_path


class Set_CI_Settings_interactive(CI_template_config):
    def __init__(self):
        """

        """
        super().__init__()

    def call_ci_setting(self):
        """

        @return:
        @rtype:
        """
        template_list = self._set_ci_templates()
        library = self._ci_set_library()
        package_list = self._set_ci_packages(library=library)
        dymola_version = self._set_ci_dymola_version()
        python_version = self._set_ci_python_version()
        wh_result = self._set_ci_whitelist()  # wh_library, git_url, wh_path
        github_repo = self._set_ci_github_repo()
        gitlab_page = self._set_ci_gitlab_page()
        image_name = self._set_ci_image()
        return template_list, library, package_list, dymola_version, python_version, wh_result, github_repo, gitlab_page, image_name

    @staticmethod
    def _set_ci_templates():
        """
        @return:
        @rtype:
        """
        config_list = []
        response = input(f'Config template: Check html Syntax in models? (y/n) ')
        if response == "y":
            print(f'Create html template')
            config_list.append("html")
        response = input(f'Config template: Check style of models? (y/n) ')
        if response == "y":
            print(f'Create style template')
            config_list.append("style")
        response = input(f'Config template: Check models? (y/n) ')
        if response == "y":
            print(f'Create check template')
            config_list.append("check")
        response = input(f'Config template: Simulate examples? (y/n) ')
        if response == "y":
            print(f'Create simulate template')
            config_list.append("simulate")
        response = input(f'Config template: Regression test? (y/n) ')
        if response == "y":
            print(f'Create regression emplate')
            config_list.append("regression")
        response = input(f'Config template: Merge Update? (y/n) ')
        if response == "y":
            print(f'Create merge template')
            config_list.append("Merge")
        if len(config_list) == 0:
            exit(0)
        return config_list

    def _ci_set_library(self):
        """

        @return:
        @rtype:
        """
        library = input(f'Which library should be tested? (e.g. {self.library}): ')
        print(f'Setting library: {library}')
        return library

    @staticmethod
    def _set_ci_packages(library):
        """
        @return:
        @rtype:
        """
        package_list = []
        package_list_final = []
        for package in os.listdir(library):
            if package.find(".") == -1:
                package_list.append(package)

        if package_list is None:
            print(f'Dont find library {library}')
            exit(1)
        for package in package_list:
            response = input(f'Test package {package}? (y/n) ')
            if response == "y":
                package_list_final.append(package)
                continue
            else:
                continue
        print(f'Setting packages: {package_list_final}')
        return package_list_final

    def _set_ci_dymola_version(self):
        """

        @return:
        @rtype:
        """
        dymola_version = input(f'Give the dymolaversion (e.g. {self.dymola_version}): ')
        print(f'Setting dymola version: {dymola_version}')
        return dymola_version

    def _set_ci_python_version(self):
        """

        @return:
        @rtype:
        """
        python_version = input(f'Give the python version in your image (e.g. {self.python_version}): ')
        print(f'Setting python version: {python_version}')
        return python_version

    def _set_ci_whitelist(self):
        """

        @return:
        @rtype:
        """
        response = input(
            f'Create whitelist? Useful if your own library has been assembled from other libraries. A whitelist is created, where faulty models from the foreign library are no longer tested in the future and are filtered out. (y/n)  ')
        wh_library = None
        git_url = None
        wh_path = None
        if response == "y":
            wh_config = True
            while wh_config is True:
                wh_library = input(
                    f'What library models should on whitelist: Give the name of the library (e.g.{self.wh_library}): ')
                print(f'Setting whitelist library: {wh_library}')
                response = input(f'If the foreign library is local on the PC? (y/n) ')
                if response == "y":
                    wh_path = input(f'Specify the local path of the library (eg. D:\..path..\AixLib) ')
                    print(f'path of library: {wh_path}')
                    git_url = None
                else:
                    git_url = input(
                        f'Give the url of the library repository (eg. "{self.git_url}"):  ')
                    print(f'Setting git_url: {git_url}')
                    wh_path = None
                response = input(f'Are settings okay(y/n)? ')
                if response == "y":
                    wh_config = False
        return wh_library, git_url, wh_path

    def _set_ci_github_repo(self):
        """

        @return:
        @rtype:
        """
        github_repo = input(f'Which github repo should be used? (e.g {self.github_repo}): ')
        print(f'Setting dymola version: {github_repo}')
        return github_repo

    def _set_ci_gitlab_page(self):
        """

        @return:
        @rtype:
        """
        gitlab_page = input(f'Which gitlab page should be used? (e.g {self.gitlab_page}): ')
        print(f'Setting dymola version: {gitlab_page}')
        return gitlab_page

    def _set_ci_image(self):
        """
        """
        image_name = input(f'Which docker image should be used? (e.g {self.image_name}): ')
        print(f'Setting dymola version: {image_name}')
        return image_name


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Set Github Environment Variables")
    check_test_group = parser.add_argument_group("Arguments to set Environment Variables")
    check_test_group.add_argument("--setting",
                                  help=f'Create the CI from file Setting{os.sep}CI_setting.txt',
                                  action="store_true")
    args = parser.parse_args()
    Conf = Read_config_data()
    Conf.delte_yml_files()

    if args.setting is False:
        set_setting = Set_CI_Settings_interactive()
        result = set_setting.call_ci_setting()
        CI_Class = CI_yml_templates(library=result[1],
                                    package_list=result[2],
                                    dymola_version=result[3],
                                    python_version=result[4],
                                    wh_library=result[5][0],
                                    git_url=result[5][1],
                                    wh_path=result[5][2],
                                    github_repo=result[6],
                                    gitlab_page=result[7],
                                    image_name=result[8])
        CI_Class.write_ci_templates(config_list=result[0])
        ci_template_list = CI_Class.get_yml_templates()
        stage_list = CI_Class.get_stages(file_list=ci_template_list)
        CI_Class.write_main_yml(stage_list=stage_list,
                                ci_template_list=ci_template_list)
        CI_Class.write_toml_settings(stage_list=stage_list,
                                     file_list=ci_template_list,
                                     config_list=result[0])
    if args.setting is True:
        result = Conf.call_toml_data()
        CI_Class = CI_yml_templates(library=result[0],
                                    package_list=result[1],
                                    dymola_version=result[2],
                                    wh_library=result[3],
                                    git_url=result[4],
                                    wh_path=result[5],
                                    python_version=result[6],
                                    github_repo=result[10],
                                    image_name=result[11],
                                    gitlab_page=result[12])
        CI_Class.write_ci_templates(config_list=result[7])
        CI_Class.write_main_yml(stage_list=result[8], ci_template_list=result[9])
