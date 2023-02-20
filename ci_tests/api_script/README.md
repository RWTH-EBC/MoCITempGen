# What is it?
Create a pull request or update a pull request in github

## api_github.py

The python script api_githuy.py creates a pull request for the current branch or comments messages into a pull request.

#### Parser Arguments
| Parser Arguments | Description                                                                | 
|---------------|----------------------------------------------------------------------------| 
| --correct-branch | Branch to correct your Code                                                |
| --github-repo | Environment Variable owner/RepositoryName                                  |
| --working-branch | Your current working Branch.                                               |
| --base-branch | your base branch (main)                                         |
| --github-token | Your GITHUB Token |
| --prepare-plot| Plot new models with new created reference files      |
| --show-plot  | Plot new models with new created reference files                                                           |
| --post-pr-comment | Plot new models with new created reference files                                                  |
| --correct-html  | folder of a whitelist library                                              |
| --ibpsa-merge | url repository of whitelist library                                        |
| --merge-request| Comment for a IBPSA Merge request                                         |
| --gitlab-page | Set your gitlab page url                          |


Set your github API [Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) and add it to your CI-Variables.

#### Example: Execution on gitlab runner (linux)
    python Dymola_python_tests/CITests/api_script/api_github.py  --working-branch $CI_COMMIT_REF_NAME --github-repo $Github_Repository --gitlab-page $GITLAB_Page --github-token $GITHUB_API_TOKEN --post-pr-comment --prepare-plot
## api_slack.py
For more information look [here](https://github.com/RWTH-EBC/AixLib/wiki/github-actions).

Setup for slack [api](https://sagarsonwane230797.medium.com/automate-slack-notification-with-github-actions-4675862713cc) 
#### Parser Arguments
| Parser Arguments | Description                             | 
|------------------|-----------------------------------------| 
| --github-token | Set GITHUB Token                        |
| --base-branch    | Name of your base branch (default:main) |
| --working-branch | Your current working Branch.            |
| --slack-token    | your base branch (main)                 |
| --github-repo    | Environment Variable owner/RepositoryName                     |
#### Example: Execution on gitlab runner (linux)
    python bin/CITests/04_api_script/api_slack.py --github-token ${{ secrets.GIT_TOKEN }} --slack-token ${{ secrets.SLACK_BOT_TOKEN }} --github-repo "RWTH-EBC/AixLib" --base-branch "development"