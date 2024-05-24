import os
from mako.template import Template
import argparse
import toml
import glob
from pathlib import Path
from MoCITempGen import ci_templates_config
from pydantic import Field, field_validator, ValidationInfo
from typing import Optional
from ModelicaPyCI.structure import config_structure


def _arg_list(_list: list):
    return " ".join(_list)


def _arg_dict(_dict: dict):
    if len(_dict) == 1:
        k, v = _dict.popitem()
        if isinstance(v, list):
            return " ".join(v)
        return v
    return " ".join(list(_dict.values()))


def recursive_type(arg):
    """if isinstance(arg, arg.values()):
        print(arg)
    """
    if isinstance(arg, dict):
        for a in arg:
            if isinstance(arg[a], dict):
                pass
            if isinstance(arg[a], list):
                pass
        return recursive_type(arg.values())
    if isinstance(arg, list):
        pass
    else:
        pass


def _recursive_types(args):
    if isinstance(args, dict):
        return _recursive_types(args.values())
    else:
        return args


def load_parser_args(python_module: str):
    import importlib
    import sys
    module = importlib.import_module(python_module)
    try:
        parse_args_function = getattr(module, "parse_args")
    except AttributeError:
        raise ImportError(f"Given module {python_module} has no 'parse_args' function!")
    pars_arg_dict = {}
    sys.argv[1:] = []
    arguments = parse_args_function()
    for args in vars(arguments):
        if getattr(arguments, args) is None or isinstance(getattr(arguments, args), Path):
            pars_arg_dict[args] = str(getattr(arguments, args))
        else:
            pars_arg_dict[args] = getattr(arguments, args)
    return pars_arg_dict


def write_parser_args(
        python_module: str,
        user_args: dict,
        template_script_args: dict,
        skip_args: list = None
):
    arg_parser = load_parser_args(python_module=python_module)
    parser_str = ""
    if skip_args is None:
        skip_args = []
    if template_script_args is None:
        template_script_args = {}
    if user_args is None:
        user_args = {}
    duplicates = set(user_args).intersection(template_script_args)
    if duplicates:
        raise KeyError("user_args and template_script_args have duplicate names, "
                       f"ensure separate names for both. Duplicates: {duplicates}")
    difference = set(template_script_args).difference(arg_parser)
    if difference:
        raise KeyError("template_script_args has names not listed in parse_args, "
                       f"can't use them: {difference}")
    replace_parsers_args_defaults = {**user_args, **template_script_args}
    for var in arg_parser:
        if var in skip_args:
            continue
        value = replace_parsers_args_defaults.get(var, arg_parser[var])
        if value is None or value == "None":
            raise ValueError(f"Parser argument {var} is None, but needs to be set")
        if isinstance(value, bool):
            if value is True:
                arg = f'--{var.replace("_", "-")}  '
            else:
                arg = ""
        elif isinstance(value, dict):
            value_str = _arg_dict(value)
            arg = f'--{var.replace("_", "-")} {value_str} '
        elif isinstance(value, list):
            value_str = _arg_list(value)
            arg = f'--{var.replace("_", "-")} {value_str} '
        else:
            arg = f'--{var.replace("_", "-")} {value} '
        parser_str = arg + parser_str

    return parser_str


def write_multiple_rules(rule_list: list = None,
                         except_string: str = None,
                         rule_option: str = "&&",
                         compare_str: str = "!~",
                         ci_variable: str = None):
    if rule_list is None:
        print("Rule is None")
        exit(1)
    if compare_str == "==":
        syntax = '"'
    else:
        syntax = "/"

    if isinstance(rule_list, dict):
        if except_string is not None:
            _list = []
            for var in rule_list:
                if var != except_string:
                    _list.append(f'{ci_variable}  {compare_str} {syntax}{rule_list[var]}{syntax}')
        else:
            _list = []
            for var in rule_list:
                _list.append(f'{ci_variable}  {compare_str} {syntax}{rule_list[var]}{syntax}')
        rule_string = ""
        for rule in _list:
            if rule == _list[0]:
                rule_string = f'{rule}  '
            else:
                rule_string = f'{rule_string} {rule_option} {rule}'
        return rule_string
    if isinstance(rule_list, list):
        if except_string is not None:
            rule_list = [f'{ci_variable}  {compare_str} {syntax}{value}{syntax}' for value in rule_list if
                         value != except_string]
        else:
            rule_list = [f'{ci_variable}  {compare_str} {syntax}{value}{syntax}' for value in rule_list]
        rule_string = ""
        for rule in rule_list:
            if rule == rule_list[0]:
                rule_string = f'{rule}  '
            else:
                rule_string = f'{rule_string} {rule_option} {rule}'
        return rule_string


