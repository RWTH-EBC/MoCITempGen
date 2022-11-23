# What CI Tests are implemented

### Check, Simulate and Regressiontest: UnitTests
With these tests, models are validated or simulated or models will compare and evaluated with stored values by means of a unit test.

###Correct HTML and Style Check: SyntaxTest

The html code (documentation) is tested and corrected if necessary. 
Thus the deposited HTML code is checked for correctness and corrected.
<p>With the ModelManagement library in dymola the style of the models is checked.</p>

###IBPSA Merge
This template performs an automatic IBPSA merge into AixLib. The models of the IBPSA are copied into the AixLib, a new conversion script is created based on the IBPSA and integrated into the AixLib as well as the whitelists are created.