import requests
import argparse
import sys
from pathlib import Path
import os
from git import Repo
import git

class GitRepository(object):

    #def __init__(self):
    #    """
    #    Args:
    #        repo_dir ():  Folder of the cloned project.
    #        git_url (): Git url of the cloned project.
    #    """
    #    pass

    @staticmethod
    def clone_repository(repo_dir: Path, git_url: str):
        """
        Pull git repository.

        Args:
            repo_dir ():  Folder of the cloned project.
            git_url (): Git url of the cloned project.
        """
        if os.path.exists(repo_dir):
            print(f'{repo_dir} folder already exists.')
        else:
            print(f'Clone {repo_dir} Repo')
            Repo.clone_from(git_url, repo_dir)

    @staticmethod
    def git_diff():
        # git diff --raw --diff-filter=AMT HEAD^1 >  dymola-ci-tests/Configfiles/ci_changed_model_list.txt
        repo = git.Repo("")
        t = repo.git()

        #print(t.diff("--raw --diff-filter=AMT HEAD^1"))
        diff_list = repo.head.commit.diff("HEAD~1")
        _list = []
        library = "ci_tests"
        for file in diff_list:

            if library in str(file):
                print(file)
                _list.append(file)


class PULL_REQUEST_GITHUB(object):

    def __init__(self, github_repo, working_branch, github_token):
        """

        Args:
            github_repo ():
            working_branch ():
            github_token ():
        """
        self.github_repo = github_repo
        self.working_branch = working_branch
        self.github_token = github_token

    def get_pr_number(self):
        """
        Returns:
            pr_number (): Return the pull request number
        """
        url = f'https://api.github.com/repos/{self.github_repo}/pulls'
        payload = {}
        headers = {'Content-Type': 'application/json'}
        response = requests.request("GET", url, headers=headers, data=payload)
        pull_request_json = response.json()
        for pull in pull_request_json:
            name = pull["head"].get("ref")
            if name == self.working_branch:
                pr_number = pull["number"]
                if pr_number is None:
                    print(f'Cant find Pull Request Number')
                    exit(1)
                else:
                    print(f'Setting pull request number: {pr_number}')
                    return pr_number

    def get_github_username(self, branch):
        """
        Args:
            branch ():
        Returns:

        """
        url = f'https://api.github.com/repos/{self.github_repo}/branches/{branch}'
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        branch = response.json()
        commit = branch["commit"]
        commit = commit["commit"]
        commit = commit["author"]
        if commit is not None:
            assignees_owner = commit["name"]
            if assignees_owner is not None:
                print(f'Setting login name: {assignees_owner}')
            else:
                assignees_owner = "ebc-aixlib-bot"
                print(f'Setting login name: {assignees_owner}')
        else:
            assignees_owner = "ebc-aixlib-bot"
            print(f'Setting login name: {assignees_owner}')
        return assignees_owner

    def return_owner(self):
        owner = self.github_repo.split("/")
        return owner[0]

    def post_pull_request(self, owner, base_branch, pull_request_title, pull_request_message):
        """

        Args:
            owner ():
            base_branch ():
            pull_request_title ():
            pull_request_message ():

        Returns:

        """
        url = f'https://api.github.com/repos/{self.github_repo}/pulls'
        title = f'\"title\": \"{pull_request_title}\"'
        body = f'\"body\":\"{pull_request_message}\"'
        head = f'\"head\":\"{owner}:{self.working_branch}\"'
        base = f'\"base\": \"{base_branch}\"'
        message = f'\n	{title},\n	{body},\n	{head},\n	{base}\n'
        payload = "{" + message + "}"
        headers = {
            'Authorization': 'Bearer ' + self.github_token,
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response

    def update_pull_request_assignees(self, pull_request_number, assignees_owner, label_name):
        """

        Args:
            pull_request_number ():
            assignees_owner ():
            label_name ():
        """
        url = f'https://api.github.com/repos/{self.github_repo}/issues/{str(pull_request_number)}'
        assignees = f'\"assignees\":[\"{assignees_owner}\"]'
        labels = f'\"labels\":[\"CI\", \"{label_name}\"]'
        payload = "{\r\n" + assignees + ",\r\n" + labels + "\r\n}"
        headers = {
            'Authorization': 'Bearer ' + self.github_token,
            'Content-Type': 'application/json'
        }
        response = requests.request("PATCH", url, headers=headers, data=payload)
        if str(response).find(f'<Response [422]>') > -1:
            assignees_owner = "ebc-aixlib-bot"
            assignees = f'\"assignees\":[\"{assignees_owner}\"]'
            payload = "{\r\n" + assignees + ",\r\n" + labels + "\r\n}"
            requests.request("PATCH", url, headers=headers, data=payload)
        print(f'User {assignees_owner} assignee to pull request Number {str(pull_request_number)}')

    def post_pull_request_comment(self, pull_request_number, post_message):
        """

        Args:
            pull_request_number ():
            post_message ():
        """
        url = f'https://api.github.com/repos/{self.github_repo}/issues/{str(pull_request_number)}/comments'
        message = f'{post_message}'
        body = f'\"body\":\"{message}\"'
        payload = "{" + body + "}"
        headers = {
            'Authorization': 'Bearer ' + self.github_token,
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)


class Parser:
    def __init__(self, args):
        self.args = args

    def main(self):
        parser = argparse.ArgumentParser(description="Set Github Environment Variables")
        check_test_group = parser.add_argument_group("Arguments to set Environment Variables")
        # [Github - settings]
        check_test_group.add_argument("--github-repository", default="RWTH-EBC/AixLib",
                                      help="Environment Variable owner/RepositoryName")
        check_test_group.add_argument("--working-branch", default="${TARGET_BRANCH}",
                                      help="Your current working Branch")
        check_test_group.add_argument("--base-branch", default="main",
                                      help="your base branch (main)")
        check_test_group.add_argument("--github-token", default="${GITHUB_API_TOKEN}",
                                      help="Your Set GITHUB Token")
        check_test_group.add_argument("--gitlab-page", default="${GITLAB_Page}", help="Set your gitlab page url")

        # [ bool - flag
        check_test_group.add_argument("--prepare-plot-flag", help="Plot new models with new created reference files",
                                      action="store_true", default=False)
        check_test_group.add_argument("--show-plot-flag", help="Plot new models with new created reference files",
                                      action="store_true", default=False)
        check_test_group.add_argument("--post-pr-comment-flag", help="Plot new models with new created reference files",
                                      action="store_true", default=False)
        check_test_group.add_argument("--create-pr-flag", help="Plot new models with new created reference files",
                                      action="store_true", default=False)
        check_test_group.add_argument("--correct-html-flag", help="Plot new models with new created reference files",
                                      action="store_true", default=False)
        check_test_group.add_argument("--ibpsa-merge-flag", help="Plot new models with new created reference files",
                                      action="store_true", default=False)
        check_test_group.add_argument("--merge-request", help="Comment for a IBPSA Merge request", action="store_true")

        args = parser.parse_args()
        return args


if __name__ == '__main__':
    args = Parser(sys.argv[1:]).main()
    GitRepository.git_diff()
    """pull_request = PULL_REQUEST_GITHUB(github_repo=args.github_repository,
                                       working_branch=args.working_branch,
                                       github_token=args.github_token)
    message = """""

    """if args.post_pr_comment_flag is True:
        page_url = f'{args.gitlab_page}/{args.working_branch}/charts'
        print(f'Setting gitlab page url: {page_url}')
        pr_number = pull_request.get_pr_number()
        if args.prepare_plot_flag is True:
            message = f'Errors in regression test. Compare the results on the following page\\n {page_url}'
        if args.show_plot_flag is True:
            message = f'Reference results have been displayed graphically and are created under the following page {page_url}'
        pull_request.post_pull_request_comment(pull_request_number=pr_number, post_message=message)
    if args.create_pr_flag is True:
        working_branch = str
        base_branch = str
        pull_request_title = str
        label_name = str
        if args.correct_html_flag is True:
            pull_request_title = f'Corrected HTML Code in branch {args.working_branch}'
            message = f'Merge the corrected HTML Code. After confirm the pull request, **pull** your branch to your local repository. **Delete** the Branch {args.working_branch}'
            label_name = f'Correct HTML'
            base_branch = f'{args.working_branch.replace("correct_HTML_", "")}'
            working_branch = f'{args.working_branch.replace("correct_HTML_", "")}'
        if args.ibpsa_merge_flag is True:
            pull_request_title = f'IBPSA Merge'
            message = f'**Following you will find the instructions for the IBPSA merge:**\\n  1. Please pull this branch IBPSA_Merge to your local repository.\\n 2. As an additional saftey check please open the AixLib library in dymola and check whether errors due to false package orders may have occurred. You do not need to translate the whole library or simulate any models. This was already done by the CI.\\n 3. If you need to fix bugs or perform changes to the models of the AixLib, push these changes using this commit message to prevent to run the automatic IBPSA merge again: **`fix errors manually`**. \\n  4. You can also output the different reference files between the IBPSA and the AixLib using the CI or perform an automatic update of the referent files which lead to problems. To do this, use one of the following commit messages \\n  **`ci_dif_ref`** \\n  **`ci_update_ref`** \\n The CI outputs the reference files as artifacts in GitLab. To find them go to the triggered pipeline git GitLab and find the artifacts as download on the right site. \\n 5. If the tests in the CI have passed successfully, merge the branch IBPSA_Merge to development branch. **Delete** the Branch {args.working_branch}'
            label_name = f'IBPSA_Merge'
            base_branch = "development"
            working_branch = args.working_branch

        assignees_owner = pull_request.get_github_username(branch=working_branch)
        owner = pull_request.return_owner()
        pr_response = pull_request.post_pull_request(owner=owner, base_branch=base_branch,
                                                     pull_request_title=pull_request_title,
                                                     pull_request_message=message)
        pr_number = pull_request.get_pr_number()
        pull_request.update_pull_request_assignees(pull_request_number=pr_number, assignees_owner=assignees_owner,
                                                   label_name=label_name)
        exit(0)"""