class CITemplatesConfig(ci_templates_config.GeneralConfig):
    commit_string: Optional[str] = Field(validate_default=True, default=None)
    pr_main_branch_rule: Optional[str] = Field(validate_default=True, default=None)

    @field_validator("bot_messages")
    @classmethod
    def create_commit_string(cls, commit_string, info: ValidationInfo):
        if commit_string is not None:
            return commit_string
        return write_multiple_rules(
            rule_list=list(info.data["commit_interaction"].dict().values()),
            rule_option="&&",
            compare_str="!~",
            ci_variable="$CI_COMMIT_MESSAGE"
        )

    @field_validator("bot_messages")
    @classmethod
    def create_pr_main_branch_rule(cls, pr_main_branch_rule, info: ValidationInfo):
        if pr_main_branch_rule is not None:
            return pr_main_branch_rule
        return write_multiple_rules(rule_list=info.data["main_branch_list"],
                                    rule_option="||",
                                    compare_str="==",
                                    ci_variable="$CI_COMMIT_BRANCH")

    def to_toml(self, path: Path):
        with open(path, "w+") as file:
            toml.dump(self.dict(), file)
        print(self.dict())

    @staticmethod
    def from_toml(path: Path):
        with open(path, "r") as file:
            return CITemplatesConfig(**toml.load(file))

    def get_utilities_path(self):
        return str(Path(self.templates_dir).joinpath(self.utilities_directory).as_posix())

    def write_OM_check_template(self):
        # out = ["root_library", "library"]
        arg_PR = write_parser_args(
            python_module=self.modelica_py_ci.OM_python_check_model_module,
            user_args=self.dict(),
            template_script_args={"om_options": "OM_CHECK",
                                  })
        arg_push = write_parser_args(
            python_module=self.modelica_py_ci.OM_python_check_model_module,
            user_args=self.dict(),
            template_script_args={"om_options": "OM_CHECK",
                                  "changed_flag": True, })

        template_kwargs = dict(
            utilities_directory=self.get_utilities_path(),
            ci_stage_OM_model_check=self.stage_names.OM_model_check,
            commit_string=self.commit_string,
            library=self.library,
            PR_main_branch_rule=self.pr_main_branch_rule,
            ci_OM_check_commit=self.commit_interaction.OM_check,
            OM_Image=self.open_modelica_image,
            HOME="${HOME}",
            TIMESTAMP="${TIMESTAMP}",
            OM_python_check_model_file=self.modelica_py_ci.OM_python_check_model_module,
            result_dir=self.result.dir,
            expire_in_time=self.expire_in_time,
            arg_PR=arg_PR,
            arg_push=arg_push,
            packages=self.packages[self.library],
            modelicapyci_config_structure_module=self.modelica_py_ci.config_structure_module,
            config_ci_changed_file=self.ci_config_files.changed_file
        )
        self._write_yml_templates(
            file=self.template_files.OM_check_file,
            template_kwargs=template_kwargs
        )

    def write_page_template(self):
        """
        Write page template, deploy artifacts, plots, reference results
        """
        template_kwargs = dict(
            utilities_directory=self.get_utilities_path(),
            image_name=self.dymola_image,
            ci_stage_deploy=self.stage_names.deploy,
            expire_in_time=self.expire_in_time,
            result_dir=self.result.dir,
            PR_main_branch_rule=self.pr_main_branch_rule
        )
        self._write_yml_templates(
            file=self.template_files.page_file,
            template_kwargs=template_kwargs
        )

    def _write_setting_template(self):
        """
        Write setting template, create template with own Syntax
        """
        template_kwargs = dict(
            utilities_directory=self.get_utilities_path(),
            image_name=self.dymola_image,
            github_repo=self.github_repo,
            ci_setting_commit=self.commit_interaction.setting,
            python_version=self.conda_environment,
            ci_stage_check_setting=self.stage_names.check_setting,
            ci_stage_build_templates=self.stage_names.build_templates,
            bot_create_CI_template_commit=self.bot_messages.create_CI_template_commit,
            temp_dir=self.templates_dir
        )
        self._write_yml_templates(
            file=self.template_files.page_file,
            template_kwargs=template_kwargs
        )

    def write_html_template(self):
        arg_PR = write_parser_args(
            python_module=self.modelica_py_ci.html_tidy_module,
            user_args=self.dict(),
            template_script_args={"correct_view_flag": True,
                                  "log_flag": True, "filter_whitelist_flag": True,
                                  "changed_flag": False}, skip_args=["git_url"])
        arg_push = write_parser_args(
            python_module=self.modelica_py_ci.html_tidy_module,
            user_args=self.dict(),
            template_script_args={"correct_view_flag": True,
                                  "log_flag": True, "filter_whitelist_flag": True,
                                  "changed_flag": True}, skip_args=["git_url"])
        arg_wh = write_parser_args(
            python_module=self.modelica_py_ci.html_tidy_module,
            user_args=self.dict(),
            template_script_args={"whitelist_flag": True,
                                  "changed_flag": True}, skip_args=["packages", "library"])
        arg_correct_html = write_parser_args(
            python_module=self.modelica_py_ci.html_tidy_module,
            user_args=self.dict(),
            template_script_args={"whitelist_flag": True,
                                  "changed_flag": True})
        arg_github_PR = write_parser_args(
            python_module=self.modelica_py_ci.api_github_module,
            user_args=self.dict(),
            template_script_args={
                "github_repo": self.github_repository,
                "working_branch": "$CI_COMMIT_REF_NAME",
                "github_token": "$GITHUB_API_TOKEN",
                "create_pr_flag": True,
                "correct_html_flag": True,
                "base_branch": self.main_branch_list[-1]
            },
            skip_args=["gitlab_page", "base_branch"])
        template_kwargs = dict(
            utilities_directory=self.get_utilities_path(),
            image_name=self.dymola_image,
            ci_stage_html_check=self.stage_names.html_check,
            ci_stage_html_whitelist=self.stage_names.html_whitelist,
            ci_stage_open_PR=self.stage_names.open_PR,
            html_praefix=self.html_praefix,
            python_version=self.conda_environment,
            modelicapyci_html_tidy_module=self.modelica_py_ci.html_tidy_module,
            arg_correct_html=arg_correct_html,
            result_dir=self.result.dir,
            expire_in_time=self.expire_in_time,
            commit_string=self.commit_string,
            library=self.library,
            PR_main_branch_rule=self.pr_main_branch_rule,
            ci_html_commit=self.commit_interaction.html,
            modelicapyci_api_github_module=self.modelica_py_ci.api_github_module,
            arg_PR=arg_PR,
            arg_wh=arg_wh,
            arg_github_PR=arg_github_PR,
            arg_push=arg_push,
            bot_create_html_file_commit=self.bot_messages.create_html_file_commit,
            bot_update_whitelist_commit=self.bot_messages.update_whitelist_commit,
            whitelist_html_file=self.whitelist_scripts.html_file,
            ci_create_html_whitelist_commit=self.ci_create_html_whitelist_commit
        )
        self._write_yml_templates(
            file=self.template_files.html_file,
            template_kwargs=template_kwargs
        )

    def write_style_template(self):
        """
        Write Style Check template
        """
        arg_PR = write_parser_args(python_module=self.modelica_py_ci.syntax_test_module,
                                   template_script_args={"changed_flag": False}, skip_args=["packages"])
        arg_push = write_parser_args(
            python_module=self.modelica_py_ci.syntax_test_module,
            user_args=self.dict(),
            template_script_args={"changed_flag": True}, skip_args=["packages"])

        template_kwargs = dict(
            utilities_directory=self.get_utilities_path(),
            image_name=self.dymola_image,
            ci_stage_style_check=self.stage_names.style_check,
            python_version=self.conda_environment,
            modelicapyci_syntax_test_module=self.modelica_py_ci.syntax_test_module,
            xvfb_flag=self.xvfb_flag,
            library=self.library,
            commit_string=self.commit_string,
            PR_main_branch_rule=self.pr_main_branch_rule,
            ci_style_commit=self.ci_style_commit,
            result_dir=self.result.dir,
            arg_PR=arg_PR,
            arg_Push=arg_push)
        self._write_yml_templates(
            file=self.template_files.style_check_file,
            template_kwargs=template_kwargs
        )

    def write_ci_whitelist_setting_template(self):
        template_kwargs = dict(
            utilities_directory=self.get_utilities_path(),
            image_name=self.dymola_image,
            ci_stage_whitelist_setting=self.stage_names.whitelist_setting,
            python_version=self.conda_environment,
            modelicapyci_config_structure_module=self.modelica_py_ci.config_structure_module,
            arg_struc_wh=2,
            arg_whitelist_check=2,
            modelicapyci_html_tidy_module=self.modelica_py_ci.html_tidy_module,
            arg_whitelist_html=2,
            arg_whitelist_sim=2,
            bot_build_whitelist_commit=self.bot_messages.build_whitelist_commit,
            dymola_ci_test_dir=self.dymola_ci_test_dir,
            ci_build_whitelist_structure_commit=self.commit_interaction.build_whitelist_structure,
            expire_in_time=self.expire_in_time,
            xvfb_flag=self.xvfb_flag,
            modelicapyci_configuration_module=self.modelica_py_ci.configuration_module,
            modelicapyci_test_validate_module=self.modelica_py_ci.test_validate_module
        )
        self._write_yml_templates(
            file=self.template_files.build_whitelist_file,
            template_kwargs=template_kwargs
        )

    def write_merge_template(self):
        """
        Write (IBPSA) Merge template
        """
        merge_branch = f'Custom{self.whitelist_library_config.library}_Merge'
        merge_library_dir = f"{self.whitelist_library_config.library}_folder"

        arg_whitelist_html = write_parser_args(
            python_module=self.modelica_py_ci.create_whitelist_module,
            user_args=self.dict(),
            template_script_args={
                "whitelist_library": self.whitelist_library_config.library,
                "git_url": self.whitelist_library_config.git_url,
                "root_whitelist_library": self.whitelist_library_config.local_path,
            }, skip_args=["packages"]
        )
        arg_lib = write_parser_args(
            python_module=self.modelica_py_ci.library_merge_module,
            user_args=self.dict(),
            template_script_args={
                "merge_library_dir": merge_library_dir,
                "library_dir": f"temp_{self.library}"
            }
        )
        arg_whitelist_check_sim = write_parser_args(
            python_module=self.modelica_py_ci.test_validate_module,
            user_args=self.dict(),
            template_script_args={
                "whitelist_library": self.whitelist_library_config.library,
                "git_url": self.whitelist_library_config.git_url,
                "root_whitelist_library": self.whitelist_library_config.local_path,
                "create_whitelist_flag": True,
                "library_package_mo": f"{self.library}/{self.library}/package.mo",
                "dym_options": ["DYM_SIM", "DYM_CHECK"]}
        )
        arg_lock = write_parser_args(
            python_module=self.modelica_py_ci.lock_model_module,
            user_args=self.dict(),
            template_script_args={
                "lock_library": self.whitelist_library_config.library
            })

        arg_api_pr = write_parser_args(
            python_module=self.modelica_py_ci.api_github_module,
            user_args=self.dict(),
            template_script_args={
                "create_pr_flag": True,
                "ibpsa_merge_flag": True,
                "base_branch": self.main_branch_list[-1]
            }
        )

        template_kwargs = dict(
            utilities_directory=self.get_utilities_path(),
            image_name=self.dymola_image,
            ci_stage_lib_merge=self.stage_names.lib_merge,
            ci_stage_update_whitelist=self.stage_names.update_whitelist,
            ci_stage_open_PR=self.stage_names.open_PR,
            python_version=self.conda_environment,
            git_url=self.whitelist_library_config.git_url,
            merge_library_dir=merge_library_dir,
            library=self.library,
            merge_branch=merge_branch,
            modelicapyci_lock_model_module=self.modelica_py_ci.lock_model_module,
            modelicapyci_library_merge_module=self.modelica_py_ci.library_merge_module,
            arg_lib=arg_lib,
            ci_trigger_ibpsa_commit=self.commit_interaction.trigger_ibpsa,
            expire_in_time=self.expire_in_time,
            modelicapyci_create_whitelist_module=self.modelica_py_ci.create_whitelist_module,
            arg_whitelist_html=arg_whitelist_html,
            arg_whitelist_check_sim=arg_whitelist_check_sim,
            modelicapyci_test_validate_module=self.modelica_py_ci.test_validate_module,
            xvfb_flag=self.xvfb_flag,
            arg_lock=arg_lock,
            whitelist_library=self.whitelist_library_config.library,
            bot_merge_commit=self.bot_messages.merge_commit,
            result_dir=self.result.dir,
            modelicapyci_api_github_module=self.modelica_py_ci.api_github_module,
            arg_api_pr=arg_api_pr
        )

        self._write_yml_templates(
            file=self.template_files.ibpsa_merge_file,
            template_kwargs=template_kwargs
        )

    def _write_yml_templates(self, file: str, template_kwargs: dict):
        ci_temp = Path(self.template_files.base, file)
        print(f"Write {ci_temp}")
        my_template = Template(strict_undefined=True, filename=str(ci_temp))
        yml_text = my_template.render(**template_kwargs)
        ci_folder = Path(self.library_path, self.templates_dir, file).parent
        config_structure.create_path(ci_folder)
        with open(ci_folder.joinpath(Path(file).name.replace(".txt", ".gitlab-ci.yml")), "w") as yml_tmp:
            yml_tmp.write(yml_text.replace('\n', ''))

    def write_regression_template(self):
        arg_PR = write_parser_args(
            python_module=self.modelica_py_ci.test_reference_module,
            user_args=self.dict(),
            template_script_args={"batch": True, "changed_flag": False
                                  })
        arg_push = write_parser_args(
            python_module=self.modelica_py_ci.test_reference_module,
            user_args=self.dict(),
            template_script_args={"batch": True,
                                  })
        coverage_arg = write_parser_args(
            python_module=self.modelica_py_ci.test_reference_module,
            user_args=self.dict(),
            template_script_args={"coverage_only": True,
                                  "batch": False,
                                  "changed_flag": False})

        arg_ref_check = write_parser_args(
            python_module=self.modelica_py_ci.test_reference_module,
            user_args=self.dict(),
            template_script_args={"create_ref": True,
                                  "dymola_version": self.dymola_version,
                                  "batch": False,
                                  "changed_flag": False},
            skip_args=["packages", "path", "root_library"])

        arg_create_plots = write_parser_args(
            python_module=self.modelica_py_ci.google_chart_module,
            user_args=self.dict(),
            template_script_args={"create_layout_flag": True,
                                  "library": self.library, "funnel_comp_flag": False,
                                  "error_flag": False, "line_html_flag": False})
        arg_chart = write_parser_args(
            python_module=self.modelica_py_ci.google_chart_module,
            user_args=self.dict(),
            template_script_args={"funnel_comp_flag": True,
                                  "line_html_flag": True, "error_flag": True})

        api_github_arg = write_parser_args(
            python_module=self.modelica_py_ci.api_github_module,
            user_args=self.dict(),
            template_script_args={"working_branch": "$CI_COMMIT_REF_NAME",
                                  "github_token": "${GITHUB_API_TOKEN}",
                                  "post_pr_comment_flag": True,
                                  "prepare_plot_flag": True})

        arg_ref = write_parser_args(
            python_module=self.modelica_py_ci.test_reference_module,
            user_args=self.dict(),
            template_script_args={"create_ref_flag": True})
        arg_check_ref_plot = write_parser_args(
            python_module=self.modelica_py_ci.google_chart_module,
            user_args=self.dict(),
            template_script_args={"line_html_flag": True, "package": self.library,
                                  "funnel_comp_flag:": False, "create_layout_flag": False,
                                  "error_flag": False, "new_ref": True,
                                  "funnel_comp_flag": False, "new_ref_flag": True},
            skip_args=["packages"])
        # python ${modelicapyci_google_chart_file} - -line - html - -new - ref - -packages ${library};

        template_kwargs = dict(
            utilities_directory=self.get_utilities_path(),
            dym_image=self.dymola_image,
            coverage_arg=coverage_arg,
            ci_stage_regression_test=self.stage_names.regression_test,
            ci_stage_ref_check=self.stage_names.ref_check,
            ci_stage_plot_ref=self.stage_names.plot_ref,
            ci_stage_prepare=self.stage_names.prepare,
            python_version=self.conda_environment,
            arg_ref_check=arg_ref_check,
            buildingspy_upgrade=self.buildingspy_upgrade,
            modelicapyci_test_reference_module=self.modelica_py_ci.test_reference_module,
            modelicapyci_google_chart_module=self.modelica_py_ci.google_chart_module,
            config_ci_exit_file=self.ci_config_files.exit_file,
            result_dir=self.result.dir,
            arg_chart=arg_chart,
            ci_regression_test_commit=self.ci_regression_test_commit,
            expire_in_time=self.expire_in_time,
            arg_PR=arg_PR,
            arg_push=arg_push,
            PR_main_branch_rule=self.pr_main_branch_rule,
            commit_string=self.commit_string,
            package_list=self.packages[self.library],
            modelicapyci_api_github_module=self.modelica_py_ci.api_github_module,
            arg_create_plots=arg_create_plots,
            api_github_arg=api_github_arg,
            library=self.library,
            xvfb_flag=self.xvfb_flag,
            modelicapyci_structure_module=self.modelica_py_ci.config_structure_module,
            arg_ref=arg_ref,
            config_ci_eof_file=self.ci_config_files.eof_file,
            config_ci_new_create_ref_file=self.ci_config_files.new_create_ref_file,
            bot_create_ref_commit=self.bot_messages.create_ref_commit,
            ci_show_ref_commit=self.ci_show_ref_commit,
            arg_check_ref_plot=arg_check_ref_plot,
            ci_reference_check=self.ci_reference_check)
        self._write_yml_templates(
            file=self.template_files.regression_file,
            template_kwargs=template_kwargs
        )

    def write_OM_simulate_template(self):
        arg_PR = write_parser_args(python_module=self.modelica_py_ci.OM_python_check_model_module,
                                   template_script_args={"om_options": "OM_SIM",
                                                         "changed_flag": False})
        arg_push = write_parser_args(
            python_module=self.modelica_py_ci.OM_python_check_model_module,
            user_args=self.dict(),
            template_script_args={"om_options": "OM_SIM",
                                  })

        template_kwargs = dict(
            utilities_directory=self.get_utilities_path(),
            ci_stage_OM_simulate=self.stage_names.OM_simulate,
            commit_string=self.commit_string,
            library=self.library,
            PR_main_branch_rule=self.pr_main_branch_rule,
            ci_OM_sim_commit=self.commit_interaction.OM_simulate,
            OM_python_check_model_module=self.modelica_py_ci.OM_python_check_model_module,
            arg_PR=arg_PR,
            arg_push=arg_push,
            result_dir=self.result.dir,
            OM_Image=self.open_modelica_image,
            expire_in_time=self.expire_in_time,
            packages=self.packages[self.library],
            modelicapyci_config_structure_module=self.modelica_py_ci.config_structure_module,
            config_ci_changed_file=self.ci_config_files.changed_file)
        self._write_yml_templates(
            file=self.template_files.OM_simulate_file,
            template_kwargs=template_kwargs
        )

    def write_check_template(self):
        arg_PR = write_parser_args(
            python_module=self.modelica_py_ci.test_validate_module,
            user_args=self.dict(),
            template_script_args={"dym_options": "DYM_CHECK",
                                  },
            skip_args=["repo_dir", "git_url"])
        arg_push = write_parser_args(
            python_module=self.modelica_py_ci.test_validate_module,
            user_args=self.dict(),
            template_script_args={"dym_options": "DYM_CHECK", },
            skip_args=["repo_dir", "git_url"])

        arg_wh = write_parser_args(
            python_module=self.modelica_py_ci.test_validate_module,
            user_args=self.dict(),
            template_script_args={"dym_options": "DYM_CHECK",
                                  "create_whitelist_flag": True,
                                  "filter_whitelist_flag": False,
                                  },
            skip_args=["root_library", "packages"])

        template_kwargs = dict(
            utilities_directory=self.get_utilities_path(),
            dym_image_name=self.dymola_image,
            ci_stage_model_check=self.stage_names.dymola_model_check,
            ci_stage_create_whitelist=self.stage_names.create_whitelist,
            commit_string=self.commit_string,
            library=self.library,
            PR_main_branch_rule=self.pr_main_branch_rule,
            ci_check_commit=self.ci_check_commit,
            xvfb_flag=self.xvfb_flag,
            modelicapyci_test_validate_module=self.modelica_py_ci.test_validate_module,
            result_dir=self.result.dir,
            expire_in_time=self.expire_in_time,
            arg_push=arg_push,
            arg_wh=arg_wh,
            arg_PR=arg_PR,
            package_list=self.packages[self.library],
            config_ci_exit_file=self.ci_config_files.exit_file,
            bot_update_model_whitelist_commit=self.bot_messages.update_model_whitelist_commit,
            whitelist_model_file=self.whitelist_scripts.check_file,
            python_version=self.conda_environment,
            ci_create_model_whitelist_commit=self.ci_create_model_whitelist_commit,
            config_ci_changed_file=self.ci_config_files.changed_file,
            modelicapyci_config_structure_module=self.modelica_py_ci.config_structure_module
        )
        self._write_yml_templates(
            file=self.template_files.check_file,
            template_kwargs=template_kwargs
        )

    def write_simulate_template(self):
        arg_PR = write_parser_args(
            python_module=self.modelica_py_ci.test_validate_module,
            user_args=self.dict(),
            template_script_args={"dym_options": "DYM_SIM",
                                  "changed_flag": False})
        arg_push = write_parser_args(
            python_module=self.modelica_py_ci.test_validate_module,
            user_args=self.dict(),
            template_script_args={"dym_options": "DYM_SIM",
                                  })
        arg_wh = write_parser_args(
            python_module=self.modelica_py_ci.test_validate_module,
            user_args=self.dict(),
            template_script_args={"dym_options": "DYM_SIM",
                                  "create_whitelist_flag": True,
                                  "changed_flag": False})

        template_kwargs = dict(
            utilities_directory=self.get_utilities_path(),
            dym_image_name=self.dymola_image,
            ci_stage_simulate=self.stage_names.simulate,
            ci_stage_create_exampeL_whitelist=self.stage_names.create_example_whitelist,
            modelicapyci_config_structure_module=self.modelica_py_ci.config_structure_module,
            arg_push=arg_push,
            config_ci_changed_file=self.ci_config_files.changed_file,
            arg_PR=arg_PR,
            commit_string=self.commit_string,
            PR_main_branch_rule=self.pr_main_branch_rule,
            library=self.library,
            ci_check_commit=self.ci_simulate_commit,
            python_version=self.conda_environment,
            modelicapyci_test_validate_module=self.modelica_py_ci.test_validate_module,
            package_list=self.packages[self.library],
            arg_wh=arg_wh,
            bot_update_model_whitelist_commit=self.bot_messages.update_example_whitelist_commit,
            whitelist_model_file=self.whitelist_scripts.simulate_file,
            ci_create_model_whitelist_commit=self.ci_create_simulate_whitelist_commit,
            result_dir=self.result.dir,
            expire_in_time=self.expire_in_time,
            xvfb_flag=self.xvfb_flag,
            config_ci_exit_file=self.ci_config_files.exit_file,
            ci_stage_create_whitelist=self.stage_names.create_whitelist)
        self._write_yml_templates(
            file=self.template_files.simulate_file,
            template_kwargs=template_kwargs
        )

    def write_toml_settings(self):
        with open(self.toml_ci_setting_file, "w") as file:
            toml.dump(self.dict(), file)
        print(f'The CI settings are saved in file {self.toml_ci_setting_file}')

    def write_main_yml(self, stage_list, ci_template_list):
        ci_template_list = [file.replace(self.library_path + "/", "") for file in ci_template_list]

        template_kwargs = dict(
            image_name=self.dymola_image,
            stage_list=stage_list,
            github_repository=self.github_repository,
            gitlab_page=self.gitlab_page,
            file_list=ci_template_list)
        self._write_yml_templates(
            file=self.template_files.main_yml_file,
            template_kwargs=template_kwargs
        )

    def write_utilities_yml(self):
        template_kwargs = dict(
            conda_environment=self.conda_environment,
            modelica_py_ci_url=self.modelica_py_ci.url
        )
        self._write_yml_templates(
            file=self.template_files.utilities_file,
            template_kwargs=template_kwargs
        )

    def get_ci_templates(self):
        path = Path(self.library_path).joinpath(self.templates_dir)
        py_f = glob.glob(f'{path}/**/*.yml', recursive=True)
        mo_py_files = []
        for file in py_f:
            if file.find(".gitlab-ci.yml") > -1:
                mo_py_files.append(file.replace(os.sep, "/"))
        return mo_py_files


