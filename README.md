# MoCITempGen
This repository holds functions to create your own, library dependant 
CI-scripts. The goal is to improve quality of models through easier CI setup and
let model developers focus on the modeling work. 
The created templates hold functionality for:
- Model checking 
- Model simulation
- Regression testing
- Correct HTML 
- Style Checking
- Merge IBPSA library (specific for IBPSA context)

The basic setup is shown in this picture:
![process](/docs/mocitempgen_process.png)
* MoCITempGen uses the base CI-Templates in .txt form stored in `templates` 
folder to create a library related CI-structure.
* This can then be placed inside the target Modelica library
* The CI tasks are executed by a GitLab runner which uses the functionality 
provided through the python functions in `CITests` folder. This will be moved 
to a public ModelicaPyCI package on PyPi soon
* Through the
[GitLab mirroring feature](https://docs.gitlab.com/ee/user/project/repository/mirror/) 
not only GitLab repos can use MoCITempGen generated templates buy any GitHub,
BitBucket or AWS CodeCommit repository

## Folder Structure

### CI_templates_python
This folder holds the main scripts that perform the creation of the library 
dependant ci-templates. For further information see it's
[Readme](CI_templates_python) 

### CITests
This folder contains all python functions that the CI will later run. This will
be moved into the [ModelicaPyCI](https://github.com/RWTH-EBC/ModelicaPyCI)
package soon. For further information see it's [Readme](CITests).

### templates
This folder contains the base templates for mako that will be used to create 
your library dependant ci-templates.


## TODOS:
* [ ] complete documentation
* [ ] complete extraction of python functions from CITests folder to 
[ModelicaPyCI](https://github.com/RWTH-EBC/ModelicaPyCI) package
* [ ] remove dymola functionality as far as possible 
* [ ] maybe add template generation for GitHub actions