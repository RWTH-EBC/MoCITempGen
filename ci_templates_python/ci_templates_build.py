import os
from mako.template import Template
import argparse
import toml
from ci_templates_python.ci_templates_config import ci_template_config
from ci_templates_python.ci_templates_structure import templates_structure
import glob
from ci_tests.structure.arg_parser import argpaser_toml
from ci_tests.structure.config_structure import data_structure
from pathlib import Path
import sys
import tomli_w as tomlwriter


class CI_temp_struc(object):

    def __init__(self):
        pass

    def _arg_list(self, _list: list):
        value_str = ""
        for value in _list:
            value_str = f'{value_str} {value} '
        return value_str
    def _arg_dict(self, _dict: dict):
        value_str = ""
        for value in _dict:
            value_str = f'{value_str} {_dict[value]} '
        return value_str



    def write_parser_args(self, py_file: str = None, repl_parser_arg: dict = None, out:list = None):
        arg_to = argpaser_toml()
        data = arg_to.load_argparser_toml()
        arg_parser = data[py_file]["Parser"]
        parser_str = ""
        for var in arg_parser:
            out_flag = False
            if out is not None:
                for o in out:
                    if o == var:
                        out_flag = True
                        break
            if out_flag is False:
                rep_flag = True
                if repl_parser_arg is not None:
                    while rep_flag is True:
                        for rep in repl_parser_arg:
                            if rep == var:
                                if isinstance(repl_parser_arg[rep], dict):
                                    value_str = self._arg_dict(arg_parser[var])
                                    arg = f'--{var.replace("_", "-")} {value_str} '
                                elif isinstance(repl_parser_arg[rep], list):
                                    value_str = self._arg_list(repl_parser_arg[rep])
                                    arg = f'--{var.replace("_", "-")} {value_str} '
                                else:
                                    arg = f'--{var.replace("_", "-")} {repl_parser_arg[rep]} '
                                parser_str = arg + parser_str
                                rep_flag = False
                                break
                        if rep_flag is True:

                            if arg_parser[var] is None or arg_parser[var] == "None":
                                break
                            elif isinstance(arg_parser[var], dict):
                                value_str = self._arg_dict(arg_parser[var])
                                arg = f'--{var.replace("_", "-")} {value_str} '
                            elif isinstance(arg_parser[var], list):
                                value_str = self._arg_list(arg_parser[var])
                                arg = f'--{var.replace("_", "-")} {value_str} '
                            else:
                                arg = f'--{var.replace("_", "-")} {arg_parser[var]} '
                            parser_str = arg + parser_str
                            rep_flag = False

                else:
                    if arg_parser[var] is None or arg_parser[var] == "None":
                        continue
                    if isinstance(arg_parser[var], list):
                        value_str = self._arg_list(arg_parser[var])
                        arg = f'--{var.replace("_", "-")} {value_str} '

                    else:
                        arg = f'--{var.replace("_", "-")} {arg_parser[var]} '
                    parser_str = arg + parser_str
        return parser_str

    @staticmethod
    def write_multiple_rules(rule_list: list = None,
                             except_string: str = None,
                             rule_option: str = "&&",
                             compare_str: str = "!~",
                             ci_variable: str = None):

        if rule_list is not None:
            if isinstance(rule_list, dict):
                if except_string is not None:
                    _list = []
                    for var in rule_list:
                        if var != except_string:
                            _list.append(f'{ci_variable}  {compare_str} /{rule_list[var]}/')

                else:
                    _list = []
                    for var in rule_list:
                        _list.append(f'{ci_variable}  {compare_str} /{rule_list[var]}/')

                rule_string = ""
                for rule in _list:
                    if rule == _list[0]:
                        rule_string = f'{rule}  '
                    else:
                        rule_string = f'{rule_string} {rule_option} {rule}'

                return rule_string
            if isinstance(rule_list, list):
                if except_string is not None:
                    rule_list = [f'{ci_variable}  {compare_str} /{value}/' for value in rule_list if
                                 value != except_string]
                else:
                    rule_list = [f'{ci_variable}  {compare_str} /{value}/' for value in rule_list]
                rule_string = ""
                for rule in rule_list:
                    if rule == rule_list[0]:
                        rule_string = f'{rule}  '
                    else:
                        rule_string = f'{rule_string} {rule_option} {rule}'
                return rule_string

        else:
            print("Rule is None")
            exit(1)

    def overwrite_ci_parser_toml(self, file_parser_dict):
        # file_parser_dict: {file: {parser_arg1: overwrite1, parser_arg2:overwrite2}}
        to = argpaser_toml()
        for file in file_parser_dict:
            to.overwrite_parser_toml(file=file, parser_dict=file_parser_dict[file])
        print("overwrite sucessful.")

    def overwrite_arg(self):
        file_dict = {}
        to = argpaser_toml()
        parser_data = to.load_argparser_toml()
        ci_data = CI_toml_parser().read_ci_template_toml()
        _dict = {}
        for file in parser_data:
            _list = []
            arg_dict = parser_data[file]["Parser"]
            for arg in arg_dict:
                _list.append(arg)
            _dict[file] = _list
        for d in ci_data:
            file = ci_data[d]
            for cont in file:
                for arg in cont:
                    value = cont[arg]
                    for ci_file in _dict:
                        for pars in _dict[ci_file]:
                            if arg == pars:
                                parser_data[ci_file]["Parser"][arg] = value
                                pass
        return parser_data

    def convert_dict_keys_to_list(self, _dict: dict):
        _list = []
        for key in _dict:
            _list.append(key)
        return _list