def get_ci_stages(file_list):
    stage_list = []
    for file in file_list:
        with open(file, "r") as infile:
            lines = infile.readlines()
        stage_content = False
        for line in lines:
            line = line.strip()
            if len(line.strip()) != 0:
                if line.find("stages:") > -1:
                    stage_content = True
                elif line.find(":") > -1 and line.find("stages:") == -1:
                    stage_content = False
                elif stage_content is True:
                    stage = line.replace("-", "").replace(" ", "")
                    if stage not in stage_list:
                        stage_list.append(stage)
    if len(stage_list) == 0:
        print(f'No stages')
        exit(1)
    if "deploy" in stage_list:
        stage_list.remove("deploy")
        stage_list.append("deploy")
    for stage in stage_list:
        print(f'Setting stages: {stage}')
    return stage_list


def yes_no_input(message):
    while True:
        response = input(f'{message} (y/n)')
        if response not in ["y", "n"]:
            print("Invalid option, try again ...")
        else:
            break
    return response == "y"


def input_with_default(message, default):
    response = input(f'{message} (example: "{default}" - leave empty to use the example):')
    if not response:
        return default
    return response


def setting_ci_templates_types():
    stages_list = []
    yes = yes_no_input('Config template: Check html Syntax in models?')
    if yes:
        print(f'Create html template')
        stages_list.append("html")
    yes = yes_no_input('Config template: Check style of models?')
    if yes:
        print(f'Create style template')
        stages_list.append("style")
    yes = yes_no_input('Config template: Check models?')
    if yes:
        print(f'Create check template')
        stages_list.append("check")
    yes = yes_no_input('Config template: Simulate examples?')
    if yes:
        print(f'Create simulate template')
        stages_list.append("simulate")
    yes = yes_no_input('Config template: Regression test?')
    if yes:
        print(f'Create regression template')
        stages_list.append("regression")
    yes = yes_no_input('Config template: Merge Update?')
    if yes:
        print(f'Create merge template')
        stages_list.append("Merge")
    print(f"Setting stages list: {stages_list}")
    return stages_list


