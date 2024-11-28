import argparse
import os
import shutil
import glob
from pathlib import Path

import toml
from mako.template import Template

from MoCITempGen.ci_templates_config import TemplateGeneratorConfig, WhitelistAndMergeLibraryConfig, TemplateFilesConfig
from ModelicaPyCI.config import CIConfig, save_toml_config, load_toml_config
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


def convert_packages_per_job(packages_per_job):
    return {job: " ".join(packages) for job, packages in packages_per_job.items()}

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
        skip_args: list = None,
        overwrite_user_args_with_template_args: bool = False
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
    if duplicates and not overwrite_user_args_with_template_args:
        raise KeyError("user_args and template_script_args have duplicate names, "
                       f"ensure separate names for both. Duplicates: {duplicates}")
    difference = set(template_script_args).difference(arg_parser)
    if difference:
        raise KeyError("template_script_args has names not listed in parse_args, "
                       f"can't use them: {difference}")
    replace_parsers_args_defaults = {**user_args}
    replace_parsers_args_defaults.update(template_script_args)
    for var in arg_parser:
        if var in skip_args:
            continue
        value = replace_parsers_args_defaults.get(var, arg_parser[var])
        if value is None:
            if arg_parser[var] == "None":
                # Default which must not be set:
                continue
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


def get_utilities_path(templates_config: TemplateGeneratorConfig):
    return Path(templates_config.templates_store_folder).joinpath(
        templates_config.template_scripts_dir, templates_config.utilities_directory
    ).as_posix()


def get_result_dir_path_for_pages(ci_config: CIConfig):
    return ci_config.get_dir_path("result").as_posix()


def write_OM_check_template(templates_config: TemplateGeneratorConfig, ci_config: CIConfig):
    arg_push = write_parser_args(
        python_module=templates_config.modelica_py_ci.OM_python_check_model_module,
        user_args=templates_config.dict(),
        template_script_args={
            "packages": ["$lib_package"],
            "om_options": "OM_CHECK",
        },
        overwrite_user_args_with_template_args=True
    )
    arg_changed = write_parser_args(
        python_module=templates_config.modelica_py_ci.OM_python_check_model_module,
        user_args=templates_config.dict(),
        template_script_args={
            "packages": ["$lib_package"],
            "om_options": "OM_CHECK",
            "changed_flag": True
        },
        overwrite_user_args_with_template_args=True
    )

    template_kwargs = dict(
        utilities_directory=get_utilities_path(templates_config=templates_config),
        ci_stage_OM_model_check=templates_config.stage_names.OM_model_check,
        library=templates_config.library,
        ci_OM_check_commit=templates_config.commit_interaction.OM_check,
        OM_Image=templates_config.open_modelica_image,
        HOME="${HOME}",
        TIMESTAMP="${TIMESTAMP}",
        OM_python_check_model_module=templates_config.modelica_py_ci.OM_python_check_model_module,
        result_dir=get_result_dir_path_for_pages(ci_config=ci_config),
        expire_in_time=templates_config.expire_in_time,
        arg_push=arg_push,
        arg_changed=arg_changed,
        packages_per_job=convert_packages_per_job(templates_config.packages_per_job),
        modelicapyci_config_structure_module=templates_config.modelica_py_ci.config_structure_module
    )
    _write_yml_templates(
        templates_config=templates_config, ci_config=ci_config,
        file=templates_config.template_files.OM_check_file,
        template_kwargs=template_kwargs
    )


def write_prepare_page_template(templates_config: TemplateGeneratorConfig, ci_config: CIConfig):
    """
    Write page template, deploy artifacts, plots, reference results
    """
    template_kwargs = dict(
        ci_stage_prepare_page=templates_config.stage_names.prepare_pages,
        expire_in_time=templates_config.expire_in_time,
        result_dir=get_result_dir_path_for_pages(ci_config=ci_config),
        utilities_directory=get_utilities_path(templates_config=templates_config)
    )
    _write_yml_templates(
        templates_config=templates_config, ci_config=ci_config,
        file=templates_config.template_files.page_file,
        template_kwargs=template_kwargs
    )


def write_ci_pr_interact_template(templates_config: TemplateGeneratorConfig, ci_config: CIConfig):
    arg = write_parser_args(
        python_module=templates_config.modelica_py_ci.api_github_module,
        user_args=templates_config.dict(),
        template_script_args={"post_initial_pr_comment": True}
    )
    template_kwargs = dict(
        utilities_directory=get_utilities_path(templates_config=templates_config),
        ci_stage_post_pr=templates_config.stage_names.post_initial_pr_comment,
        modelicapyci_api_github_module=templates_config.modelica_py_ci.api_github_module,
        arg=arg
    )
    _write_yml_templates(
        templates_config=templates_config, ci_config=ci_config,
        file=templates_config.template_files.ci_pr_interact_comment_file,
        template_kwargs=template_kwargs
    )


