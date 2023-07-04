from gitlab_ci_templates.ci_templates_config import ci_template_config

class templates_structure(ci_template_config):

    def __init__(self):
        super(templates_structure, self).__init__()

    @staticmethod
    def create_except_commit_list():
        """

        Returns:

        """
        except_commit_list = []
        except_commit_dic = (vars(ci_template_config()))
        for commit in except_commit_dic:
            if commit.find("ci_") > -1 and commit.find("_commit") > -1:
                except_commit_list.append(except_commit_dic[commit])
        return except_commit_list


    def get_toml_var(self, pattern_1: str, pattern_2: str, to_group: str):
        """

        Args:
            pattern_1 ():
            pattern_2 ():
            to_group ():

        Returns:

        """
        _list = {}
        var_dict = vars(ci_template_config())
        _dict = {}
        for var in var_dict:
            if var.find(pattern_1) > -1 and var.find(pattern_2) > -1:
                _list[var] = var_dict[var]
        _dict[to_group] = _list
        return _dict

    def get_variables(self, pattern: str, to_group: str):
        """

        Args:
            pattern ():
            to_group ():

        Returns:

        """
        _list = {}
        var_dict = vars(ci_template_config())
        _dict = {}
        for var in var_dict:
            if var.find(pattern) > -1:
                _list[var] = var_dict[var]
        _dict[to_group] = _list
        return _dict

