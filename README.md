# gcp-logging-retrieved

Retrieve logs from Cloud logging

## Requirements

- Python 3.6+

## Setup

1. Create configuration file

```
$ touch config.yaml
$ vi config.yaml

startTime: "2021-03-01T00:00:00.000Z"
endTime: "2021-03-01T03:00:00.000Z"
# google cloud logging query statement
queryStatement: 'resource.type="k8s_container" resource.labels.cluster_name="dev-test-gke-cluster" resource.labels.namespace_name="test-ns" resource.labels.container_name="dev-project"'
#filter logs
field: 'textPayload'
# The script breaks down time range into several small intervals to speed up, decrease the value if google api limit is exceeded.
interval: 90
# multiprocessing
maxWorkers: 4
```

2. Google authentication

a. Using environment variable

- GCP Dashboard > IAM&Admin > Services Accounts > Create a service account with Logging Admin role

```
$ export GOOGLE_APPLICATION_CREDENTIALS=<<PATH_TO_SERVICE_ACCOUNT_JSON_FILE>>
```

b. Using json file

Save service account json file (keyfile.json) in executable script or binary

c. Using gcloud

```
$ gcloud init
$ gcloud auth application-default login
```

3. Run the script

```
$ pip install -r requirements.txt
$ python main.py -h
$ python main.py
```

## Execute as binary file in Mac OSX

```
$ curl -L https://github.com/bangnh1/gcp-logging-retrieved/releases/download/v0.0.1/gcp-logging-retrieved -o gcp-logging-retrieved
$ export GOOGLE_APPLICATION_CREDENTIALS=<<PATH_TO_SERVICE_ACCOUNT_JSON_FILE>>
$ ./gcp-logging-retrieved -c config.yaml
```
