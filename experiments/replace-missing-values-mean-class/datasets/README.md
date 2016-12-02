The datasets in this directory are all based on the same dataset 'census-chborn.arff'.

By introducing missing values for low information gain attributes (`lowIG` in file names), for high information gain attributes (`highIG`) and for all attributes (`all`), experiments should show, how the algorithm behaves with (slightly) modified data.

There are also small fraction (`sm`) and large (`lg`) fractions replaced to missing values. Small fraction is considered to be 20%, large fraction is to be considered 80% (50% when applying for 'all' attributes).


low information gain attribute: `poverty`
high information gain attributes: `sploc`, `sprule`, `yngch`, `relateg`, `raceg`


The higher the value in `highIG-<value>`, the more high information gain attributes where modified. `highIG-2` means `sploc` and `sprule` have been modified.


Missing values are introduced by the `scripts/create-missing-values` script. Replacements on the datasets also performed by this script, using the `-r true` parameter. For this, you need python3.x and the liac-arff python module installed.

command: `./create-missing-values -s 1 -f FRACTION -a ATTRIBUTES -r true`
