import requests
import argparse


class GET_API_GITHUB(object):

    def __init__(self, github_repo, working_branch):
        """
        Args:
            github_repo (): github repository
            working_branch ():  Branch in which work is currently being done
        """
        self.github_repo = github_repo
        self.working_branch = working_branch

    def get_pr_number(self):
        """

        Returns:
            pr_number (): Return the pull request number

        """
        url = f'https://api.github.com/repos/{self.github_repo}/pulls'
        payload = {}
        headers = {'Content-Type': 'application/json' }
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
        print(response.text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Set Github Environment Variables")  # Configure the argument parser
    check_test_group = parser.add_argument_group("Arguments to set Environment Variables")
    check_test_group.add_argument("-CB", "--correct-branch", default="${Newbranch}", help="Branch to correct your Code")
    check_test_group.add_argument("-GR", "--github-repo", default="RWTH-EBC/AixLib",
                                  help="Environment Variable owner/RepositoryName")
    check_test_group.add_argument('-WB', "--working-branch", default="${TARGET_BRANCH}",
                                  help="Your current working Branch")
    check_test_group.add_argument("--base-branch", default="master",
                                  help="your base branch (master or develpment)")
    check_test_group.add_argument('-GT', "--github-token", default="${GITHUB_API_TOKEN}", help="Your Set GITHUB Token")
    check_test_group.add_argument("--prepare-plot", help="Plot new models with new created reference files",
                                  action="store_true")
    check_test_group.add_argument("--show-plot", help="Plot new models with new created reference files",
                                  action="store_true")
    check_test_group.add_argument("--post-pr-comment", help="Plot new models with new created reference files",
                                  action="store_true")
    check_test_group.add_argument("--create-pr", help="Plot new models with new created reference files",
                                  action="store_true")
    check_test_group.add_argument("--correct-html", help="Plot new models with new created reference files",
                                  action="store_true")
    check_test_group.add_argument("--ibpsa-merge", help="Plot new models with new created reference files",
                                  action="store_true")
    check_test_group.add_argument("--merge-request", help="Comment for a IBPSA Merge request", action="store_true")
    check_test_group.add_argument('-GP', "--gitlab-page", default="${GITLAB_Page}", help="Set your gitlab page url")
    args = parser.parse_args()

    pull_request = PULL_REQUEST_GITHUB(github_repo=args.github_repo,
                                       working_branch=args.working_branch,
                                       github_token=args.github_token)
    get_api = GET_API_GITHUB(github_repo=args.github_repo,
                             working_branch=args.working_branch)

    if args.post_pr_comment is True:
        message = str
        page_url = f'{args.gitlab_page}/{args.working_branch}/plots'
        print(f'Setting gitlab page url: {page_url}')
        pr_number = get_api.get_pr_number()
        if args.prepare_plot is True:
            message = f'Errors in regression test. Compare the results on the following page\\n {page_url}'
        if args.show_plot is True:
            message = f'Reference results have been displayed graphically and are created under the following page {page_url}'
        pull_request.post_pull_request_comment(pull_request_number=pr_number, post_message=message)
    if args.create_pr is True:
        working_branch = str
        base_branch = str
        pull_request_title = str
        label_name = str
        pull_request_message = str
        if args.correct_html is True:
            pull_request_title = f'Corrected HTML Code in branch {args.working_branch}'
            pull_request_message = f'Merge the corrected HTML Code. After confirm the pull request, **pull** your branch to your local repository. **Delete** the Branch {args.working_branch}'
            label_name = f'Correct HTML'
            base_branch = f'{args.working_branch.replace("correct_HTML_", "")}'
            working_branch = f'{args.working_branch.replace("correct_HTML_", "")}'
            print(working_branch)
        if args.ibpsa_merge is True:
            pull_request_title = f'IBPSA Merge'
            pull_request_message = f'**Following you will find the instructions for the IBPSA merge:**\\n  1. Please pull this branch IBPSA_Merge to your local repository.\\n 2. As an additional saftey check please open the AixLib library in dymola and check whether errors due to false package orders may have occurred. You do not need to translate the whole library or simulate any models. This was already done by the CI.\\n 3. If you need to fix bugs or perform changes to the models of the AixLib, push these changes using this commit message to prevent to run the automatic IBPSA merge again: **`fix errors manually`**. \\n  4. You can also output the different reference files between the IBPSA and the AixLib using the CI or perform an automatic update of the referent files which lead to problems. To do this, use one of the following commit messages \\n  **`ci_dif_ref`** \\n  **`ci_update_ref`** \\n The CI outputs the reference files as artifacts in GitLab. To find them go to the triggered pipeline git GitLab and find the artifacts as download on the right site. \\n 5. If the tests in the CI have passed successfully, merge the branch IBPSA_Merge to development branch. **Delete** the Branch {args.working_branch}'
            label_name = f'IBPSA_Merge'
            base_branch = "development"
            working_branch = args.working_branch

        assignees_owner = get_api.get_github_username(branch=working_branch)
        owner = get_api.return_owner()
        pr_response = pull_request.post_pull_request(owner=owner, base_branch=base_branch, pull_request_title=pull_request_title, pull_request_message=pull_request_message)
        pr_number = get_api.get_pr_number()
        pull_request.update_pull_request_assignees(pull_request_number=pr_number, assignees_owner=assignees_owner, label_name=label_name)
        exit(0)
