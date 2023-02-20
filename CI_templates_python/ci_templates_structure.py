from CI_templates_python.ci_templates_configuration import CI_template_config




@staticmethod
def create_except_commit_list():
    except_commit_list = []
    except_commit_dic = (vars(CI_template_config()))
    for commit in except_commit_dic:
        if commit.find("ci_") > -1 and commit.find("_commit") > -1:
            except_commit_list.append(except_commit_dic[commit])
    return except_commit_list


def _create_except_branches(self):
    pass


@staticmethod
def _create_stage_list():
    stage_list = []
    stage_dic = (vars(CI_template_config()))
    for stage in stage_dic:
        if stage.find("_stage_") > -1:
            stage_list.append(stage_dic[stage])
    return stage_list