def write_html_template(templates_config: TemplateGeneratorConfig, ci_config: CIConfig):
    arg_push = write_parser_args(
        python_module=templates_config.modelica_py_ci.html_tidy_module,
        user_args=templates_config.dict(),
        template_script_args={"correct_view_flag": True,
                              "log_flag": True, "filter_whitelist_flag": True},
        skip_args=["git_url"]
    )
    arg_changed = write_parser_args(
        python_module=templates_config.modelica_py_ci.html_tidy_module,
        user_args=templates_config.dict(),
        template_script_args={"correct_view_flag": True,
                              "log_flag": True, "filter_whitelist_flag": True
                              },
        skip_args=["git_url"])
    arg_wh = write_parser_args(
        python_module=templates_config.modelica_py_ci.html_tidy_module,
        user_args=templates_config.dict(),
        template_script_args={"filter_whitelist_flag": True},
        skip_args=["packages", "library"])
    arg_correct_html = write_parser_args(
        python_module=templates_config.modelica_py_ci.html_tidy_module,
        user_args=templates_config.dict(),
        template_script_args={
            "filter_whitelist_flag": True,
            "correct_overwrite_flag": True,
            "log_flag": True
        }
    )
    arg_github_PR = write_parser_args(
        python_module=templates_config.modelica_py_ci.api_github_module,
        user_args=templates_config.dict(),
        template_script_args={
            "working_branch": "$CI_COMMIT_REF_NAME",
            "github_token": "$GITHUB_API_TOKEN",
            "create_pr_flag": True,
            "correct_html_flag": True
        },
        skip_args=["page"])
    template_kwargs = dict(
        utilities_directory=get_utilities_path(templates_config=templates_config),
        image_name=templates_config.dymola_image,
        ci_stage_html_check=templates_config.stage_names.html_check,
        ci_stage_html_whitelist=templates_config.stage_names.html_whitelist,
        ci_stage_open_PR=templates_config.stage_names.open_PR,
        html_praefix=templates_config.html_praefix,
        arg_correct_html=arg_correct_html,
        config_ci_exit_file=ci_config.get_file_path("ci_files", "exit_file").as_posix(),
        result_dir=get_result_dir_path_for_pages(ci_config=ci_config),
        expire_in_time=templates_config.expire_in_time,
        library=templates_config.library,
        ci_html_commit=templates_config.commit_interaction.html,
        modelicapyci_html_tidy_module=templates_config.modelica_py_ci.html_tidy_module,
        modelicapyci_api_github_module=templates_config.modelica_py_ci.api_github_module,
        arg_push=arg_push,
        arg_wh=arg_wh,
        arg_github_PR=arg_github_PR,
        arg_changed=arg_changed,
        bot_create_html_file_commit=templates_config.bot_messages.create_html_file_commit,
        bot_update_whitelist_commit=templates_config.bot_messages.update_whitelist_commit,
        whitelist_html_file=ci_config.whitelist.ibpsa_file,
        ci_create_html_whitelist_commit=templates_config.commit_interaction.create_html_whitelist
    )
    _write_yml_templates(
        templates_config=templates_config, ci_config=ci_config,
        file=templates_config.template_files.html_file,
        template_kwargs=template_kwargs
    )


def write_style_template(templates_config: TemplateGeneratorConfig, ci_config: CIConfig):
    """
    Write Style Check template
    """
    arg_push = write_parser_args(
        python_module=templates_config.modelica_py_ci.syntax_test_module,
        template_script_args={"changed_flag": False},
        user_args=templates_config.dict()
    )
    arg_changed = write_parser_args(
        python_module=templates_config.modelica_py_ci.syntax_test_module,
        user_args=templates_config.dict(),
        template_script_args={"changed_flag": True}
    )

    template_kwargs = dict(
        utilities_directory=get_utilities_path(templates_config=templates_config),
        image_name=templates_config.dymola_image,
        ci_stage_style_check=templates_config.stage_names.style_check,
        modelicapyci_syntax_test_module=templates_config.modelica_py_ci.syntax_test_module,
        xvfb_flag=templates_config.xvfb_flag,
        library=templates_config.library,
        ci_style_commit=templates_config.commit_interaction.style,
        result_dir=get_result_dir_path_for_pages(ci_config=ci_config),
        arg_push=arg_push,
        arg_changed=arg_changed
    )
    _write_yml_templates(
        templates_config=templates_config, ci_config=ci_config,
        file=templates_config.template_files.style_check_file,
        template_kwargs=template_kwargs
    )


def write_naming_template(templates_config: TemplateGeneratorConfig, ci_config: CIConfig):
    """
    Write naming guideline template
    """
    arg = write_parser_args(
        python_module=templates_config.modelica_py_ci.naming_guideline_module,
        template_script_args={
            "changed_flag": True,
            "config": ci_config.get_dir_path().joinpath(ci_config.naming_guideline_file).as_posix()
        },
        user_args=templates_config.dict()
    )

    template_kwargs = dict(
        utilities_directory=get_utilities_path(templates_config=templates_config),
        image_name=templates_config.dymola_image,
        ci_stage_style_check=templates_config.stage_names.style_check,
        modelicapyci_syntax_test_module=templates_config.modelica_py_ci.syntax_test_module,
        xvfb_flag=templates_config.xvfb_flag,
        library=templates_config.library,
        ci_naming_guideline=templates_config.commit_interaction.naming,
        result_dir=get_result_dir_path_for_pages(ci_config=ci_config),
        arg=arg,
        modelicapyci_syntax_naming_guideline=templates_config.modelica_py_ci.naming_guideline_module,
        ci_stage_om_badge=templates_config.stage_names.OM_badge
    )
    _write_yml_templates(
        templates_config=templates_config, ci_config=ci_config,
        file=templates_config.template_files.naming_guideline_file,
        template_kwargs=template_kwargs
    )


def write_om_badge_template(templates_config: TemplateGeneratorConfig, ci_config: CIConfig):
    """
    Write OM Badge Check template
    """
    arg = write_parser_args(
        python_module=templates_config.modelica_py_ci.om_badge_module,
        template_script_args={"main_branch": "master"},
        overwrite_user_args_with_template_args=True,
        user_args=templates_config.dict()
    )

    template_kwargs = dict(
        utilities_directory=get_utilities_path(templates_config=templates_config),
        arg=arg,
        image_name=templates_config.dymola_image,
        modelicapyci_om_badge_module=templates_config.modelica_py_ci.om_badge_module,
        result_dir=get_result_dir_path_for_pages(ci_config=ci_config),
        badge_name=templates_config.om_badge_name,
        main_branch=templates_config.main_branch,
        ci_stage_om_badge=templates_config.stage_names.OM_badge
    )
    _write_yml_templates(
        templates_config=templates_config, ci_config=ci_config,
        file=templates_config.template_files.om_badge_file,
        template_kwargs=template_kwargs
    )


