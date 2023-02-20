# What is it?
### lock_model.py
The script sets all models of the library for which a whitelist has been created to read-only mode. 
#### Parser Arguments
| Parser Arguments  | Description | 
|-------------------|------------| 
|--library| Library to test           | 
|--lock-library|    Library to lock        | 

#### Example: Execution on gitlab runner (linux)
    python Dymola_python_tests/CITests/Converter/lock_model.py --library ${library} --lock-library ${wh_library}
### google_charts.py
The script visualizes the deviation of failing models that failed the regression test. It also creates graphs of the generated values based on the reference files.
#### Parser Arguments
| Parser Arguments | Description                           | 
|-----------------|---------------------------------------| 
|--line-html| plot a google html chart in line form |  | 
|--create-layout| Create a layout with a plots                                      | 
|--line-matplot|          plot a matlab chart                             |  
|--new-ref|        Plot new models with new created reference files                               |   
|--error|      Plot only model with errors                                 |   
|--show-ref| Plot only model on the interact ci list | 
|--update-ref| Plot only updated models |  
|--single-package| Test only the Modelica package Modelica.Package |  
|--library| Library to test|  
|--funnel-comp| Take the datas from funnel_comp |  
|--ref-txt| Take the datas from reference datas |  

#### Example: Execution on gitlab runner (linux)
    python Dymola_python_tests/CITests/Converter/google_charts.py --line-html --show-ref --single-package AixLib --library AixLib
    python Dymola_python_tests/CITests/Converter/google_charts.py  --create-layout --library AixLib --single-package AixLib