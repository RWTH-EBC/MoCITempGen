## Create your own templates

Execute the `python Dymola_python_tests/python CI_templates_python/ci_templates.py` command in the root directory of your repository. 
The script will then ask you which tests and packages to check, adapting to your library. 

Also the variables in the `Dymola_python_tests\CI_templates_python\ci_templates_configuration.py` should be checked before. 
Important are the variables `image_name` and `variable_main_list`. These must be adapted to the current repo. The settings are then stored under `Dymola_python_tests\CI_templates_python\Setting\CI_setting.toml`. 
If changes should be made in the settings, these can be made in the toml file. 

Then the command `python Dymola_python_tests/python CI_templates_python/ci_templates.py --setting` must be executed. 


## Setup your own CI

### Variables
| CI Pipeline Arguments | Description                                                                        | 
|-----------------------|------------------------------------------------------------------------------------| 
| CI_TEST_TOKEN          | Name of the dymola library                                                         |
| GITHUB_API_TOKEN    | name of the library that is not tested. Faulty models are written to the whitelist |
| GITHUB_PRIVATE_KEY        | Version of dymola in docker image                                                  |



For more information look [here](https://git.rwth-aachen.de/EBC/EBC_all/gitlab_ci/templates/-/wikis/Python-Dymola-CI-Templates).