def write_ci_whitelist_setting_template(templates_config: TemplateGeneratorConfig, ci_config: CIConfig):
    template_kwargs = dict(
        utilities_directory=get_utilities_path(templates_config=templates_config),
        image_name=templates_config.dymola_image,
        ci_stage_whitelist_setting=templates_config.stage_names.whitelist_setting,
        modelicapyci_config_structure_module=templates_config.modelica_py_ci.config_structure_module,
        arg_struc_wh=2,
        arg_whitelist_check=2,
        modelicapyci_html_tidy_module=templates_config.modelica_py_ci.html_tidy_module,
        arg_whitelist_html=2,
        arg_whitelist_sim=2,
        bot_build_whitelist_commit=templates_config.bot_messages.build_whitelist_commit,
        ci_dir=ci_config.dir,
        ci_build_whitelist_structure_commit=templates_config.commit_interaction.build_whitelist_structure,
        expire_in_time=templates_config.expire_in_time,
        xvfb_flag=templates_config.xvfb_flag,
        modelicapyci_configuration_module=templates_config.modelica_py_ci.configuration_module,
        modelicapyci_test_validate_module=templates_config.modelica_py_ci.test_validate_module
    )
    _write_yml_templates(
        templates_config=templates_config, ci_config=ci_config,
        file=templates_config.template_files.build_whitelist_file,
        template_kwargs=template_kwargs
    )


def write_merge_template(templates_config: TemplateGeneratorConfig, ci_config: CIConfig, ci_toml_path: str):
    """
    Write (IBPSA) Merge template
    """
    merge_branch = f'{templates_config.whitelist_library_config.library}_Merge'
    merge_library_dir = f"{templates_config.whitelist_library_config.library}_folder"

    arg_whitelist_html = write_parser_args(
        python_module=templates_config.modelica_py_ci.create_whitelist_module,
        user_args=templates_config.dict(),
        template_script_args={
            "whitelist_library": templates_config.whitelist_library_config.library,
            "git_url": templates_config.whitelist_library_config.git_url,
            "root_whitelist_library": templates_config.whitelist_library_config.local_path,
        }, skip_args=["packages"]
    )
    arg_lib = write_parser_args(
        python_module=templates_config.modelica_py_ci.library_merge_module,
        user_args=templates_config.dict(),
        template_script_args={
            "merge_library_dir": merge_library_dir,
            "library_dir": f"temp_{templates_config.library}"
        }
    )
    arg_lock = write_parser_args(
        python_module=templates_config.modelica_py_ci.lock_model_module,
        user_args=templates_config.dict(),
        template_script_args={}
    )

    arg_api_pr = write_parser_args(
        python_module=templates_config.modelica_py_ci.api_github_module,
        user_args=templates_config.dict(),
        template_script_args={
            "create_pr_flag": True,
            "ibpsa_merge_flag": True,
        }
    )

    template_kwargs = dict(
        utilities_directory=get_utilities_path(templates_config=templates_config),
        image_name=templates_config.dymola_image,
        ci_stage_lib_merge=templates_config.stage_names.lib_merge,
        ci_stage_update_whitelist=templates_config.stage_names.update_whitelist,
        ci_stage_open_PR=templates_config.stage_names.open_PR,
        git_url=templates_config.whitelist_library_config.git_url,
        merge_library_dir=merge_library_dir,
        library=templates_config.library,
        merge_branch=merge_branch,
        ci_toml_path=ci_toml_path,
        modelicapyci_lock_model_module=templates_config.modelica_py_ci.lock_model_module,
        modelicapyci_library_merge_module=templates_config.modelica_py_ci.library_merge_module,
        arg_lib=arg_lib,
        ci_trigger_ibpsa_commit=templates_config.commit_interaction.trigger_ibpsa,
        expire_in_time=templates_config.expire_in_time,
        modelicapyci_create_whitelist_module=templates_config.modelica_py_ci.create_whitelist_module,
        arg_whitelist_html=arg_whitelist_html,
        modelicapyci_test_validate_module=templates_config.modelica_py_ci.test_validate_module,
        xvfb_flag=templates_config.xvfb_flag,
        arg_lock=arg_lock,
        whitelist_library=templates_config.whitelist_library_config.library,
        bot_merge_commit=templates_config.bot_messages.merge_commit,
        result_dir=get_result_dir_path_for_pages(ci_config=ci_config),
        modelicapyci_api_github_module=templates_config.modelica_py_ci.api_github_module,
        arg_api_pr=arg_api_pr
    )

    _write_yml_templates(
        templates_config=templates_config, ci_config=ci_config,
        file=templates_config.template_files.ibpsa_merge_file,
        template_kwargs=template_kwargs
    )


def _write_yml_templates(
        templates_config: TemplateGeneratorConfig,
        ci_config: CIConfig,
        file: str,
        template_kwargs: dict,
        extra_name: str = ".gitlab-ci",
        suffix: str = "yml"
):
    ci_temp = Path(templates_config.template_files.base, file)
    print(f"Write {ci_temp}")
    my_template = Template(strict_undefined=True, filename=str(ci_temp))
    text = my_template.render(**template_kwargs)
    ci_folder = templates_config.get_templates_dir().joinpath(file).parent
    config_structure.create_path(ci_folder)
    output_file = ci_folder.joinpath(Path(file).name.replace(".txt", f"{extra_name}.{suffix}"))
    with open(output_file, "w") as file:
        file.write(text)
    return output_file