def setting_ci_libraries():
    library = input_with_default(message='Which library should be tested?', default="AixLib")
    path_library = input(
        f'Path of library? (If the library is located in the directory, do not enter an entry.)'
    )
    lib_path = Path(path_library).joinpath(library, "package.mo")
    config_structure.check_file_setting(lib_path)
    print(f'Setting library root: {lib_path}')
    print(f'Setting library : {library}')
    return lib_path, library


def setting_ci_packages(library: str, library_path: Path):
    packages = {}
    package_list = []
    package_lib = []
    print(f'**** Library {library} ****')
    for package in os.listdir(Path(library_path).parent):
        if package.find(".") == -1:
            package_list.append(package)
    if package_list is None:
        print(f'Dont find library {library}')
        exit(1)
    for package in package_list:
        yes = yes_no_input(f'Test package {package} in library {library}?')
        if yes:
            package_lib.append(package)
            continue
    packages[library] = package_lib
    print(f'Setting packages: {packages}')
    return packages


def setting_ci_dymola_version():
    dymola_version = input_with_default(message='Give the dymola version?', default="2022")
    print(f'Setting dymola version: {dymola_version}')
    return dymola_version


def setting_ci_python_conda_env():
    conda_environment = input_with_default(message="Give the conda environment in your image", default="myenv")
    print(f'Setting conda environment: {conda_environment}')
    return conda_environment


