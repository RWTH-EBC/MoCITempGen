from pydantic import Field, field_validator, ValidationInfo, ConfigDictfrom typing import Optional, Unionimport tomlfrom pathlib import Pathfrom ModelicaPyCI.config import ModelicaPyCIConfig, BaseModelNoExtradef write_multiple_rules(rule_list: list = None,                         except_string: str = None,                         rule_option: str = "&&",                         compare_str: str = "!~",                         ci_variable: str = None):    if rule_list is None:        print("Rule is None")        exit(1)    if compare_str == "==":        syntax = '"'    else:        syntax = "/"    if isinstance(rule_list, dict):        if except_string is not None:            _list = []            for var in rule_list:                if var != except_string:                    _list.append(f'{ci_variable}  {compare_str} {syntax}{rule_list[var]}{syntax}')        else:            _list = []            for var in rule_list:                _list.append(f'{ci_variable}  {compare_str} {syntax}{rule_list[var]}{syntax}')        rule_string = ""        for rule in _list:            if rule == _list[0]:                rule_string = f'{rule}  '            else:                rule_string = f'{rule_string} {rule_option} {rule}'        return rule_string    if isinstance(rule_list, list):        if except_string is not None:            rule_list = [f'{ci_variable}  {compare_str} {syntax}{value}{syntax}' for value in rule_list if                         value != except_string]        else:            rule_list = [f'{ci_variable}  {compare_str} {syntax}{value}{syntax}' for value in rule_list]        rule_string = ""        for rule in rule_list:            if rule == rule_list[0]:                rule_string = f'{rule}  '            else:                rule_string = f'{rule_string} {rule_option} {rule}'        return rule_stringclass StageNameWithOrder(BaseModelNoExtra):    name: str    order: float    def __str__(self):        return self.nameclass StageNamesConfig(BaseModelNoExtra):    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")    check_setting: StageNameWithOrder = StageNameWithOrder(name="check_setting", order=0)    build_templates: StageNameWithOrder = StageNameWithOrder(name="build_templates", order=0.1)    whitelist_setting: StageNameWithOrder = StageNameWithOrder(name="build_ci_whitelist", order=0.2)    OM_badge: StageNameWithOrder = StageNameWithOrder(name="OM_Badge", order=0.3)    ref_check: StageNameWithOrder = StageNameWithOrder(name="Ref_Check", order=1)    lib_merge: StageNameWithOrder = StageNameWithOrder(name="merge", order=1.1)    open_PR: StageNameWithOrder = StageNameWithOrder(name="open_PR", order=1.2)    update_whitelist: StageNameWithOrder = StageNameWithOrder(name="update_whiteList", order=1.3)    html_whitelist: StageNameWithOrder = StageNameWithOrder(name="create_html_whitelist", order=2)    create_whitelist: StageNameWithOrder = StageNameWithOrder(name="create_model_whitelist", order=2.1)    create_example_whitelist: StageNameWithOrder = StageNameWithOrder(name="create_example_whitelist", order=2.2)    html_check: StageNameWithOrder = StageNameWithOrder(name="HTML_Check", order=3)    style_check: StageNameWithOrder = StageNameWithOrder(name="Style_check", order=3.1)    dymola_model_check: StageNameWithOrder = StageNameWithOrder(name="model_check", order=4)    OM_model_check: StageNameWithOrder = StageNameWithOrder(name="model_check", order=4.1)    simulate: StageNameWithOrder = StageNameWithOrder(name="simulate", order=5)    OM_simulate: StageNameWithOrder = StageNameWithOrder(name="simulate", order=5.1)    regression_test: StageNameWithOrder = StageNameWithOrder(name="RegressionTest", order=6)    update_ref: StageNameWithOrder = StageNameWithOrder(name="Update_Ref", order=6.1)    plot_ref: StageNameWithOrder = StageNameWithOrder(name="plot_ref", order=6.2)    prepare: StageNameWithOrder = StageNameWithOrder(name="prepare", order=6.3)    prepare_pages: StageNameWithOrder = StageNameWithOrder(name="prepare_pages", order=999)    post_initial_pr_comment: StageNameWithOrder = StageNameWithOrder(name="prepare_pages", order=999)    deploy: StageNameWithOrder = StageNameWithOrder(name="deploy", order=1000)    def get_names_with_order(self) -> dict:        return {stage["name"]: stage["order"] for stage in self.dict().values()}class TemplateFilesConfig(BaseModelNoExtra):    base: Union[str, Path] = "templates"    url: str = "https://github.com/RWTH-EBC/MoCITempGen.git@03_openModelica"    regression_file: str = "unit_tests/regression_test.txt"    check_file: str = "unit_tests/check_model.txt"    simulate_file: str = "unit_tests/simulate_model.txt"    page_file: str = "deploy/prepare_pages.txt"    ci_pr_interact_comment_file: str = "deploy/ci_pr_interact_comment_file.txt"    ibpsa_merge_file: str = "deploy/IBPSA_Merge.txt"    om_badge_file: str = "deploy/om_badge.txt"    html_file: str = "syntax_tests/html_check.txt"    style_check_file: str = "syntax_tests/style_check.txt"    naming_guideline_file: str = "syntax_tests/naming_guideline.txt"    structure_file: str = "deploy/create_CI_path.txt"    main_yml_file: str = ".gitlab-ci.txt"    local_templates_yml_file: str = "local_templates.gitlab-ci.txt"    remote_templates_yml_file: str = "remote_templates.gitlab-ci.txt"    deploy_test_file: str = "deploy/deploy_ci_tests.txt"    build_whitelist_file: str = "cleanupscript/ci_build_whitelist.txt"    OM_check_file: str = "unit_tests/check_OM_model.txt"    OM_simulate_file: str = "unit_tests/simulate_OM_model.txt"    utilities_file: str = "utilities.txt"    local_windows: str = "local_windows_test.txt"class CommitInteractionConfig(BaseModelNoExtra):    update_ref: str = "ci_update_ref"    show_ref: str = "ci_show_ref"    dif_ref: str = "ci_dif_ref"    create_model_whitelist: str = "ci_create_model_whitelist"    create_html_whitelist: str = "ci_create_html_whitelist"    create_simulate_whitelist: str = "ci_create_example_whitelist"    simulate: str = "ci_simulate"    OM_simulate: str = "ci_om_simulate"    check: str = "ci_check"    OM_check: str = "ci_om_check"    regression_test: str = "ci_regression_test"    html: str = "ci_html"    style: str = "ci_style_check"    trigger_ibpsa: str = "ci_trigger_ibpsa"    merge_except: str = "ci_merge_except"    correct_html: str = "ci_correct_html"    build_structure: str = "ci_build_structure"    build_whitelist_structure: str = "ci_build_whitelist"    reference_check: str = "ci_reference_check"    naming: str = "ci_check_naming"class BotMessageConfig(BaseModelNoExtra):    merge_commit: str    push_commit: str    create_ref_message: str    update_whitelist_commit: str    create_ref_commit: str    create_CI_template_commit: str    update_model_whitelist_commit: str    update_example_whitelist_commit: str    create_structure_commit: str    create_html_file_commit: str    build_whitelist_commit: strclass WhitelistAndMergeLibraryConfig(BaseModelNoExtra):    local_path: str = "modelica-ibpsa"    library: str = "IBPSA"    git_url: str = "https://github.com/ibpsa/modelica-ibpsa.git"class TemplateGeneratorConfig(BaseModelNoExtra):    # User inputs    dymola_image: str    open_modelica_image: str    page: str    github_repository: str    stage_list: list    packages: list    packages_per_job: dict    library: str    library_local_path: Union[Path, str]    templates_store_local_path: Union[Path, str]    templates_store_project: str    templates_store_folder: str    templates_store_branch_name: str    dymola_version: str    conda_environment: str    # [main_branches]    main_branch: str    whitelist_library_config: Optional[WhitelistAndMergeLibraryConfig] = Field(default=None)    # Default parameters    min_number_of_unused_licences: int = 5    html_praefix: str = "correct_HTML_"    expire_in_time: str = "7h"    xvfb_flag: str = "xvfb-run -n 77"    bot_name: str = "ebc-aixlib-bot"    utilities_directory: str = "utilities.yml"    template_scripts_dir: str = "scripts"    om_badge_name: str = "om_readiness_badge.svg"    extended_examples: bool = False    extra_command_list: list = ['echo "Skipping custom installation of other Modelica libraries"']    startup_mos: str = None    # Default settings for templates, scripts, and CI-names    stage_names: StageNamesConfig = StageNamesConfig()    modelica_py_ci: ModelicaPyCIConfig = ModelicaPyCIConfig()    template_files: TemplateFilesConfig = TemplateFilesConfig()    commit_interaction: CommitInteractionConfig = CommitInteractionConfig()    bot_messages: Optional[BotMessageConfig] = Field(default=None, validate_default=True)    commit_string: Optional[str] = Field(validate_default=True, default=None)    pr_main_branch_rule: Optional[str] = Field(validate_default=True, default=None)    @field_validator("bot_messages")    @classmethod    def create_messages(cls, bot_messages, info: ValidationInfo):        if bot_messages is not None:            return bot_messages        whitelist_library_config = info.data.get("whitelist_library_config")        if whitelist_library_config is not None:            whitelist_library_name = whitelist_library_config.library        else:            whitelist_library_name = None        return BotMessageConfig(            merge_commit=f"CI message from {info.data['bot_name']}. "                         f"Merge of '{whitelist_library_name}' library.",            push_commit=f"CI message from {info.data['bot_name']}. "                        f"Automatic push of CI with new regression reference files. "                        f"Please pull the new files before push again.",            create_ref_message=f"CI message from {info.data['bot_name']}. "                               f"New reference files were pushed to this branch. "                               f"The job was successfully and the newly added files are tested in another commit.",            update_whitelist_commit=f"CI message from {info.data['bot_name']}. "                                    f"Update or created new whitelist. "                                    f"Please pull the new whitelist before push again.",            create_ref_commit=f"CI message from {info.data['bot_name']}. "                              f"Automatic push of CI with new regression reference files. "                              f"Please pull the new files before push again. ",            create_CI_template_commit=f"CI message from {info.data['bot_name']}. "                                      f"Automatic push of CI with new created CI templates. "                                      f"Please pull the new files before push again.",            update_model_whitelist_commit=f"CI message from {info.data['bot_name']}. "                                          f"Update file whitelist-check_file. "                                          f"Please pull the new files before push again.",            update_example_whitelist_commit=f"CI message from {info.data['bot_name']}. "                                            f"Update file whitelist-simulate_file. "                                            f"Please pull the new files before push again.",            create_structure_commit=f"CI message from {info.data['bot_name']}. "                                    f"Add files for ci structure",            create_html_file_commit=f"CI message from {info.data['bot_name']}. "                                    f"Push new files with corrected html Syntax .",            build_whitelist_commit=f"CI message from {info.data['bot_name']}. "                                   f"Push new created whitelists.",        )    @field_validator("commit_string")    @classmethod    def create_commit_string(cls, commit_string, info: ValidationInfo):        if commit_string is not None:            return commit_string        if "commit_interaction" not in info.data:            return   # Already another error before        return write_multiple_rules(            rule_list=list(info.data["commit_interaction"].dict().values()),            rule_option="&&",            compare_str="!~",            ci_variable="$CI_COMMIT_MESSAGE"        )    @field_validator("pr_main_branch_rule")    @classmethod    def create_pr_main_branch_rule(cls, pr_main_branch_rule, info: ValidationInfo):        if pr_main_branch_rule is not None:            return pr_main_branch_rule        if "main_branch" not in info.data:            return  # Already another error before        return write_multiple_rules(rule_list=[info.data["main_branch"]],                                    rule_option="||",                                    compare_str="==",                                    ci_variable="$CI_COMMIT_BRANCH")    def to_toml(self, path: Path):        with open(path, "w+") as file:            toml.dump(self.dict(), file)        print(self.dict())    @classmethod    def from_toml(cls, path: Path):        with open(path, "r") as file:            return cls(**toml.load(file))    def get_templates_dir(self) -> Path:        return Path(self.templates_store_local_path).joinpath(self.templates_store_folder).joinpath(            self.template_scripts_dir        )