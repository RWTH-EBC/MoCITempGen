### [CI_setting.toml](CI_setting.toml)
This folder contains settings for the CI. The CI_setting.toml file contains the variables for the CI. Changes can be made in the toml file. The templates are then updated with the command `python bin/CITests/07_ci_templates/ci_templates.py --setting`.

| TOML Arguments    | Description                                                                       | 
|-------------------|-----------------------------------------------------------------------------------| 
| library_name      | Name of the dymola library                                                        |
| whitelist_library | name of the library that is not tested. Faulty models are written to the whitelist |
| dymola_version    | Version of dymola in docker image                                                 |
| python_version    | Version of anaconda python environment                                            |
| Package           | List of package which are tested                                                  |
| stages            | Stage in CI Pipeline (depends on ci templates)                                    |
| git_url           | The URL from the whitelist library                                                |
| wh_library_path   | path from the whitelist library (if local)                                        |
| Merge_Branch      | For merging two libraries (default: IBPSA_Merge)                                  |
| image_name         | Name of the runner image                                                          |
| Github_Repository         | Name of Github Repository                                                         |
| GITLAB_Page         | Name of gitlab page                                                               |
| ci_commit_commands         | Name of the runner image                                                          |
| File_list         | Name of the runner image                                                          |

