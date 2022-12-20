## Create your own templates

Execute the `python Dymola_python_tests/python CI_templates_python/ci_templates.py` command in the root directory of your repository. 
The script will then ask you which tests and packages to check, adapting to your library. 

Also the variables in the `Dymola_python_tests\CI_templates_python\ci_templates_configuration.py` should be checked before. 
Important are the variables `image_name` and `variable_main_list`. These must be adapted to the current repo. The settings are then stored under `Dymola_python_tests\CI_templates_python\Setting\CI_setting.toml`. 
If changes should be made in the settings, these can be made in the toml file. 

Then the command `python Dymola_python_tests/python CI_templates_python/ci_templates.py --setting` must be executed. 


## Setup your own CI
After the templates are created, they should be pushed to the template repository with the following path. 
In the repository to be tested, the following content is written to the .gitlab-ci.yml. 
"ref" is the name of the branch where the templates are located. 
Be sure you have access to the repository [Dymola_Python_tests](https://git.rwth-aachen.de/EBC/EBC_all/gitlab_ci/Dymola_python_tests) and the [template repository](https://git.rwth-aachen.de/EBC/EBC_all/gitlab_ci/templates).

```	
	include:
            project: 'EBC/EBC_all/gitlab_ci/templates'
            ref: AixLib
            file: 'dymola-ci-tests/ci_templates/.gitlab-ci.yml' 
```
### Variables
#### GitLab
| GitLab Variables | Description                                                                                                                                                                      | 
|------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| 
| CI_PYTHON_DYMOLA_NAME   | Deploy Username for Repository [Dymola_python_tests](https://git.rwth-aachen.de/EBC/EBC_all/gitlab_ci/Dymola_python_tests)                                                       |
| CI_PYTHON_DYMOLA_TOKEN   | Deploy Token for Repository [Dymola_python_tests](https://git.rwth-aachen.de/EBC/EBC_all/gitlab_ci/Dymola_python_tests)                                                          |
| GITHUB_API_TOKEN | API Github [Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)                                              |
| GITHUB_PRIVATE_KEY  | RSA Private [Key](https://docs.github.com/de/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent), Used to push to a repository |

#### GitHub
| Github Variables | Description                             | 
|------------------|-----------------------------------------| 
| GIT_TOKEN     | Token for access to the API             |
| SLACK_BOT_TOKEN    | RSA Private key to push to a repository |

For more information look [here](https://git.rwth-aachen.de/EBC/EBC_all/gitlab_ci/templates/-/wikis/Python-Dymola-CI-Templates).

