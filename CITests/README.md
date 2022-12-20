# What CI Tests are implemented

### Check, Simulate and Regressiontest: [UnitTests](UnitTests)
With these tests, models are validated or simulated or models will compare and evaluated with stored values by means of a unit test.

### Correct HTML and Style Check: [SyntaxTest](SyntaxTest)

The html code (documentation) is tested and corrected if necessary. 
Thus the deposited HTML code is checked for correctness and corrected.
<p>With the ModelManagement library in dymola the style of the models is checked.</p>

### [IBPSA Merge](deploy/IBPSA_Merge)
This template performs an automatic IBPSA merge into AixLib. The models of the IBPSA are copied into the AixLib, a new conversion script is created based on the IBPSA and integrated into the AixLib as well as the whitelists are created.
### [Converter](Converter)
lock_model: Lock Models of a specific library has been created to read-only mode.
google_charts: script visualizes the deviation of failing models that failed the regression test

### [Api Scripts](api_script)
Create or update a pull request.


### Setting CI Variables
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