def write_regression_template(templates_config: TemplateGeneratorConfig, ci_config: CIConfig, ci_toml_path: str):
    arg_push = write_parser_args(
        python_module=templates_config.modelica_py_ci.test_reference_module,
        user_args=templates_config.dict(),
        template_script_args={
            "packages": ["$lib_package"],
            "batch": True,
            "changed_flag": False,
            "library_root": ".."
        },
        overwrite_user_args_with_template_args=True
    )
    arg_changed = write_parser_args(
        python_module=templates_config.modelica_py_ci.test_reference_module,
        user_args=templates_config.dict(),
        template_script_args={
            "packages": ["$lib_package"],
            "batch": True,
            "changed_flag": True,
            "library_root": ".."
        },
        overwrite_user_args_with_template_args=True
    )
    coverage_arg = write_parser_args(
        python_module=templates_config.modelica_py_ci.test_reference_module,
        user_args=templates_config.dict(),
        template_script_args={
            "coverage_only": True,
            "batch": False,
            "library_root": "..",
            "changed_flag": False})

    arg_ref_check = write_parser_args(
        python_module=templates_config.modelica_py_ci.test_reference_module,
        user_args=templates_config.dict(),
        template_script_args={
            "create_ref": True,
            "batch": False,
            "library_root": "..",
            "changed_flag": False}
    )

    arg_chart = write_parser_args(
        python_module=templates_config.modelica_py_ci.google_chart_module,
        user_args=templates_config.dict(),
        template_script_args={
            "funnel_comp_flag": True,
            "packages": ["$lib_package"],
            "templates_url": templates_config.template_files.url,
            "error_flag": True},
        overwrite_user_args_with_template_args=True
    )
    api_github_arg = write_parser_args(
        python_module=templates_config.modelica_py_ci.api_github_module,
        user_args=templates_config.dict(),
        template_script_args={"working_branch": "$CI_COMMIT_REF_NAME",
                              "github_token": "${GITHUB_API_TOKEN}",
                              "post_pr_comment_flag": True,
                              "prepare_plot_flag": True})
    api_github_create_ref_arg = write_parser_args(
        python_module=templates_config.modelica_py_ci.api_github_module,
        user_args=templates_config.dict(),
        template_script_args={
            "working_branch": "$CI_COMMIT_REF_NAME",
            "github_token": "${GITHUB_API_TOKEN}",
            "post_pr_comment_flag": True,
            "show_plot_flag": True}
    )
    arg_ref = write_parser_args(
        python_module=templates_config.modelica_py_ci.test_reference_module,
        user_args=templates_config.dict(),
        template_script_args={"create_ref": True, "library_root": ".."})
    arg_check_ref_plot = write_parser_args(
        python_module=templates_config.modelica_py_ci.google_chart_module,
        user_args=templates_config.dict(),
        template_script_args={
            "templates_url": templates_config.template_files.url,
            "funnel_comp_flag": False,
            "error_flag": False,
            "new_ref_flag": True}
    )
    # python ${modelicapyci_google_chart_file} - -line - html - -new - ref - -packages ${library};

    template_kwargs = dict(
        utilities_directory=get_utilities_path(templates_config=templates_config),
        dym_image=templates_config.dymola_image,
        coverage_arg=coverage_arg,
        ci_stage_regression_test=templates_config.stage_names.regression_test,
        ci_stage_ref_check=templates_config.stage_names.ref_check,
        ci_stage_plot_ref=templates_config.stage_names.plot_ref,
        ci_stage_prepare=templates_config.stage_names.prepare,
        arg_ref_check=arg_ref_check,
        ci_toml_path=ci_toml_path,
        modelicapyci_test_reference_module=templates_config.modelica_py_ci.test_reference_module,
        modelicapyci_google_chart_module=templates_config.modelica_py_ci.google_chart_module,
        config_ci_exit_file=ci_config.get_file_path("ci_files", "exit_file").as_posix(),
        result_dir=get_result_dir_path_for_pages(ci_config=ci_config),
        arg_chart=arg_chart,
        ci_regression_test_commit=templates_config.commit_interaction.regression_test,
        expire_in_time=templates_config.expire_in_time,
        arg_push=arg_push,
        arg_changed=arg_changed,
        packages_per_job=convert_packages_per_job(templates_config.packages_per_job),
        modelicapyci_api_github_module=templates_config.modelica_py_ci.api_github_module,
        api_github_arg=api_github_arg,
        api_github_create_ref_arg=api_github_create_ref_arg,
        library=templates_config.library,
        xvfb_flag=templates_config.xvfb_flag,
        modelicapyci_structure_module=templates_config.modelica_py_ci.config_structure_module,
        arg_ref=arg_ref,
        config_ci_new_create_ref_file=ci_config.get_file_path("ci_files", "new_create_ref_file").as_posix(),
        bot_create_ref_commit=templates_config.bot_messages.create_ref_commit,
        ci_show_ref_commit=templates_config.commit_interaction.show_ref,
        arg_check_ref_plot=arg_check_ref_plot,
        ci_reference_check=templates_config.commit_interaction.reference_check
    )
    _write_yml_templates(
        templates_config=templates_config, ci_config=ci_config,
        file=templates_config.template_files.regression_file,
        template_kwargs=template_kwargs
    )


def write_OM_simulate_template(templates_config: TemplateGeneratorConfig, ci_config: CIConfig):
    arg_push = write_parser_args(
        python_module=templates_config.modelica_py_ci.OM_python_check_model_module,
        template_script_args={
            "om_options": "OM_SIM"
        },
        user_args=templates_config.dict())
    arg_changed = write_parser_args(
        python_module=templates_config.modelica_py_ci.OM_python_check_model_module,
        user_args=templates_config.dict(),
        template_script_args={"om_options": "OM_SIM", "changed_flag": True})

    template_kwargs = dict(
        utilities_directory=get_utilities_path(templates_config=templates_config),
        ci_stage_OM_simulate=templates_config.stage_names.OM_simulate,
        library=templates_config.library,
        ci_OM_sim_commit=templates_config.commit_interaction.OM_simulate,
        OM_python_check_model_module=templates_config.modelica_py_ci.OM_python_check_model_module,
        arg_push=arg_push,
        arg_changed=arg_changed,
        result_dir=get_result_dir_path_for_pages(ci_config=ci_config),
        OM_Image=templates_config.open_modelica_image,
        expire_in_time=templates_config.expire_in_time,
        packages_per_job=convert_packages_per_job(templates_config.packages_per_job),
        modelicapyci_config_structure_module=templates_config.modelica_py_ci.config_structure_module
    )
    _write_yml_templates(
        templates_config=templates_config, ci_config=ci_config,
        file=templates_config.template_files.OM_simulate_file,
        template_kwargs=template_kwargs
    )


