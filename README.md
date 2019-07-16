# Data-Science-Portfolio
Reference repository of my data science, process automation and other work in Python.

### [PCA-research_paper](https://github.com/sinpe13/Data-Science-Portfolio/tree/master/PCA-research_paper)
The PCA-research_paper folder contains some samples from the research paper I co-authored titled "A Spectral Decomposition of the Credit Default Swap Indices" (submitted to Physica A on July 13 2019, available: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3419188)

  - **cds_pca.py**: the main PCA calculation file that does the backbone calculation of the paper. Main Python libraries used: Pandas, Numpy, Scypy, Sklear. The code connects to a local MSSql DB to query data based on a predefined menu, processes it using the appropriate PCA methodology and outputs it into Excel spreadsheets.

  - **pl_plot.py**: plotting the profit/loss standard deviation of the index VS the portfolios resulted from the PCA runs. [Link to sample picture.](https://github.com/sinpe13/Data-Science-Portfolio/blob/master/PCA-research_paper/pl_plot.png)

  - **pl_dist_plot.py**: plotting the profit/loss disctribution of the PCA index vs the names in each PCA runs. ![alt text](https://github.com/sinpe13/Data-Science-Portfolio/blob/master/PCA-research_paper/pl_dist_plot.png)

### [Compliance-Automation](https://github.com/sinpe13/Data-Science-Portfolio/tree/master/Compliance-Automation)

Python application to automate internal compliance process. Over 200 clients are sending backcompliance reports in a predefined excel format that used to be processed manually by a 3-person team for 2 weeks. The application imports all xls files from the source folder and outputs the processed results into an output spreadsheet. This **reduced manual processing time from 240 manhours to minutes of computing time**.

### [Who is the GOAT (Greatest Of All Time) in men's tennis?](https://github.com/sinpe13/ATP-dataset)

Fun experiment to calculate ELO score - used mainly in chess to compare players from different eras based on the strenght of their opponents played - to make a quantitative argument of who is the greatest mens tennis player all time (GOAT). Jupyter notebook with the results is available [here](https://github.com/sinpe13/ATP-dataset/blob/master/ATP%20dataset.ipynb).

**Spoiler alert:** the first two players on the list are still going strong...
