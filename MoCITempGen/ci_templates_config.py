from pydantic import BaseModel, Field, field_validator, ValidationInfo, ConfigDictfrom typing import Optional, Unionfrom ModelicaPyCI.config import FilesConfig, ResultConfig, WhitelistConfigclass StageNamesConfig(BaseModel):    check_setting: str = "check_setting"    build_templates: str = "build_templates"    ref_check: str = "Ref_Check"    lib_merge: str = "merge"    html_whitelist: str = "create_html_whitelist"    create_whitelist: str = "create_model_whitelist"    create_example_whitelist: str = "create_example_whitelist"    html_check: str = "HTML_Check"    style_check: str = "Style_check"    dymola_model_check: str = "model_check"    simulate: str = "simulate"    OM_model_check: str = "OM_model_check"    OM_simulate: str = "OM_simulate"    regression_test: str = "RegressionTest"    update_ref: str = "Update_Ref"    plot_ref: str = "plot_ref"    prepare: str = "prepare"    open_PR: str = "open_PR"    update_whitelist: str = "update_whiteList"    build_ci_structure: str = "build_ci_structure"    deploy: str = "deploy"    whitelist_setting: str = "build_ci_whitelist"    class TemplateFilesConfig(BaseModel):    base: str = "../../MoCITempGen/templates/ci_templates"    regression_file: str = "UnitTests/regression_test.txt"    check_file: str = "UnitTests/check_model.txt"    simulate_file: str = "UnitTests/simulate_model.txt"    page_file: str = "deploy/gitlab_pages.txt"    ibpsa_merge_file: str = "deploy/IBPSA_Merge.txt"    html_file: str = "syntaxtest/html_check.txt"    style_check_file: str = "syntaxtest/style_check.txt"    structure_file: str = "deploy/create_CI_path.txt"    main_yml_file: str = ".gitlab-ci.txt"    setting_file: str = "cleanupscript/ci_setting.txt"    deploy_test_file: str = "deploy/deploy_ci_tests.txt"    build_whitelist_file: str = "cleanupscript/ci_build_whitelist.txt"    OM_check_file: str = "UnitTests/check_OM_model.txt"    OM_simulate_file: str = "UnitTests/simulate_OM_model.txt"    utilities_file: str = "utilities.txt"class CommitInteractionConfig(BaseModel):    update_ref: str = "ci_update_ref"    show_ref: str = "ci_show_ref"    dif_ref: str = "ci_dif_ref"    create_model_wh: str = "ci_create_model_wh"    create_html_wh: str = "ci_create_html_wh"    create_simulate_wh: str = "ci_create_example_wh"    simulate: str = "ci_simulate"    OM_simulate: str = "ci_om_simulate"    check: str = "ci_check"    OM_check: str = "ci_om_check"    regression_test: str = "ci_regression_test"    html: str = "ci_html"    setting: str = "ci_setting"    style: str = "ci_style_check"    trigger_ibpsa: str = "ci_trigger_ibpsa"    merge_except: str = "ci_merge_except"    correct_html: str = "ci_correct_html"    build_structure: str = "ci_build_structure"    build_whitelist_structure: str = "ci_build_whitelist"    reference_check: str = "ci_reference_check"class BotMessageConfig(BaseModel):    merge_commit: str    push_commit: str    create_ref_message: str    update_whitelist_commit: str    create_ref_commit: str    create_CI_template_commit: str    update_model_whitelist_commit: str    update_example_whitelist_commit: str    create_structure_commit: str    create_html_file_commit: str    build_whitelist_commit: strclass ModelicaPyCIConfig(BaseModel):    url: str = "https://github.com/RWTH-EBC/ModelicaPyCI.git@2_pydantic_config"    OM_python_check_model_module: str = "ModelicaPyCI.unittest.om_check"    test_validate_module: str = "ModelicaPyCI.unittest.checkpackages.validatetest"    test_reference_module: str = "ModelicaPyCI.unittest.reference_check"    google_chart_module: str = "ModelicaPyCI.converter.google_charts"    api_github_module: str = "ModelicaPyCI.api_script.api_github"    html_tidy_module: str = "ModelicaPyCI.syntax.html_tidy"    syntax_test_module: str = "ModelicaPyCI.syntax.style_checking"    configuration_module: str = "ModelicaPyCI.config"    library_merge_module: str = "ModelicaPyCI.deploy.ibpsa_merge"    lock_model_module: str = "ModelicaPyCI.converter.lock_model"    config_structure_module: str = "ModelicaPyCI.structure.config_structure"    setting_check_module: str = "ModelicaPyCI.clean_up.setting_check"class WhitelistAndMergeLibraryConfig(BaseModel):    local_path: str = "modelica-ibpsa"    library: str = "IBPSA"    git_url: str = "https://github.com/ibpsa/modelica-ibpsa.git"class GeneralConfig(BaseModel):    model_config = ConfigDict(extra='forbid')    dymola_image: str = "registry.git.rwth-aachen.de/ebc/ebc_intern/dymola-docker:Dymola_2022-miniconda"    open_modelica_image: str = "registry.git.rwth-aachen.de/ebc/ebc_intern/openmodelica-docker:main"    gitlab_page: str = "https://ebc.pages.rwth-aachen.de/EBC_all/github_ci/AixLib"    github_repository: str = "RWTH-EBC/AixLib"    stage_list: list = []    package_list: dict = {}    changed_flag: bool = True    extended_examples_flag: bool = True    html_praefix: str = "correct_HTML_"    expire_in_time: str = "7h"    library: str = "AixLib"    library_path: str = ""    dymola_version: str = "2022"    conda_environment: str = "myenv"    xvfb_flag: str = "xvfb-run -n 77"    bot_name: str = "ebc-aixlib-bot"    # [main_branches]    main_branch_list: list = ['main', 'development']    buildingspy_upgrade: str = "git+https://github.com/MichaMans/BuildingsPy@testexamplescoverage"    toml_setting_file_template: str = "Setting/CI_setting_template.txt"    toml_setting_file: str = "Setting/CI_setting.toml"    templates_dir: str = "bin/ci-tests"    utilities_directory: str = "utilities.yml"    dymola_ci_test_dir: str = 'dymola-ci-tests'    stage_names: StageNamesConfig = StageNamesConfig()    modelica_py_ci: ModelicaPyCIConfig = ModelicaPyCIConfig()    template_files: TemplateFilesConfig = TemplateFilesConfig()    commit_interaction: CommitInteractionConfig = CommitInteractionConfig()    ci_config_files: FilesConfig = FilesConfig()    result: ResultConfig = ResultConfig()    whitelist_scripts: WhitelistConfig = WhitelistConfig()    whitelist_library: Optional[WhitelistAndMergeLibraryConfig] = Field(default=None)    bot_messages: Optional[BotMessageConfig] = Field(default=None, validate_default=True)    @field_validator("bot_messages")    @classmethod    def create_messages(cls, bot_messages, info: ValidationInfo):        if bot_messages is not None:            return bot_messages        if "whitelist_library" in info.data:            whitelist_library_name = info.data['whitelist_library'].library        else:            whitelist_library_name = None        return BotMessageConfig(            merge_commit=f"CI message from {info.data['bot_name']}. "                         f"Merge of '{whitelist_library_name}' library. "                         f"Update files {info.data['whitelist_scripts'].check_file} and {info.data['whitelist_scripts'].html_file}",            push_commit=f"CI message from {info.data['bot_name']}. "                        f"Automatic push of CI with new regression reference files. "                        f"Please pull the new files before push again.",            create_ref_message=f"CI message from {info.data['bot_name']}. "                               f"New reference files were pushed to this branch. "                               f"The job was successfully and the newly added files are tested in another commit.",            update_whitelist_commit=f"CI message from {info.data['bot_name']}. "                                    f"Update or created new whitelist. "                                    f"Please pull the new whitelist before push again.",            create_ref_commit=f"CI message from {info.data['bot_name']}. "                              f"Automatic push of CI with new regression reference files. "                              f"Please pull the new files before push again. "                              f"Plottet Results $GITLAB_Page/$CI_COMMIT_REF_NAME/charts/",            create_CI_template_commit=f"CI message from {info.data['bot_name']}. "                                      f"Automatic push of CI with new created CI templates. "                                      f"Please pull the new files before push again.",            update_model_whitelist_commit=f"CI message from {info.data['bot_name']}. "                                          f"Update file {info.data['whitelist_scripts'].check_file}. "                                          f"Please pull the new files before push again.",            update_example_whitelist_commit=f"CI message from {info.data['bot_name']}. "                                            f"Update file {info.data['whitelist_scripts'].simulate_file}. "                                            f"Please pull the new files before push again.",            create_structure_commit=f"CI message from {info.data['bot_name']}. "                                    f"Add files for ci structure",            create_html_file_commit=f"CI message from {info.data['bot_name']}. "                                    f"Push new files with corrected html Syntax .",            build_whitelist_commit=f"CI message from {info.data['bot_name']}. "                                   f"Push new created whitelists.",        )