def extended_simulates():
    extended_ex_flag = yes_no_input('Should examples be searched recursively?')
    print(f'Setting extended_ex_flag: {extended_ex_flag}')
    return extended_ex_flag


def setting_ci_changed_flag():
    changed_flag = yes_no_input('Should only new or modified models from the last commit be tested?')
    print(f'Setting changed_flag: {changed_flag}')
    return changed_flag


def setting_ci_whitelist():
    yes = yes_no_input(
        f'Create whitelist? '
        f'Useful if your own library has been assembled from other libraries. '
        f'A whitelist is created, where faulty models from the foreign library are no '
        f'longer tested in the future and are filtered out.'
    )
    if not yes:
        return None
    # Else
    whitelist_library = input_with_default(
        message='What library models should on whitelist: Give the name of the library',
        default="IBPSA"
    )
    print(f'Setting whitelist library: {whitelist_library}')
    locally_available = yes_no_input(f'If the foreign library is local on the PC?')
    lib_path = "modelica-ibpsa"
    if locally_available:
        whitelist_path = input(
            f'Specify the local path of the library (e.g. ..\..\IBPSA). '
            f'(If the library is located in the directory, do not enter an entry.) '
        )
        lib_path = os.path.join(whitelist_path, whitelist_library, "package.mo").replace(os.sep, "/")
        config_structure.check_file_setting(lib_path)
        print(f'path of library: {lib_path}')
    git_url = input_with_default(
        message='Give the url of the library repository',
        default="https://github.com/ibpsa/modelica-ibpsa.git"
    )
    print(f'Setting git_url: {git_url}')
    repo_dir = input_with_default(
        message='Give the repository name',
        default="modelica-ibpsa"
    )
    print(f'Setting repo_dir: {repo_dir}')
    return ci_templates_config.WhitelistAndMergeLibraryConfig(
        library=whitelist_library,
        local_path=lib_path,
        git_url=git_url
    )


