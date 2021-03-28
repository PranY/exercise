The objective of this exercise to build an end-to-end pipeline that is satisfies all the requirements mentioned in the `Task.md` file.

There is an option to work with Apache Airflow or Kubeflow. Since the developer is new to both, it is fairly straightforward to go with the Airflow approach and builds DAGs (ingest >> preprocess >> train >> evaluate >> deploy). Airflow offers numerous operator and the `PythonOperator`can easily help plug the functions and build the pipeline.

However, the developer knows that such an implementation comes at a cost. For instance, he will need to move to `KubernetesOperator` to run the tasks on a Kubernetes cluster for scalability. Additionally, he will need to opt for `CeleryExecutor` or any other distributed executor because sequential execution may become a bottleneck and under-utilize workers. Although, there should be a work around to use Airflow for the most part, it needs further evaluation.

Considering the above points (and knowing that Unity is using GCP services), it is a good idea to follow Kubernetes route.

Now, focusing on the architecture, there are broadly 3 steps:

- **Data** ingestion, validation, transformation, feature-generation, splitting.
- **Model** training (+ hyper-params tuning), evaluation, serving.
- **Life cycle** monitoring, logging, iterating model.

There are numerous ways to approach the above steps and below is a purely GCP-based example for the same, courtesy Google blogs.

![architecture](https://cloud.google.com/solutions/images/architecture-for-mlops-using-tfx-kubeflow-pipelines-and-cloud-build-6-ci-cd-kubeflow.svg)
<br><br>
<br><br>

---

# Solution

<br><br>

## <u> Data understanding </u>

After an initial overview of all the features, we can bucket features in 4 broader categories, namely, company-side features, interaction features, user attributes and user activity.

![data_clusters](assets/data_clusters.jpg)

Based on the provided field descriptors, we will represent the information flow in a logical and consistent way that binds back to how this data may have been generated.
<br><br>

A user arrives with the user attributes {device type, connection type, platform, software version, country} and a video ad is shown. The ad is associated with a campaign (campaign ID) and promotes a game (game ID). This leads to an impression event, which is the granularity of the provided data.
<br><br>

**Conversion funnel**:
(Assumptions based on the provided definition)

<u>_startCount_</u>: This refers to all the videos ads ever started on the user's device

<u>_viewCount_</u>: Since all impressions are implicitly viewed; the meaning of view, here, can imply that the ad was viewed for more than a specific time interval or completely. Thus, this refers to all the video ads viewed, as per definition, by the user.

<u>_clickCount_</u>: If the user click's on the ad while or after watching. This refers to all the ads that we clicked.

<u>_installCount_</u>: If the ad led to an installation. This refers to all previous installation via video ads.

**Note**: The definition says 'how many times the user has installed games from this network ever'. There is not further information about what a network is so we will assume that it means the Unity ad network.
<br><br>

**User journey**: When a user is impressed with an ad, the user can view -> click -> install. If the installation happens, install flag is set to 1 for the impression and other information is logged as usual.
<br><br>

**Other factors**: The installation flag also derives from factors outside the logged information. For example, the user may have clicked but the app/play store didn't function. Or the user was trying to press the skip/close button on the ad but clicked wrong and arrived at the app/play store. Overall, the user's propensity to install depends on the following factors:

- the game type or the user-recommendation match
- the ad placement; between some loading period vs in the middle of the play
- Funnel attributes with given user attributes i.e. ease of skipping or clicking, re-direct to app/play store, installation size, paid/free app.
- unknowns
  <br><br>

With the above analysis, we can say that a campaign is a collection of video ads from various games and a game can be a part of multiple campaigns. There is no information if the video ad corresponding to a gameId-campaignId pair is unique for that pair or reused across all campaigns for that game.
<br><br>

## <u> Components for pipeline </u>

After the EDA, we can start designing the components for our kubeflow pipeline. We will follow `preprocess >> train(+evaluation) >> test(prediction) >> deploy`. We will remove the ingest component as the data is locally available.

> If time permits, we can add basic spark functionality coupled with a querying mechanism that can pull data dynamically form RDS, as an example to containerize the ingestion process.

---

## <u> ML pipeline </u>

### <u> Building components and running CI </u>

The pipeline solution will follow a similar but scaled-down pattern as shown in the above GCP image. The component structure will be `preprocess >> train >> test >> deploy`. After investigating the kubeflow-pipeline, we observed that we needed our workflow to push the docker containers to a hosting or manually inject the files in pods. **Pushing containers to dockerhub is not an option due to private data**. We will leave the pipeline functional and locally run the pipeline to generate all the files. Additionally, Github actions are also setup for the CI process in case we want an alternate pipeline build process (image below).

![exercise_CI](assets/exercise_CI.png)
Note: This is expected to fail and ideally the file reading process will be from S3 or anything other location.

### <u> Model versioning and hyper-param tuning </u>

Since the model performance holds less weightage in this exercise, we will focus on the next steps. Ideally, we should implement MLFlow with all our components for file versioning and use it for hyper parameter tuning in the train component. We can scale the pods for the training step in case we need to cover a wider param scan. Another alternate is Pachyderm but evaluating it against MLflow is not required at the moment.

### <u> Serving </u>

Initially, the plan was to use kf serving but after reviewing documentation and downstream feature richness, we have decidede to move with Seldon. Here are a few benefits

- Reusable inference servers - It provides out-of-the-box model servers for SKLearn, XGBoost, TF and MLFlow.
- Better documentation
- Coverts ML models to REST/gRPC microservices
- Advanced metrics and logging (Prometheus + Grafana)
- Explainers for models and a feedback mechanism for live learnings.
- A/B testing with canary, green-blue, shadow deployments.
- Otlier detection and more.

> The seldon-core installation with Helm consumed about 20% of the time in the process. Helm is confusing and lacks documentation, use Kustomize.

> Seldon-core's XGBoost server is the easiest way to deploy our model but due to a bug, it took almost a day to figure out why the deployments didn't work. We have raised a _Bug Report_ on github and found a way around.
> <br> <br>

## <u> Proof of a working deployment </u>

Let's start with a prediction generated using our pipeline for reference.
<br> <br>
![local_pred](assets/local_pred.png)
<br>
The is the probability of install for the test case in the first-row. We will ensure that we get the same probability from the seldon deployment.

Let's take a look at our deployment and ensure everything is working as expected.
<br>
![running_deployment](assets/running_deployment.png)
Everything looks okay (finally! after reading the source-code of seldon-core for a day). Now is a good time to test our server.
<br>
![serving_initialization](assets/serving_initialization.png)
<br>
Initialization seems to be okay, now we will test the first row from our test data to see if the deployment works.
![serving_test_response_1](assets/serving_test_response_1.png)
![serving_test_response_2](assets/serving_test_response_2.png)

Yay! It works.

---

## <u> Model Life Cycle </u>

Currently, we are not epxloring the logging, monitoring and A/B testing options but, **these are all available with the deployment**. If time permits, we can simulate a live server that samples 5K records per sec from the test data and requests the SeldonClient. That way we can simulate live traffic and can test our A/B tests or bandit stratergies with a simple change in our deployment yamls.
