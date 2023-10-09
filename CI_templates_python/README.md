## Create your own templates

Execute the `python python CI_templates_python/ci_templates.py` command in the root directory of your repository. 
The script will then ask you which tests and packages to check, adapting to your library. 

Also the variables in the `CI_templates_python\ci_templates_configuration.py` should be checked before. 
Important are the variables `image_name` and `variable_main_list`. These must be adapted to the current repo. The settings are then stored under `CI_templates_python\Setting\CI_setting.toml`. 
If changes should be made in the settings, these can be made in the toml file. 

Then the command `python python CI_templates_python/ci_templates.py --setting` must be executed. 