def write_check_template(templates_config: TemplateGeneratorConfig, ci_config: CIConfig):
    arg_push = write_parser_args(
        python_module=templates_config.modelica_py_ci.test_validate_module,
        user_args=templates_config.dict(),
        template_script_args={
            "packages": ["$lib_package"],
            "dym_options": ["DYM_CHECK"],
            "filter_whitelist_flag": True,
        },
        overwrite_user_args_with_template_args=True
    )
    arg_changed = write_parser_args(
        python_module=templates_config.modelica_py_ci.test_validate_module,
        user_args=templates_config.dict(),
        template_script_args={
            "packages": ["$lib_package"],
            "dym_options": ["DYM_CHECK"],
            "filter_whitelist_flag": True,
            "changed_flag": True
        },
        overwrite_user_args_with_template_args=True
    )

    arg_wh = write_parser_args(
        python_module=templates_config.modelica_py_ci.test_validate_module,
        user_args=templates_config.dict(),
        template_script_args={
            "dym_options": ["DYM_CHECK"],
            "create_whitelist_flag": True,
            "filter_whitelist_flag": False,
        }
    )

    template_kwargs = dict(
        utilities_directory=get_utilities_path(templates_config=templates_config),
        dym_image_name=templates_config.dymola_image,
        ci_stage_model_check=templates_config.stage_names.dymola_model_check,
        ci_stage_create_whitelist=templates_config.stage_names.create_whitelist,
        library=templates_config.library,
        ci_check_commit=templates_config.commit_interaction.check,
        xvfb_flag=templates_config.xvfb_flag,
        modelicapyci_test_validate_module=templates_config.modelica_py_ci.test_validate_module,
        result_dir=get_result_dir_path_for_pages(ci_config=ci_config),
        expire_in_time=templates_config.expire_in_time,
        arg_changed=arg_changed,
        arg_wh=arg_wh,
        arg_push=arg_push,
        packages_per_job=convert_packages_per_job(templates_config.packages_per_job),
        config_ci_exit_file=ci_config.get_file_path("ci_files", "exit_file").as_posix(),
        bot_update_model_whitelist_commit=templates_config.bot_messages.update_model_whitelist_commit,
        whitelist_model_file=ci_config.whitelist.dymola_check_file,
        ci_create_model_whitelist_commit=templates_config.commit_interaction.create_model_whitelist,
        modelicapyci_config_structure_module=templates_config.modelica_py_ci.config_structure_module,
    )
    _write_yml_templates(
        templates_config=templates_config, ci_config=ci_config,
        file=templates_config.template_files.check_file,
        template_kwargs=template_kwargs
    )


def write_simulate_template(templates_config: TemplateGeneratorConfig, ci_config: CIConfig):
    arg_changed = write_parser_args(
        python_module=templates_config.modelica_py_ci.test_validate_module,
        user_args=templates_config.dict(),
        template_script_args={
            "packages": ["$lib_package"],
            "dym_options": ["DYM_SIM"],
            "filter_whitelist_flag": True,
            "changed_flag": True
        },
        overwrite_user_args_with_template_args=True
    )
    arg_push = write_parser_args(
        python_module=templates_config.modelica_py_ci.test_validate_module,
        user_args=templates_config.dict(),
        template_script_args={
            "packages": ["$lib_package"],
            "dym_options": ["DYM_SIM"],
            "filter_whitelist_flag": True,
        },
        overwrite_user_args_with_template_args=True
    )
    arg_wh = write_parser_args(
        python_module=templates_config.modelica_py_ci.test_validate_module,
        user_args=templates_config.dict(),
        template_script_args={"dym_options": "DYM_SIM",
                              "create_whitelist_flag": True})

    template_kwargs = dict(
        utilities_directory=get_utilities_path(templates_config=templates_config),
        dym_image_name=templates_config.dymola_image,
        ci_stage_simulate=templates_config.stage_names.simulate,
        ci_stage_create_exampel_whitelist=templates_config.stage_names.create_example_whitelist,
        modelicapyci_config_structure_module=templates_config.modelica_py_ci.config_structure_module,
        arg_changed=arg_changed,
        arg_push=arg_push,
        library=templates_config.library,
        ci_check_commit=templates_config.commit_interaction.simulate,
        modelicapyci_test_validate_module=templates_config.modelica_py_ci.test_validate_module,
        packages_per_job=convert_packages_per_job(templates_config.packages_per_job),
        arg_wh=arg_wh,
        bot_update_model_whitelist_commit=templates_config.bot_messages.update_example_whitelist_commit,
        whitelist_model_file=ci_config.whitelist.dymola_simulate_file,
        ci_create_model_whitelist_commit=templates_config.commit_interaction.create_simulate_whitelist,
        result_dir=get_result_dir_path_for_pages(ci_config=ci_config),
        expire_in_time=templates_config.expire_in_time,
        xvfb_flag=templates_config.xvfb_flag,
        config_ci_exit_file=ci_config.get_file_path("ci_files", "exit_file").as_posix(),
        ci_stage_create_whitelist=templates_config.stage_names.create_whitelist,
        ci_stage_create_example_whitelist=templates_config.stage_names.create_example_whitelist
    )
    _write_yml_templates(
        templates_config=templates_config, ci_config=ci_config,
        file=templates_config.template_files.simulate_file,
        template_kwargs=template_kwargs
    )


