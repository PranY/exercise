Unity Machine Learning Engineering Homework

In this homework, your task is to build a simple machine learning pipeline. The pipeline should perform two tasks: 
- 1 prepare training data 
- 2 use the prepared training data to train a simple model that predicts the install probabilities of ad impressions.

Here are the guidelines:

* Complete the homework with your language of choice.
* Use a workflow management tool (e.g., Apache Airflow and Kubeflow) to combine the data preparation and model training tasks.
* Ensure your work is packaged in a way such that it is easy to set up the environment and to perform end-to-end run of the pipeline.
* Please include instructions for the setup.
* It is sufficient to train a simple model that predicts the install probabilities of ad impressions. Time consuming tasks like advanced feature engineering and hyper-parameter tuning are not required.
* ReportROC AUC and log-loss of your model. Note that these are not the main criteria we use for evaluating the homework
* Keep your code organized and clean.

**Deliverables**

You are asked to upload the following deliverables in a zip file:
* A report (PDF) detailing:
    * Description of the pipeline and design choices.
    * Performance evaluation of the model.
    * Discussion of how to scale up the pipeline to process tens of billions data points.
    * Discussion of future work
* The source code used to create the pipeline

**Data description**

The training data includes the attributes and labels of each ad impression. The label is set to 1 if an ad impression leads to an install of the advertised game, otherwise the label is set to 0.

- id:impression id
- timestamp:time of the event in UTC
- campaignId:id of the advertising campaign(the game being advertised)
- platform:device platform
- softwareVersion:software version of the device
- sourceGameId:id of the publishing game(the game being played)
- country:country of user
- startCount:how many times user has started a campaign
- viewCount:how many times user has viewed a campaign
- clickCount:how many times user has clicked a campaign
- installCount:how many times user has installed games from this ad network
- lastStart:last time user started any campaign
- startCount1d:how many times user has started (any) campaigns within the last 24hours
- startCount7d:how many times user has started (any) campaigns within the last 7days
- connectionType:internet connection type
- deviceType:device model
- install:binary indicator if install was observed (install=1) or not(install=0) after impression