def setting_ci_github_repo():
    github_repository = input_with_default(
        message=f'Which github repository in your CI should be used? ',
        default="RWTH-EBC/AixLib"
    )
    print(f'Setting github repository: {github_repository}')
    return github_repository


def setting_ci_gitlab_page():
    gitlab_page = input_with_default(
        message='Which gitlab page should be used?',
        default="https://ebc.pages.rwth-aachen.de/EBC_all/github_ci/AixLib"
    )
    print(f'Setting gitlab page: {gitlab_page}')
    return gitlab_page


def setting_dymola_image_name():
    dymola_image = input_with_default(
        message=f'Which docker image should be used? ',
        default="registry.git.rwth-aachen.de/ebc/ebc_intern/dymola-docker:Dymola_2022-miniconda"
    )
    print(f'Setting dymola version: {dymola_image}')
    return dymola_image


def overwrite_args_parser_toml(ci_parser_toml: Path, ci_templates_toml: Path):
    with open(ci_parser_toml, "r") as file:
        parser_data = toml.load(file)
    ci_templates_config = CITemplatesConfig.from_toml(path=ci_templates_toml).dict()
    for file in parser_data:
        parser_arguments = parser_data[file]
        for arg_group in parser_arguments:
            value = None
            for ci_group in ci_templates_config:
                value = None
                if ci_group == arg_group:
                    if isinstance(ci_templates_config[ci_group], dict):
                        if ci_group == "whitelist_library":
                            value = ci_templates_config[ci_group].keys()
                            pass
                        else:
                            for l in ci_templates_config[ci_group]:
                                if isinstance(ci_templates_config[ci_group][l], list):
                                    value = ci_templates_config[ci_group][l]
                                else:
                                    value = ci_templates_config[ci_group].values()
                    else:
                        value = ci_templates_config[ci_group]
                if value is not None:
                    print(f"Change for parser arguments in file {file} in group {arg_group} with value {value}")
                    parser_data[file][arg_group] = value

            if arg_group == "git_url":
                for wh in ci_templates_config["whitelist_library"]:
                    value = ci_templates_config["whitelist_library"][wh][arg_group]

            elif arg_group == "repo_dir":
                for wh in ci_templates_config["whitelist_library"]:
                    value = ci_templates_config["whitelist_library"][wh][arg_group]
            if value is not None:
                print(f"Change for parser arguments in file {file} in group {arg_group} with value {value}")
                parser_data[file][arg_group] = value
    with open(ci_parser_toml, "w") as file:
        toml.dump(parser_data, file)


