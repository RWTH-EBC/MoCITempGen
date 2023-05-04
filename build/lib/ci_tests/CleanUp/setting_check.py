from ci_test_config import ci_config

class Check_Settings(ci_config):

    def __init__(self):
        super().__init__()

    def _check_variables(self, variable_main_list, github_token, github_private_key):
        for var in variable_main_list:
            if var is None:
                print(f'Please set variable {var}.')
            else:
                print(f'variable {var} is set in file .gitlab-ci.yml.')
        if github_token is None:
            print(f'Please set variable GITHUB_API_TOKEN in your gitlab ci repo under CI/Variables.')
        else:
            print(f'Variable GITHUB_API_TOKEN is set.')
        if github_private_key is None:
            print(f'Please set variable GITHUB_PRIVATE_KEY in your gitlab ci repo under CI/Variables.')
        else:
            print(f'Variable GITHUB_PRIVATE_KEY is set.')





if __name__ == '__main__':


    sett_check = Check_Settings()
    #sett_check._check_variables(variable_main_list, github_token=args.github_token, github_private_key=args.github_private_key)

