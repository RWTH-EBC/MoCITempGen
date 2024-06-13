# MoCiTempGen
A template generator tool for GitLab CI templates that creates a CI setup that can perform various tasks for Modelica libraries.
## How to use
### Create your templates

If you start fresh, run 
```
python MoCiTempGen/ci_templates_build.py --create-templates
```
to create intial settings in form of two `.toml` files:
1. `templates_generator_config.toml`
2. `modelica_py_ci_config.toml` 

`templates_generator_config.toml` stores information about how to generate your templates and can be stored local, while `modelica_py_ci_config.toml` stores information that is relevant for the later CI jobs and will always be placed in your repository.
A prompt based process will guide you through the next steps and allow you to configure how your CI setup should look like.

If you already have a config and just changed something inside your `templates_generator_config.toml`, you can run 
```
python MoCiTempGen/ci_templates_build.py --update-templates --templates-toml-file <path_tou_your_templates_generator_config.toml> --ci-toml-file <path_to_your_modelica_py_ci_config.toml>
```

### Setup your own CI
If you decided to create the CI setup inside in a separate repository, you need to create a link to this repository. 
In the repository to be tested, the following content needs to be written to the .gitlab-ci.yml. 
"ref" is the name of the branch of the separate template where the templates are located. 
```	
	include:
            project: '<Path/to/your/GitLab/repository>'
            ref: <branch_in_template_repository>
            file: '<path to the created .gitlab-ci.yml' 
```

#### Variables (ToDo: Check if up2date)
##### GitLab
| GitLab Variables | Description                                                                                                                                                                      | 
|------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| 
| CI_PYTHON_DYMOLA_NAME   | Deploy Username for Repository [Dymola_python_tests](https://git.rwth-aachen.de/EBC/EBC_all/gitlab_ci/Dymola_python_tests)                                                       |
| CI_PYTHON_DYMOLA_TOKEN   | Deploy Token for Repository [Dymola_python_tests](https://git.rwth-aachen.de/EBC/EBC_all/gitlab_ci/Dymola_python_tests)                                                          |
| GITHUB_API_TOKEN | API Github [Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)                                              |
| GITHUB_PRIVATE_KEY  | RSA Private [Key](https://docs.github.com/de/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent), Used to push to a repository |

##### GitHub
| Github Variables | Description                             | 
|------------------|-----------------------------------------| 
| GIT_TOKEN     | Token for access to the API             |
| SLACK_BOT_TOKEN    | RSA Private key to push to a repository |

[//]: # (For more information look [here]&#40;https://git.rwth-aachen.de/EBC/EBC_all/gitlab_ci/templates/-/wikis/Python-Dymola-CI-Templates&#41;.)


## Repository structure

## [MoCiTempGen](MoCITempGen)
Holds the code to create your own CI structure

## [templates](templates)
This folder contains the base templates that are used to create your library specific templates
