**Following you will find the instructions for the IBPSA merge:** 
1. Please pull this branch IBPSA_Merge to your local repository.
2. As an additional saftey check please open the AixLib library in dymola and check whether errors due to false package orders may have occurred. You do not need to translate the whole library or simulate any models. This was already done by the CI.
3. If you need to fix bugs or perform changes to the models of the AixLib, push these changes using this commit message to prevent to run the automatic IBPSA merge again: **`fix errors manually`**. 
4. You can also output the different reference files between the IBPSA and the AixLib using the CI or perform an automatic update of the referent files which lead to problems. 
To do this, use one of the following commit messages:
   - **`ci_dif_ref`**   
   - **`ci_update_ref`** 
The CI outputs the reference files as artifacts in GitLab. To find them go to the triggered pipeline git GitLab and find the artifacts as download on the right site. 
5. If the tests in the CI have passed successfully, merge the branch IBPSA_Merge to development branch. **Delete** the Branch {args.working_branch}