def write_toml_settings(templates_config: TemplateGeneratorConfig, ci_config: CIConfig):
    with open(templates_config.toml_ci_setting_file, "w") as file:
        toml.dump(templates_config.dict(), file)
    print(f'The CI settings are saved in file {templates_config.toml_ci_setting_file}')


def write_main_yml(templates_config: TemplateGeneratorConfig, ci_config: CIConfig, stage_list, ci_template_list):
    ci_template_list = [
        str(Path(file).relative_to(templates_config.templates_store_local_path).as_posix()) for file in ci_template_list
    ]
    if "github.io" in templates_config.page:
        pages_file = "pages/gh-pages.gitlab-ci.yml"
    else:
        pages_file = "pages/gl-pages.gitlab-ci.yml"

    template_kwargs = dict(
        image_name=templates_config.dymola_image,
        stage_list=stage_list,
        github_repository=templates_config.github_repository,
        page=templates_config.page,
        file_list=ci_template_list,
        pages_file=pages_file
    )
    gitlab_ci_yml = _write_yml_templates(
        templates_config=templates_config, ci_config=ci_config,
        file=templates_config.template_files.main_yml_file,
        template_kwargs=template_kwargs,
        extra_name=""
    )
    if templates_config.templates_store_project:
        yml_file = _write_yml_templates(
            templates_config=templates_config, ci_config=ci_config,
            file=templates_config.template_files.remote_templates_yml_file,
            template_kwargs=dict(
                project=templates_config.templates_store_project,
                ref=templates_config.templates_store_branch_name,
                file=gitlab_ci_yml.relative_to(templates_config.templates_store_local_path).as_posix()
            ),
            extra_name=""
        )
        replace_str = "remote_templates"
    else:
        yml_file = _write_yml_templates(
            templates_config=templates_config, ci_config=ci_config,
            file=templates_config.template_files.local_templates_yml_file,
            template_kwargs=dict(
                file=gitlab_ci_yml.relative_to(templates_config.templates_store_local_path).as_posix()
            ),
            extra_name=""
        )
        replace_str = "local_templates"
    new_path = Path(templates_config.library_local_path).joinpath(
        yml_file.relative_to(templates_config.get_templates_dir())
    )
    new_path = new_path.parent.joinpath(new_path.name.replace(replace_str, ""))
    shutil.copy(yml_file, new_path)
    os.remove(yml_file)


def write_utilities_yml(templates_config: TemplateGeneratorConfig, ci_config: CIConfig, ci_toml_path: str):
    template_kwargs = dict(
        activate_python_environment=templates_config.activate_python_environment,
        modelica_py_ci_url=templates_config.modelica_py_ci.url,
        commit_string=templates_config.commit_string,
        PR_main_branch_rule=templates_config.pr_main_branch_rule,
        ci_toml_path=ci_toml_path,
        command_list=templates_config.extra_command_list
    )
    _write_yml_templates(
        templates_config=templates_config, ci_config=ci_config,
        file=templates_config.template_files.utilities_file,
        template_kwargs=template_kwargs,
        extra_name=""
    )


def write_local_windows_test(templates_config: TemplateGeneratorConfig, ci_config: CIConfig):
    arg_changed = write_parser_args(
        python_module=templates_config.modelica_py_ci.test_validate_module,
        user_args=templates_config.dict(),
        template_script_args={
            "dym_options": ["DYM_SIM", "DYM_CHECK"],
            "changed_flag": True
        },
        skip_args=["packages"],
        overwrite_user_args_with_template_args=True
    )
    arg_push = write_parser_args(
        python_module=templates_config.modelica_py_ci.test_validate_module,
        user_args=templates_config.dict(),
        template_script_args={
            "dym_options": ["DYM_SIM", "DYM_CHECK"],
        },
        skip_args=["packages"],
        overwrite_user_args_with_template_args=True
    )
    arg_push_html = write_parser_args(
        python_module=templates_config.modelica_py_ci.html_tidy_module,
        user_args=templates_config.dict(),
        template_script_args={
            "correct_view_flag": True,
            "log_flag": True, "filter_whitelist_flag": True}
    )
    arg_changed_html = write_parser_args(
        python_module=templates_config.modelica_py_ci.html_tidy_module,
        user_args=templates_config.dict(),
        template_script_args={
            "correct_view_flag": True,
            "log_flag": True,
            "filter_whitelist_flag": True
        }
    )
    arg_push_syntax = write_parser_args(
        python_module=templates_config.modelica_py_ci.syntax_test_module,
        template_script_args={"changed_flag": False},
        user_args=templates_config.dict()
    )
    arg_changed_syntax = write_parser_args(
        python_module=templates_config.modelica_py_ci.syntax_test_module,
        user_args=templates_config.dict(),
        template_script_args={"changed_flag": True}
    )
    arg_naming_guideline = write_parser_args(
        python_module=templates_config.modelica_py_ci.naming_guideline_module,
        template_script_args={
            "changed_flag": True,
            "config": ci_config.get_dir_path().joinpath(ci_config.naming_guideline_file).as_posix()
        },
        user_args=templates_config.dict()
    )

    template_kwargs = dict(
        library=templates_config.library,
        packages_per_job=convert_packages_per_job(templates_config.packages_per_job),
        modelicapyci_test_validate_module=templates_config.modelica_py_ci.test_validate_module,
        modelicapyci_syntax_test_module=templates_config.modelica_py_ci.syntax_test_module,
        modelicapyci_html_tidy_module=templates_config.modelica_py_ci.html_tidy_module,
        modelicapyci_api_github_module=templates_config.modelica_py_ci.api_github_module,
        modelicapyci_config_structure_module=templates_config.modelica_py_ci.config_structure_module,
        modelicapyci_syntax_naming_guideline=templates_config.modelica_py_ci.naming_guideline_module,
        arg_naming_guideline=arg_naming_guideline,
        arg_changed=arg_changed,
        arg_push=arg_push,
        arg_changed_syntax=arg_changed_syntax,
        arg_push_syntax=arg_push_syntax,
        arg_changed_html=arg_changed_html,
        arg_push_html=arg_push_html,
        log_path="local_execution_logs"
    )
    _write_yml_templates(
        templates_config=templates_config, ci_config=ci_config,
        file=templates_config.template_files.local_windows,
        template_kwargs=template_kwargs,
        suffix="bat",
        extra_name=""
    )