def parse_args():
    parser = argparse.ArgumentParser(description="Set Github Environment Variables")
    check_test_group = parser.add_argument_group("Arguments to set Environment Variables")
    check_test_group.add_argument("--set-setting",
                                  help=f'Create the CI from file Setting{os.sep}CI_setting.txt',
                                  action="store_true")
    check_test_group.add_argument("--write-templates",
                                  default=False,
                                  action="store_true")
    check_test_group.add_argument("--update-toml",
                                  default=False,
                                  action="store_true")

    return parser.parse_args()


def get_toml_var(self, pattern_1: str, pattern_2: str, to_group: str):
    _list = {}
    var_dict = vars(CITemplatesConfig())
    _dict = {}
    for var in var_dict:
        if var.find(pattern_1) > -1 and var.find(pattern_2) > -1:
            _list[var] = var_dict[var]
    _dict[to_group] = _list
    return _dict


def create_toml_config(path):
    library_path, library = setting_ci_libraries()

    whitelist_library = setting_ci_whitelist()
    package_list = setting_ci_packages(library=library, library_path=library_path)
    stage_list = setting_ci_templates_types()
    conda_environment = setting_ci_python_conda_env()
    dymola_version = setting_ci_dymola_version()
    github_repository = setting_ci_github_repo()
    gitlab_page = setting_ci_gitlab_page()
    dymola_image = setting_dymola_image_name()
    changed_flag = setting_ci_changed_flag()
    extended_examples_flag = extended_simulates()

    CITemplatesConfig(
        stage_list=stage_list,
        library=library,
        library_path=library_path,
        package_list=package_list,
        whitelist_library=whitelist_library,
        conda_environment=conda_environment,
        dymola_version=dymola_version,
        github_repository=github_repository,
        gitlab_page=gitlab_page,
        dymola_image=dymola_image,
        changed_flag=changed_flag,
        extended_examples_flag=extended_examples_flag,
        template_files=ci_templates_config.TemplateFilesConfig(base=Path(__file__).parents[1].absolute())
    ).to_toml(path=path)