class ci_templates(ci_template_config):

    def __init__(self, library, package_list, dymola_version, wh_library, git_url, wh_path, python_version, github_repo,
                 image_name, gitlab_page, except_commit_list, stage_list):
        super().__init__()
        self.except_commit_list = except_commit_list
        self.stage_list = stage_list
        self.library = library
        self.package_list = package_list
        self.dymola_version = dymola_version
        self.wh_library = wh_library
        self.git_url = git_url
        self.wh_path = wh_path
        self.python_version = python_version
        self.merge_branch = f'{self.wh_library}_Merge'
        self.github_repository = github_repo
        self.image_name = image_name
        self.gitlab_page = gitlab_page

        # self.variable_main_list = [f'Github_Repository: {self.github_repo}', f'GITLAB_Page: {self.gitlab_page}']
        self.rule = CI_temp_struc()
        self.commit_string = self.rule.write_multiple_rules(rule_list=self.except_commit_list,
                                                       rule_option="&&",
                                                       compare_str="!~",
                                                       ci_variable="$CI_COMMIT_MESSAGE")

        self.pr_main_branch_rule = self.rule.write_multiple_rules(rule_list=self.main_branch_list,
                                                             rule_option="||",
                                                             compare_str="==",
                                                             ci_variable="$CI_COMMIT_BRANCH")
    def write_OM_check_template(self):
        ci_temp = Path(self.temp_ci_dir, self.temp_ci_OM_check_file)
        print(f"Write {ci_temp}")
        my_template = Template(filename=str(ci_temp))
        commit_string = self.rule.write_multiple_rules(rule_list=self.except_commit_list,
                                                       rule_option="&&",
                                                       compare_str="!~",
                                                       ci_variable="$CI_COMMIT_MESSAGE")
        pr_main_branch_rule = self.rule.write_multiple_rules(rule_list=self.main_branch_list,
                                                             rule_option="||",
                                                             compare_str="==",
                                                             ci_variable="$CI_COMMIT_BRANCH")
        #out = ["root_library", "library"]
        arg_PR = self.rule.write_parser_args(py_file=Path(self.OM_python_check_model_file).name.replace(".py", ""),
                                             repl_parser_arg={"packages": "$lib_package", "om_options": "OM_CHECK"})
        arg_push = self.rule.write_parser_args(py_file=Path(self.OM_python_check_model_file).name.replace(".py", ""),
                                             repl_parser_arg={"packages": "$lib_package", "om_options": "OM_CHECK", "changed_flag":True})

        yml_text = my_template.render(ci_stage_OM_model_check=self.ci_stage_OM_model_check,
                                      commit_string=commit_string,
                                      library=self.library[0],
                                      PR_main_branch_rule=pr_main_branch_rule,
                                      ci_OM_check_commit=self.ci_OM_check_commit,
                                      OM_Image=self.OM_Image,
                                      dymola_python_test_url=self.dymola_python_test_url,
                                      OM_python_check_model_file=self.OM_python_check_model_file,
                                      result_dir=self.result_dir,
                                      expire_in_time=self.expire_in_time,
                                      arg_PR=arg_PR,
                                      arg_push=arg_push,
                                      packages=self.package_list[self.library[0]],
                                      dymola_python_dir=self.dymola_python_dir)
        ci_folder = Path(self.temp_dir, self.temp_ci_OM_check_file).parent
        data_structure().create_path(ci_folder)
        yml_tmp = open(Path(ci_folder, Path(self.temp_ci_OM_check_file).name.replace(".txt", ".gitlab-ci.yml")), "w")
        yml_tmp.write(yml_text.replace('\n', ''))
        yml_tmp.close()

    def write_ci_structure_template(self):
        """

        """
        my_template = Template(filename=self.temp_ci_structure_file)
        yml_text = my_template.render(image_name=self.image_name,
                                      ci_stage_build_ci_structure=self.ci_stage_build_ci_structure,
                                      python_version=self.python_version,
                                      dymola_python_test_url=self.dymola_python_test_url,
                                      bot_create_structure_commit=self.bot_create_structure_commit,
                                      ci_build_structure_commit=self.ci_build_structure_commit,
                                      wh_model_file=self.wh_model_file,
                                      wh_html_file=wh_html_file,
                                      wh_ref_file=self.wh_ref_file,
                                      ci_interact_show_ref_file=self.ci_interact_show_ref_file,
                                      ci_interact_update_ref_file=self.ci_interact_update_ref_file,
                                      expire_in_time=self.expire_in_time,
                                      dymola_python_dir=self.dymola_python_dir.replace(os.sep, "/"))
        ci_folder = f'{self.temp_dir}{os.sep}{self.temp_ci_structure_file.split(os.sep)[-2]}'
        self.check_path_setting(ci_folder)
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

    def write_page_template(self):
        """
        Write page template, deploy artifacts, plots, reference results
        """
        my_template = Template(filename=self.temp_ci_page_file)
        yml_text = my_template.render(image_name=self.image_name,
                                      ci_stage_deploy=self.ci_stage_deploy,
                                      expire_in_time=self.expire_in_time,
                                      except_branch_list=self.except_branch_list,
                                      dymola_python_dir=self.dymola_python_dir.replace(os.sep, "/"),
                                      result_dir=self.result_dir.replace(os.sep, "/"))
        ci_folder = f'{self.temp_dir}{os.sep}{self.temp_ci_page_file.split(os.sep)[-2]}'
        self.check_path_setting(ci_folder)
        yml_file = f'{ci_folder}{os.sep}{self.temp_ci_page_file.split(os.sep)[-1]}'
        yml_tmp = open(yml_file.replace(".txt", ".gitlab-ci.yml"), "w")
        yml_tmp.write(yml_text.replace('\n', ''))
        yml_tmp.close()

    def _write_setting_template(self):
        """
        Write setting template, create template with own Syntax
        """
        my_template = Template(filename=self.temp_ci_setting_file)
        yml_text = my_template.render(image_name=self.image_name,
                                      github_repo=self.github_repo,
                                      ci_setting_commit=self.ci_setting_commit,
                                      python_version=self.python_version,
                                      ci_stage_check_setting=self.ci_stage_check_setting,
                                      ci_stage_build_templates=self.ci_stage_build_templates,
                                      bot_create_CI_template_commit=self.bot_create_CI_template_commit,
                                      temp_dir=self.temp_dir,
                                      dymola_python_test_url=self.dymola_python_test_url,
                                      dymola_python_dir=self.dymola_python_dir.replace(os.sep, "/"))
        ci_folder = f'{self.temp_dir}{os.sep}{self.temp_ci_setting_file.split(os.sep)[-2]}'
        self.check_path_setting(ci_folder)
        yml_file = f'{ci_folder}{os.sep}{self.temp_ci_setting_file.split(os.sep)[-1]}'
        yml_tmp = open(yml_file.replace(".txt", ".gitlab-ci.yml"), "w")
        yml_tmp.write(yml_text.replace('\n', ''))
        yml_tmp.close()

    def write_html_template(self):
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
        yml_text = my_template.render(image_name=self.image_name,
                                      ci_stage_html_check=self.ci_stage_html_check,
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
        self.check_path_setting(ci_folder)
        yml_file = f'{ci_folder}{os.sep}{self.temp_ci_html_file.split(os.sep)[-1]}'
        yml_tmp = open(yml_file.replace(".txt", ".gitlab-ci.yml"), "w")
        yml_tmp.write(yml_text.replace('\n', ''))
        yml_tmp.close()

    def write_style_template(self):
        """
        Write Style Check template
        """
        merge_branch = f'- {self.wh_library}_Merge'
        mytemplate = Template(filename=self.temp_ci_style_check_file)
        yml_text = mytemplate.render(image_name=self.image_name,
                                     ci_stage_style_check=self.ci_stage_style_check,
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
        self.check_path_setting(ci_folder)
        yml_file = f'{ci_folder}{os.sep}{self.temp_ci_style_check_file.split(os.sep)[-1]}'
        yml_tmp = open(yml_file.replace(".txt", ".gitlab-ci.yml"), "w")
        yml_tmp.write(yml_text.replace('\n', ''))
        yml_tmp.close()

    def write_ci_whitelist_setting_template(self):
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
        yml_text = my_template.render(image_name=self.image_name,
                                      ci_stage_whitelist_setting=self.ci_stage_whitelist_setting,
                                      python_version=self.python_version,
                                      dymola_python_test_url=self.dymola_python_test_url,
                                      dymola_python_configuration_file=self.dymola_python_configuration_file.replace(
                                          os.sep, "/"),
                                      dymola_python_test_validate_file=self.dymola_python_test_validate_file.replace(
                                          os.sep, "/"),
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
        self.check_path_setting(ci_folder)
        yml_file = f'{ci_folder}{os.sep}{self.temp_ci_build_whitelist_file.split(os.sep)[-1]}'
        yml_tmp = open(yml_file.replace(".txt", ".gitlab-ci.yml"), "w")
        yml_tmp.write(yml_text.replace('\n', ''))
        yml_tmp.close()

    def write_merge_template(self):
        """
        Write (IBPSA) Merge template
        """
        merge_branch = f'{self.wh_library}_Merge'
        my_template = Template(filename=self.temp_ci_ibpsa_merge_file)
        yml_text = my_template.render(image_name=self.image_name,
                                      ci_stage_lib_merge=self.ci_stage_lib_merge,
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
        self.check_path_setting(ci_folder)
        yml_file = f'{ci_folder}{os.sep}{self.temp_ci_ibpsa_merge_file.split(os.sep)[-1]}'
        yml_tmp = open(yml_file.replace(".txt", ".gitlab-ci.yml"), "w")
        yml_tmp.write(yml_text.replace('\n', ''))
        yml_tmp.close()

    def write_regression_template(self):
        if self.merge_branch is not None:
            merge_branch = f'- {self.wh_library}_Merge'
        else:
            merge_branch = ""
        mytemplate = Template(filename=self.temp_ci_regression_file)
        yml_text = mytemplate.render(image_name=self.image_name,
                                     ci_stage_regression_test=self.ci_stage_regression_test,
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
                                     result_dir=self.result_dir.replace(os.sep, "/"),
                                     dymola_python_dir=self.dymola_python_dir.replace(os.sep, "/")
                                     )
        ci_folder = f'{self.temp_dir}{os.sep}{self.temp_ci_regression_file.split(os.sep)[-2]}'
        self.check_path_setting(ci_folder)
        yml_file = f'{ci_folder}{os.sep}{self.temp_ci_regression_file.split(os.sep)[-1]}'
        yml_tmp = open(yml_file.replace(".txt", ".gitlab-ci.yml"), "w")
        yml_tmp.write(yml_text.replace('\n', ''))
        yml_tmp.close()

    def write_OM_simulate_template(self):
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
        yml_text = my_template.render(OM_Image=self.OM_Image,
                                      ci_stage_OM_simulate=self.ci_stage_OM_simulate,
                                      python_version=self.python_version,
                                      dymola_python_test_url=self.dymola_python_test_url,
                                      dymola_python_dir=self.dymola_python_dir.replace(os.sep, "/"),
                                      xvfb_flag=self.xvfb_flag,
                                      dymola_python_test_validate_file=self.dymola_python_test_validate_file.replace(
                                          os.sep, "/"),
                                      library=self.library,
                                      dymola_version=self.dymola_version,
                                      result_dir=self.result_dir.replace(os.sep, "/"),
                                      except_branch_list=self.except_branch_list,
                                      html_praefix=self.html_praefix,
                                      except_commit_list=self.except_commit_list,
                                      package_list=self.package_list,
                                      expire_in_time=self.expire_in_time,
                                      merge_branch=merge_branch,
                                      dymola_python_configuration_file=self.dymola_python_configuration_file.replace(
                                          os.sep, "/"),
                                      config_ci_changed_file=self.config_ci_changed_file.replace(os.sep, "/"),
                                      ci_simulate_commit=self.ci_OM_simulate_commit,
                                      wh_flag=wh_flag,
                                      filter_flag=filter_flag)
        ci_folder = f'{self.temp_dir}{os.sep}{self.temp_ci_OM_simulate_file.split(os.sep)[-2]}'
        self.check_path_setting(ci_folder)
        yml_file = f'{ci_folder}{os.sep}{self.temp_ci_OM_simulate_file.split(os.sep)[-1]}'
        yml_tmp = open(yml_file.replace(".txt", ".gitlab-ci.yml"), "w")
        yml_tmp.write(yml_text.replace('\n', ''))
        yml_tmp.close()

    def write_check_template(self):
        ci_temp = Path(self.temp_ci_dir, self.temp_ci_check_file)
        print(f"Write {ci_temp}")
        my_template = Template(filename=str(ci_temp))

        yml_text = my_template.render(dym_image_name="",
                                      ci_stage_model_check=self.ci_stage_model_check,
                                      ci_stage_create_whitelist=self.ci_stage_create_whitelist,
                                      commit_string=self.commit_string,
                                      library=self.library[0],
                                      PR_main_branch_rule=self.pr_main_branch_rule,
                                      ci_check_commit=self.ci_check_commit,
                                      dymola_python_test_url=self.dymola_python_test_url,
                                      dymola_python_dir=self.dymola_python_dir,
                                      xvfb_flag=self.xvfb_flag,
                                      dymola_python_test_validate_file=self.dymola_python_test_validate_file,
                                      result_dir=self.result_dir,
                                      expire_in_time=self.expire_in_time,
                                      arg_push="",
                                      arg_wh="",
                                      arg_PR="",
                                      package_list=self.package_list[self.library[0]],
                                      config_ci_exit_file=self.config_ci_exit_file,
                                      bot_update_model_wh_commit=self.bot_update_model_wh_commit,
                                      wh_model_file=self.wh_model_file,
                                      python_version=self.python_version,
                                      ci_create_model_wh_commit=self.ci_create_model_wh_commit)
        ci_folder = Path(self.temp_dir, self.temp_ci_check_file).parent
        data_structure().create_path(ci_folder)
        yml_tmp = open(Path(ci_folder, Path(self.temp_ci_check_file).name.replace(".txt", ".gitlab-ci.yml")), "w")
        yml_tmp.write(yml_text.replace('\n', ''))
        yml_tmp.close()

    def write_simulate_template(self):
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
        yml_text = my_template.render(image_name=self.image_name,
                                      ci_stage_simulate=self.ci_stage_simulate,
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
        self.check_path_setting(ci_folder)
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
        yml_text = my_template.render(
            library=self.library,
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
        self.check_path_setting(ci_folder)
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

    def get_ci_templates(self):
        """
        @return:
        @rtype:
        """
        py_f = glob.glob(f'{self.temp_dir}/**/*.yml', recursive=True)
        mo_py_files = []
        for file in py_f:
            if file.find(".gitlab-ci.yml") == -1:
                mo_py_files.append(file)
        return mo_py_files

    def get_ci_stages(self, file_list):
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


class Read_config_data(ci_template_config):

    def __init__(self):
        """
        """
        super().__init__()

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


class settings_ci_interactive(ci_template_config):
    def __init__(self):
        """

        """
        super().__init__()
        self.data = data_structure()

    @staticmethod
    def setting_ci_templates_types():
        """
        @return:
        @rtype:
        """
        config_list = []
        file_config_dict = {}
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
        file_config_dict["config_stages"] = config_list
        return file_config_dict

    def setting_ci_libraries(self):
        """
        @return:
        @rtype:
        """
        libraries_root = {}
        libraries = {}
        _list = []
        lib_flag = True
        while lib_flag is True:
            library = input(f'Which library should be tested? (e.g. {self.library}): ')
            path_library = input(
                f'Path of library? (If the library is located in the directory, do not enter an entry.)  ')
            lib_path = os.path.join("..", path_library, library, "package.mo")
            self.data.check_file_setting(lib_path)
            libraries_root[library] = lib_path
            _list.append(library)
            response = input(f'Test more libraries? (y/n) ')
            if response == "n":
                lib_flag = False
        libraries["library"] = _list
        #root_library["root_library"] = _root_list
        print(f'Setting library root: {libraries_root}')
        print(f'Setting library : {libraries}')

        return libraries_root, libraries

    @staticmethod
    def setting_ci_packages(libraries: dict):
        """
        @return:
        @rtype:
        """
        lib_pack_dict = {}
        package_dict = {}
        for lib in libraries:
            package_list = []
            package_lib = []
            print(f'**** Library {lib} ****')
            for package in os.listdir(Path(libraries[lib]).parent):
                if package.find(".") == -1:
                    package_list.append(package)
            if package_list is None:
                print(f'Dont find library {lib}')
                exit(1)
            for package in package_list:
                response = input(f'Test package {package} in library {lib}? (y/n) ')
                if response == "y":
                    package_lib.append(package)
                    continue
            lib_pack_dict[lib] = package_lib
        print(f'Setting packages: {lib_pack_dict}')
        package_dict["package"] = lib_pack_dict
        return package_dict

    def setting_ci_dymola_version(self):
        """

        @return:
        @rtype:
        """
        dymola_dict = {}
        dymola_version = input(f'Give the dymola version (e.g. {self.dymola_version}): ')
        print(f'Setting dymola version: {dymola_version}')
        dymola_dict["dymola_version"] = dymola_version
        return dymola_dict

    def setting_ci_python_conda_env(self):
        """

        @return:
        @rtype:
        """
        conda_env_dict = {}
        python_version = input(f'Give the conda environment in your image (e.g. {self.python_version}): ')
        print(f'Setting python version: {python_version}')
        conda_env_dict["conda_environment"] = python_version
        return conda_env_dict


    def extended_simulates(self):
        _dict = {}
        response = input(f'Should examples be searched recursively? (y/n) ')
        if response == "y":
            flag = True
        else:
            flag = False
        print(f'Setting extended_ex_flag: {flag}')
        _dict["extended_ex_flag"] = flag
        return _dict
    def setting_ci_changed_flag(self):
        changed_dict = {}
        response = input(f'Should only new or modified models from the last commit be tested? (y/n) ')
        if response == "y":
            flag = True
        else:
            flag = False
        print(f'Setting changed_flag: {flag}')
        changed_dict["changed_flag"] = flag
        return changed_dict

    def setting_ci_whitelist(self):
        """

        @return:
        @rtype:
        """
        response = input(
            f'Create whitelist? Useful if your own library has been assembled from other libraries. A whitelist is created, where faulty models from the foreign library are no longer tested in the future and are filtered out. (y/n)  ')
        wh_library_dict = {}
        whitelist_dict = {}
        if response == "y":
            lib_flag = True
            while lib_flag is True:
                wh_library = input(
                    f'What library models should on whitelist: Give the name of the library (e.g.{self.wh_library}): ')
                print(f'Setting whitelist library: {wh_library}')
                response = input(f'If the foreign library is local on the PC? (y/n) ')
                if response == "y":
                    wh_path = input(
                        f'Specify the local path of the library (eg. ..\..\AixLib). (If the library is located in the directory, do not enter an entry.) ')
                    lib_path = os.path.join("..", wh_path, wh_library, "package.mo")
                    self.data.check_file_setting(lib_path)
                    print(f'path of library: {lib_path}')
                    wh_library_dict[wh_library] = lib_path
                else:
                    git_url = input(f'Give the url of the library repository (eg. "{self.git_url}"):  ')
                    print(f'Setting git_url: {git_url}')
                    wh_library_dict[wh_library] = git_url
                response = input(f'More libraries on whitelist? (y/n) ')
                if response == "n":
                    lib_flag = False
        else:
            wh_library_dict = "None"
        print(f'Setting whitelist libraries: {wh_library_dict}')
        whitelist_dict["wh_libraries"] = wh_library_dict
        return whitelist_dict

    def setting_ci_github_repo(self):
        """
        @return:
        @rtype:
        """
        github_repo_dict = {}
        github_repo = input(f'Which github repository in your CI should be used? (e.g {self.github_repository}): ')
        print(f'Setting github repository: {github_repo}')
        github_repo_dict["github_repository"] = github_repo
        return github_repo_dict

    def setting_ci_gitlab_page(self):
        """
        @return:
        @rtype:
        """
        gitlab_page_dict = {}
        gitlab_page = input(f'Which gitlab page should be used? (e.g {self.gitlab_page}): ')
        print(f'Setting gitlab page: {gitlab_page}')
        gitlab_page_dict["gitlab_page"] = gitlab_page
        return gitlab_page_dict

    def setting_dymola_image_name(self):
        """
        """
        dymola_image_dict = {}
        image_name = input(f'Which docker image should be used? (e.g {self.image_name}): ')
        print(f'Setting dymola version: {image_name}')
        dymola_image_dict["dymola_image"] = image_name
        return dymola_image_dict


class CI_toml_parser(object):

    def __init__(self):
        self.ci_template_toml_file = os.path.join("ci_templates_python", "ci_config", "toml_files",
                                                  "ci_user_template.toml")

    def return_toml_content(self, *args):
        toml_dict = {}
        arg_list = []
        for arg in args:
            if arg is not None:
                arg_list.append(arg)
        toml_dict["CI_setting"] = arg_list
        return toml_dict

    def write_ci_template_toml(self, ci_temp_dict: dict = None):
        if ci_temp_dict is not None:
            with open(self.ci_template_toml_file, "wb") as f:
                tomlwriter.dump(ci_temp_dict, f)
            print(f"Write toml in {self.ci_template_toml_file} ")
        else:
            print("No toml content.")

    def read_ci_template_toml(self):
        _dict = {}
        data = toml.load(self.ci_template_toml_file)
        data = data["CI_setting"]
        for d in data:
            for t in d:
                _dict[t] = d[t]
        return _dict

    def overwrite_arg_parser_toml(self):
        parser_data = argpaser_toml().load_argparser_toml()
        ci_data = self.read_ci_template_toml()
        for ci_group in ci_data:
            for file in parser_data:
                parser_arguments = parser_data[file]["Parser"]
                for arg_group in parser_arguments:
                    if ci_group == arg_group:
                        value = ci_data[ci_group]
                        print(f"Change for parser arguments in file {file} in group {ci_group} with value {value}")
                        parser_data[file]["Parser"][ci_group] = value
        argpaser_toml().overwrite_parser_toml(parser_data=parser_data)


class Parser:
    def __init__(self, args):
        self.args = args

    def main(self):
        parser = argparse.ArgumentParser(description="Set Github Environment Variables")
        check_test_group = parser.add_argument_group("Arguments to set Environment Variables")
        check_test_group.add_argument("--set-setting",
                                      help=f'Create the CI from file Setting{os.sep}CI_setting.txt',
                                      action="store_true")
        check_test_group.add_argument("--write-templates",
                                      default=False,
                                      action="store_true")

        args = parser.parse_args()
        return args


if __name__ == '__main__':
    args = Parser(sys.argv[1:]).main()
    ci_temp = ci_template_config()
    """data_structure().delete_files_path(root=ci_temp.temp_dir,
                                       pattern=".yml",
                                       subfolder=True)"""
    Conf = Read_config_data()

    if args.set_setting is True:
        library_path = {}
        wh_flag_dict = {}
        struc = templates_structure()
        ci_set = settings_ci_interactive()
        file_config_dict = ci_set.setting_ci_templates_types()
        result = ci_set.setting_ci_libraries()
        library_path["root_library"] = result[0]
        libraries = result[1]
        package_dict = ci_set.setting_ci_packages(libraries=result[0])
        dymola_dict = ci_set.setting_ci_dymola_version()
        conda_env = ci_set.setting_ci_python_conda_env()
        wh_library_dict = ci_set.setting_ci_whitelist()
        if wh_library_dict == "None":
            wh_flag_dict["filter_wh_flag"] = False
        else:
            wh_flag_dict["filter_wh_flag"] = True
        changed_dict = ci_set.setting_ci_changed_flag()
        extended_ex_dict = ci_set.extended_simulates()
        github_repo = ci_set.setting_ci_github_repo()
        gitlab_page = ci_set.setting_ci_gitlab_page()
        dymola_image = ci_set.setting_dymola_image_name()
        stage_dict = struc.get_variables(pattern="_stage_", to_group="stages")
        commit_dict = struc.get_variables(pattern="_commit", to_group="ci_commit_message")
        python_file_dict = struc.get_variables(pattern="_commit", to_group="ci_commit_message")
        file_dict = struc.get_toml_var(pattern_1="python", pattern_2="file", to_group="dymola_python_script")
        except_commit_list = struc.get_toml_var(pattern_1="ci_", pattern_2="_commit", to_group="except_commit_list")

        to_parser = CI_toml_parser()
        ci_temp_dict = to_parser.return_toml_content(file_config_dict, dymola_dict, library_path, libraries, package_dict,
                                                     conda_env, wh_library_dict, wh_flag_dict, changed_dict, extended_ex_dict, github_repo, gitlab_page, dymola_image,
                                                     stage_dict, commit_dict, file_dict, except_commit_list)
        to_parser.write_ci_template_toml(ci_temp_dict=ci_temp_dict)
    to_parser = CI_toml_parser()
    to_parser.overwrite_arg_parser_toml()

    if args.write_templates is True:
        data_dict = CI_toml_parser().read_ci_template_toml()
        ci = ci_templates(library=data_dict["library"],
                          package_list=data_dict["package"],
                          dymola_version=data_dict["dymola_version"],
                          python_version=data_dict["conda_environment"],
                          wh_library=data_dict["wh_libraries"],
                          git_url=data_dict["conda_environment"],
                          wh_path=data_dict["conda_environment"],
                          github_repo=data_dict["github_repository"],
                          gitlab_page=data_dict["gitlab_page"],
                          image_name=data_dict["dymola_image"],
                          except_commit_list=data_dict["except_commit_list"],
                          stage_list=data_dict["stages"])
        for temp in data_dict["config_stages"]:
            if temp == "check":
                ci.write_check_template()
                ci.write_OM_check_template()
                pass
            """if temp == "simulate":
                ci.write_simulate_template()
                ci.write_OM_simulate_template()
            if temp == "regression":
                ci.write_regression_template()
            if temp == "html":
                ci.write_html_template()
            if temp == "style":
                ci.write_style_template()
            if temp == "Merge" and data_dict["wh_libraries"] is not None:
                ci.write_merge_template()
        ci.write_ci_whitelist_setting_template()
        ci.write_page_template()
        ci.write_ci_structure_template()
        ci_template_list = ci.get_ci_templates()
        stage_list = ci.get_ci_stages(file_list=ci_template_list)
        ci.write_main_yml(stage_list=stage_list,
                          ci_template_list=ci_template_list)"""