def get_ci_templates(templates_config: TemplateGeneratorConfig, ci_config: CIConfig):
    yml_files = glob.glob(f'{templates_config.get_templates_dir()}\\**\\**\\*.yml', recursive=True)
    yml_files = sorted(list(set(yml_files)))
    mo_py_files = []
    for file in yml_files:
        if file.find(".gitlab-ci.yml") > -1:
            mo_py_files.append(file.replace(os.sep, "/"))
    return mo_py_files


def get_ci_stages(file_list, template_config: TemplateGeneratorConfig):
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

    # Return sorted list
    names_with_order = template_config.stage_names.get_names_with_order()
    stage_list = sorted(stage_list, key=lambda x: names_with_order[x])
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
    yes = yes_no_input('Config template: Create OpenModelica badge?')
    if yes:
        print('Create OpenModelica badge')
        stages_list.append("om_badge")
    print(f"Setting stages list: {stages_list}")
    return stages_list


def setting_ci_library():
    library = input_with_default(
        message='Which library should be tested?',
        default="AixLib"
    )
    library_path = input(
        f'Path of library? (If the library is located in '
        f'the directory, do not enter an entry.)'
    )
    main_branch = input_with_default(
        message="What is the name of your default/main/master branch?",
        default="main"
    )
    ci_dir = input_with_default(
        message="In which folder of this repository "
                "should configs, whitelists, etc. be stored?",
        default="ci"
    )
    library_mo = Path(library_path).joinpath(library, "package.mo")
    config_structure.check_file_setting(library_mo=library_mo)
    print(f'Setting {library=}, {library_path=}, {library_mo=}, and {main_branch=}')
    return library_path, library, main_branch, library_mo, ci_dir


def setting_ci_dir(library_path: str):
    save_local = yes_no_input("Should the templates and config files be "
                              "stored in your library? Type 'n' for another git-repository")
    if save_local:
        ci_dir = input_with_default(
            message="In which folder of your library "
                    "should the CI templates be stored?",
            default="ci"
        )
        print(f"Setting {ci_dir=}")
        return library_path, ci_dir, "", ""
    else:
        repo_location = input(
            "In which local repository-folder should the templates be saved?"
        )
        ci_dir = input_with_default(
            message="In which folder of this repository "
                    "should the CI templates be stored?",
            default="ci"
        )
        branch_name = input_with_default(
            message="What is the name of the branch in this repository?",
            default="main"
        )
        project = input_with_default(
            message='Give the project name (or url) of the repository',
            default="EBC/EBC_all/gitlab_ci/templates"
        )

        return repo_location, ci_dir, project, branch_name


def setting_ci_packages(library: str, library_mo: Path):
    packages_in_lib = []
    print(f'**** Library {library} ****')
    library_dir = Path(library_mo).parent
    for package in os.listdir(library_dir):
        if package.find(".") == -1 and os.path.isfile(library_dir.joinpath(package, "package.mo")):
            packages_in_lib.append(package)
    if packages_in_lib is None:
        print(f'Dont find library {library}')
        exit(1)
    packages = []
    for package in packages_in_lib:
        yes = yes_no_input(f'Test package {package} in library {library}?')
        if yes:
            packages.append(package)
            continue
    print(f'Setting packages: {packages}')
    return packages


def setting_ci_python_conda_env():
    activate_python_environment = input_with_default(
        message="Give the command to activate a python environment in the image",
        default='eval "$(micromamba shell hook --shell bash)" && micromamba activate base'
    )
    print(f'Setting environment activation command: {activate_python_environment}')
    return activate_python_environment


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
    return WhitelistAndMergeLibraryConfig(
        library=whitelist_library,
        local_path=repo_dir,
        git_url=git_url
    )


def setting_ci_github_repo():
    github_repository = input_with_default(
        message=f'Which github repository in your CI should be used? ',
        default="RWTH-EBC/AixLib"
    )
    print(f'Setting github repository: {github_repository}')
    return github_repository


def setting_ci_page():
    page = input_with_default(
        message='Which gitlab page should be used?',
        default="https://ebc.pages.rwth-aachen.de/EBC_all/github_ci/AixLib"
    )
    print(f'Setting gitlab page: {page}')
    return page


def setting_image_names():
    dymola_image = input_with_default(
        message=f'Which dymola docker image should be used? ',
        default="registry.git.rwth-aachen.de/ebc/ebc_intern/dymola-docker:Dymola2024xRefresh1-micromamba"
    )
    print(f'Setting dymola image: {dymola_image}')
    open_modelica_image = input_with_default(
        message=f'Which OpenModelica docker image should be used? ',
        default="registry.git.rwth-aachen.de/ebc/ebc_intern/openmodelica-docker:main"
    )
    print(f'Setting OpenModelica image: {open_modelica_image}')
    return dymola_image, open_modelica_image


