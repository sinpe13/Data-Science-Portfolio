# Data-Science-Portfolio
Reference repository of my data science, process automation and other work in Python.

### PCA-research_paper
The PCA-research_paper folder contains some samples from the research paper I co-authored titled "A Spectral Decomposition of the Credit Default Swap Indices" (submitted to Physica A on July 13 2019, available: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3419188)

- **cds_pca.py**: the main PCA calculation file that does the backbone calculation of the paper. Main Python libraries used: Pandas, Numpy, Scypy, Sklear. The code connects to a local MSSql DB to query data based on a predefined menu, processes it using the appropriate PCA methodology and outputs it into Excel spreadsheets.

- **pl_plot.py**: plotting the profit/loss standard deviation of the index VS the portfolios resulted from the PCA runs. [Link to sample picture.](https://github.com/sinpe13/Data-Science-Portfolio/blob/master/PCA-research_paper/pl_plot.png)

- **pl_dist_plot.py**: plotting the profit/loss disctribution of the PCA index vs the names in each PCA runs. [Link to sample picture.](https://github.com/sinpe13/Data-Science-Portfolio/blob/master/PCA-research_paper/pl_dist_plot.png)

###