def write_templates(path: Path):
    ci_templates_config = CITemplatesConfig.from_toml(path=path)

    for temp in ci_templates_config.stage_list:
        if temp == "check":
            ci_templates_config.write_check_template()
            ci_templates_config.write_OM_check_template()
        if temp == "simulate":
            ci_templates_config.write_simulate_template()
            ci_templates_config.write_OM_simulate_template()
        if temp == "regression":
            ci_templates_config.write_regression_template()
        if temp == "html":
            ci_templates_config.write_html_template()
        if temp == "style":
            ci_templates_config.write_style_template()
        if temp == "Merge" and ci_templates_config.whitelist_library_config is not None:
            ci_templates_config.write_merge_template()
    # ci_templates_config.write_ci_whitelist_setting_template()
    ci_templates_config.write_page_template()
    ci_template_list = ci_templates_config.get_ci_templates()
    stage_list = get_ci_stages(file_list=ci_template_list)
    ci_templates_config.write_utilities_yml()
    ci_templates_config.write_main_yml(stage_list=stage_list, ci_template_list=ci_template_list)


if __name__ == '__main__':
    args = parse_args()
    TEMPLATES_TOML_FILE = Path(__file__).parent.joinpath(
        "ci_config", "toml_files", "ci_user_template.toml"
    )
    PARSER_TOML_FILE = Path(__file__).parent.joinpath(
        "ci_config", "toml_files", "parser.toml"
    )
    # create_toml_config(path=TEMPLATES_TOML_FILE)
    write_templates(path=TEMPLATES_TOML_FILE)

    if args.set_setting is True:
        create_toml_config(path=TEMPLATES_TOML_FILE)
    if args.update_toml:
        overwrite_args_parser_toml(
            ci_parser_toml=PARSER_TOML_FILE,
            ci_templates_toml=TEMPLATES_TOML_FILE
        )
    if args.write_templates is True:
        write_templates(path=TEMPLATES_TOML_FILE)
