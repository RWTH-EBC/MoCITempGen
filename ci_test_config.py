from pathlib import Pathclass ci_config(object):    def __init__(self):        # [CI_dir]        self.dymola_ci_test_dir = f"dymola-ci-tests"        self.dymola_python_test_dir = Path(__file__).parent         # [whitelist]        self.wh_ci_dir = f"dymola-ci-tests/ci_whitelist"        self.wh_model_file = f"dymola-ci-tests/ci_whitelist/ci_check_whitelist.txt"        self.wh_simulate_file = f"dymola-ci-tests/ci_whitelist/ci_simulate_whitelist.txt"        self.wh_html_file = f"dymola-ci-tests/ci_whitelist/ci_html_whitelist.txt"        self.wh_ref_file = f"dymola-ci-tests/ci_whitelist/ci_reference_check_whitelist.txt"        # [config_ci]        self.config_ci_dir = f"dymola-ci-tests/Configfiles"        self.config_ci_exit_file = f"dymola-ci-tests/Configfiles/exit.sh"        self.config_ci_new_ref_file = f"dymola-ci-tests/Configfiles/ci_new_ref_file.txt"        self.config_ci_new_create_ref_file = f"dymola-ci-tests/Configfiles/ci_new_created_reference.txt"        self.config_ci_changed_file = f"dymola-ci-tests/Configfiles/ci_changed_model_list.txt"        self.config_ci_ref_file = f"dymola-ci-tests/Configfiles/ci_reference_list.txt"        self.config_ci_eof_file = f"dymola-ci-tests/Configfiles/EOF.sh"        # [plot]        self.chart_dir = f"dymola-ci-tests/charts"        self.temp_chart_dir = f"MoCITempGen/templates/google_templates"        self.temp_chart_file = f"MoCITempGen/templates/google_templates/google_chart.txt"        self.temp_index_file = f"MoCITempGen/templates/google_templates/index.txt"        self.temp_layout_file = f"MoCITempGen/templates/google_templates/layout_index.txt"        # [interact_ci_list]        self.ci_interact_dir = f"dymola-ci-tests/interact_CI"        self.ci_interact_show_ref_file = f"dymola-ci-tests/interact_CI/show_ref.txt"        self.ci_interact_update_ref_file = f"dymola-ci-tests/interact_CI/update_ref.txt"        # [artifcats]        self.artifacts_dir = f"dymola-ci-tests/templates/artifacts"        self.library_ref_results_dir = f"Resources/ReferenceResults/Dymola"        self.library_resource_dir = f"Resources/Scripts/Dymola"        # [Dymola_Python_Tests]        self.dymola_python_test_url = f"--single-branch --branch 03_openModelica https://github.com/RWTH-EBC/MoCITempGen.git"        # [result]        self.result_dir = f"dymola-ci-tests/result"        self.result_whitelist_dir = f"dymola-ci-tests/result/ci_whitelist"        self.result_config_dir = f"dymola-ci-tests/result/configfiles"        self.result_plot_dir = f"dymola-ci-tests/result/charts"        self.result_syntax_dir = f"dymola-ci-tests/result/syntax"        self.result_regression_dir = f"dymola-ci-tests/result/regression"        self.result_interact_ci_dir = f"dymola-ci-tests/result/interact_CI"        self.result_ci_template_dir = f"dymola-ci-tests/result/ci_template"        self.result_check_result_dir = f"dymola-ci-tests/result/Dymola_check"        self.result_OM_check_result_dir = f"dymola-ci-tests/result/OM_check"        # [Color]        self.CRED = f"\033[91m"        self.CEND = f"\033[0m"        self.green = f"\033[0;32m"        self.yellow = f"\033[33m"        self.blue = f"\033[44m"