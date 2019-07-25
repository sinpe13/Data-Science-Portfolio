# Data Science Portfolio
Sample repository of my data science, process automation and other work in Python.

### [PCA Research Paper](https://github.com/sinpe13/Data-Science-Portfolio/tree/master/PCA-research_paper)
The PCA-research_paper folder contains some samples from the research paper I co-authored titled "A Spectral Decomposition of the Credit Default Swap Indices" (submitted to Physica A on July 13 2019, available: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3419188)

We utilized PCA to make significant imporvements to hedging credit portfolios versus the market-standard CDS index hedge which is traded above 1TRN dollars per day. Besides the machine learning part, the project included a significant database excercise to create the source database, bring together the required views and make sure data issues are addressed.

  - **cds_pca.py**: the main PCA calculation file that does the backbone calculation for the paper. Main Python libraries used: Pandas, Numpy, Scypy, Sklearn. The code connects to a local MSSql DB to query data based on a predefined menu, processes it using the appropriate PCA methodology and outputs it into Excel spreadsheets.

  - **pl_plot.py**: plotting the profit/loss standard deviation of the index VS the portfolios resulted from the PCA runs. [Link to sample picture.](https://github.com/sinpe13/Data-Science-Portfolio/blob/master/PCA-research_paper/pl_plot.png)

  - **pl_dist_plot.py**: plotting the profit/loss disctribution of the PCA index vs the names in each PCA runs. Main Python libraries used: Matplotlib, Seaborn ![alt text](https://github.com/sinpe13/Data-Science-Portfolio/blob/master/PCA-research_paper/pl_dist_plot.png)

### Sales Opportunity Closing Predictions using Machine Learning Techniques

This was project to predict which deals will close for the given year based on Salesforce data attributes of the opportunities. The complexity came from the poor data quality of the source data which requried significant data engineering. We ended up deriving attributes based on activity and milestone history which proved to be the only reliable data source. We ran different machine learning methods and imporved forecasting on the annual sales of the company. (This code is company confidential.)

### [Who is the GOAT (Greatest Of All Time) in men's tennis?](https://github.com/sinpe13/ATP-dataset)

Fun experiment to calculate [ELO score](https://en.wikipedia.org/wiki/Elo_rating_system) - used mainly in chess to compare players from different eras based on the strenght of their opponents they played - to make a quantitative argument of who is the greatest mens tennis player all time (GOAT). Jupyter notebook with the results is available [here](https://github.com/sinpe13/ATP-dataset/blob/master/ATP%20dataset.ipynb).

**Spoiler alert:** the first two players on the list are still going strong...

### Compliance Automation

Python application to automate internal compliance process. Over 200 clients are sending back compliance reports in a predefined excel format that used to be processed manually by a 3-person team for 2 weeks. The application imports all xls files from the source folder and outputs the processed results into an output spreadsheet. This **reduced manual processing time from 240 manhours to minutes of computing time**. (This code is company confidential.)

### Salesforce Data Extraction and Manipulation

The objective here was to automate a laborous manual process to extract Salesforce data into different spreadsheets per customer so that account managers can provide information per client; then automatically import the feedbak to Salesforce once the results are sent back. The application can directly import data from Salesforce via API or also read from xls.

With the above application weeks of manual work taking place semi-annually has been automated. (This code is company confidential.)
