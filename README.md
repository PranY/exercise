The objective of this exercise to build an end-to-end pipeline that is satisfies all the requirements mentioned in the `Task.md` file.

There is an option to work with Apache Airflow or Kubeflow. Since the developer is new to both, it is fairly straightforward to go with the Airflow approach and builds DAGs (ingest >> preprocess >> train >> evaluate >> deploy). Airflow offers numerous operator and the `PythonOperator`can easily help plug the functions and build the pipeline.

However, the developer knows that such an implementation comes at a cost. For instance, he will need to move to `KubernetesOperator` to run the tasks on a Kubernetes cluster for scalability. Additionally, he will need to opt for `CeleryExecutor` or any other distributed executor because sequential execution may become a bottleneck and under-utilize workers. Although, there should be a work around to use Airflow for the most part, it needs further evaluation.

Considering the above points (and knowing that Unity is using GCP services), it is a good idea to use Kubeflow pipelines.

Now, focusing on the architecture, there are broadly 3 steps:
- **Data** ingestion, validation, transformation, feature-generation, splitting.
- **Model** training, evaluation, serving.
- **Life cycle** monitoring, logging, iterating model.

There are numerous ways to approach the above steps and below is a purely GCP-based example for the same, courtesy Google blogs.

![architecture](https://cloud.google.com/solutions/images/architecture-for-mlops-using-tfx-kubeflow-pipelines-and-cloud-build-6-ci-cd-kubeflow.svg)

---

## Solution

The pipeline solution will follow a similar but scaled-down pattern. The component structure will be preprocess >> train >> test >> deploy. Github actions will help with CI. The docker containers will be accessible via github (no secrets for sharing purpose, but the password will be changed in a week).