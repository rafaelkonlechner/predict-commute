The 01_census.arff file is the base file in ARFF format.

First step was, to transform the base ARFF file into CSV using OpenRefine. `-> 02_census.csv`

Second step was, to converting all nominal attributes to numeric. We used OpenRefine for this. `-> 03_census-openrefine-numeric-values.csv` 

Next, we converted the CSV back to the ARFF format using OpenRefine. `-> 04_census-openrefine-numeric-values.arff`

Process the chborn attribute by simple text find/replace as follows:
1. Convert No_children to 0
2. Convert 1_child to 1
3. Convert 2_children to 2
4. Convert 10_children to 10
5. Convert 12_(12+_1960-1990) to 12


Links:
------
OpenRefine http://openrefine.org/