def create_toml_config():
    library_path, library, main_branch, library_mo, ci_dir = setting_ci_library()
    templates_store_local_path, templates_store_folder, templates_store_project, templates_store_branch_name = setting_ci_dir(
        library_path=library_path
    )

    whitelist_library_config = setting_ci_whitelist()
    packages = setting_ci_packages(library=library, library_mo=library_mo)
    stage_list = setting_ci_templates_types()
    activate_python_environment = setting_ci_python_conda_env()
    github_repository = setting_ci_github_repo()
    page = setting_ci_page()
    dymola_image, open_modelica_image = setting_image_names()
    ci_config = CIConfig(dir=str(ci_dir), library_root="")
    templates_toml_save_path = ci_config.get_dir_path(
        different_library_root=templates_store_local_path).joinpath("config", "templates_generator_config.toml")
    mopyci_toml_save_path = ci_config.get_dir_path(
        different_library_root=library_path).joinpath("config", "modelica_py_ci_config.toml")
    os.makedirs(templates_toml_save_path.parent, exist_ok=True)
    os.makedirs(mopyci_toml_save_path.parent, exist_ok=True)

    TemplateGeneratorConfig(
        stage_list=stage_list,
        library=library,
        library_local_path=library_path,
        templates_store_local_path=templates_store_local_path,
        templates_store_project=templates_store_project,
        templates_store_folder=templates_store_folder,
        templates_store_branch_name=templates_store_branch_name,
        main_branch=main_branch,
        packages=packages,
        packages_per_job={package: [package] for package in packages},
        activate_python_environment=activate_python_environment,
        github_repository=github_repository,
        page=page,
        dymola_image=dymola_image,
        open_modelica_image=open_modelica_image,
        whitelist_library_config=whitelist_library_config,
        template_files=TemplateFilesConfig(
            base=str(Path(__file__).parents[1].absolute().joinpath("templates", "ci_templates"))
        )
    ).to_toml(path=templates_toml_save_path)
    print(f"Templates CI-Config saved under: {templates_toml_save_path}")
    save_toml_config(ci_config, mopyci_toml_save_path)
    print(f"Modelica-Py-CI-Config saved under: {mopyci_toml_save_path}")
    return templates_toml_save_path, mopyci_toml_save_path


def write_templates(templates_toml: Path, ci_toml_path: Path):
    templates_config = TemplateGeneratorConfig.from_toml(path=templates_toml)
    ci_config = load_toml_config(ci_toml_path)
    if "CI_PYTHON_CONFIG_FILE" not in os.environ:
        os.environ["CI_PYTHON_CONFIG_FILE"] = str(ci_toml_path)

    relative_ci_toml_path = ci_toml_path.relative_to(templates_config.library_local_path).as_posix()
    for temp in templates_config.stage_list:
        if temp == "check":
            write_check_template(templates_config=templates_config, ci_config=ci_config)
            write_OM_check_template(templates_config=templates_config, ci_config=ci_config)
        if temp == "simulate":
            write_simulate_template(templates_config=templates_config, ci_config=ci_config)
            write_OM_simulate_template(templates_config=templates_config, ci_config=ci_config)
        if temp == "regression":
            write_regression_template(
                templates_config=templates_config, ci_config=ci_config,
                ci_toml_path=relative_ci_toml_path
            )
        if temp == "html":
            write_html_template(templates_config=templates_config, ci_config=ci_config)
        if temp == "style":
            write_style_template(templates_config=templates_config, ci_config=ci_config)
            write_naming_template(templates_config=templates_config, ci_config=ci_config)
        if temp == "Merge" and templates_config.whitelist_library_config is not None:
            write_merge_template(
                templates_config=templates_config, ci_config=ci_config,
                ci_toml_path=relative_ci_toml_path
            )
        if temp == "om_badge":
            write_om_badge_template(templates_config=templates_config, ci_config=ci_config)
    write_ci_pr_interact_template(templates_config=templates_config, ci_config=ci_config)

    # write_ci_whitelist_setting_template(templates_config=templates_config, ci_config=ci_config)
    write_prepare_page_template(templates_config=templates_config, ci_config=ci_config)
    ci_template_list = get_ci_templates(templates_config=templates_config, ci_config=ci_config)
    stage_list = get_ci_stages(file_list=ci_template_list, template_config=templates_config)
    write_utilities_yml(
        templates_config=templates_config, ci_config=ci_config,
        ci_toml_path=relative_ci_toml_path
    )
    write_main_yml(
        templates_config=templates_config,
        ci_config=ci_config,
        stage_list=stage_list,
        ci_template_list=ci_template_list
    )
    write_local_windows_test(templates_config=templates_config, ci_config=ci_config)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Set Github Environment Variables")
    check_test_group = parser.add_argument_group(
        "Arguments to set Environment Variables")
    check_test_group.add_argument("--create-templates",
                                  help=f'Create the CI templates and configs',
                                  action="store_true")
    check_test_group.add_argument("--update-templates",
                                  default=False,
                                  action="store_true")
    check_test_group.add_argument("--templates-toml-file",
                                  help="Path to the "
                                       "templates_generator_config.toml"
                                       " used if write-templates=True",
                                  default=None)
    check_test_group.add_argument("--ci-toml-file",
                                  help="Path to the modelica_py_ci_config.toml"
                                       " used if write-templates=True",
                                  default=None)

    return parser.parse_args()


if __name__ == '__main__':
    ARGS = parse_args()
    if ARGS.create_templates is True:
        template_toml_file, ci_toml_file = create_toml_config()
        write_templates(templates_toml=Path(template_toml_file),
                        ci_toml_path=Path(ci_toml_file))
    if ARGS.update_templates is True:
        if ARGS.templates_toml_file is None or ARGS.ci_toml_file is None:
            raise FileNotFoundError(
                "You have to pass --templates-toml-file and --ci-toml-file"
                " in order to write the templates from an existing setup.\n"
                "Run --create-templates instead to create a fresh setup")
        write_templates(
            templates_toml=Path(ARGS.templates_toml_file),
            ci_toml_path=Path(ARGS.ci_toml_file)
        )
