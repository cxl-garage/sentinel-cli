# Sentinel: Command Line Interface
Command Line Interface and Python Library for running Sentinel algorithms locally

## Purpose
Conservation X Labs aims to make the deployment of customized machine learning models as simple as possible across all endpoints (Sentinel Field-Hardware, Offline Laptops, Cloud). 

This software is designed to run custom offline machine learning models across many images/videos on customer laptops or desktops. This will likely be used in field scenarios where:
- Data sorting is required without reliable internet connection. 
- Privacy is paramount


## High Level Overview

### Basic Controls (via Python)
This repo is the high-level functionality of the system, such as selecting:
- Organization/Model Selection
- Input Folders

### Docker: Organization-Specific Algorithms
We use Docker to manage the difficulties of different dependencies (Operating Systems, existing tensorflow installations) that will inevitably be present on people's systems. It also allows us to update/fix systems, algorithms on-the-go.
This wil be downloaded by the python script, so dont worry about downloading this, it will be done automatically. Each Conservation  X Labs customer will have a docker container with their most up-to-date algorithms pre-loaded with the latest TensorFlow libraries. As new/updated algorithms are made, your new algorithms can be found here.

===Please run the python script at least once before being offline to ensure your org's docker container is downloaded===


## Installation Instructions

1. Install [Python](https://www.python.org/downloads/)
2. Download Sentinel Python Package ```pip install sentinel_local```
3. If using private algorithms (you should know if this is the case) - add the provided .json key to your machine
4. Follow Usage Instructions

## CLI (Command Line Interface)
```
  sentinel_download --org <ORG_NAME> --key <PATH_TO_JSON_KEY>
  
```
```
  sentinel_run --org <ORG_NAME> --model <model_name> --input_folder <PATH_TO_INPUT_FODLER>
```
## Python Scripting
```
  import sentinel_local
  sentinel_local.download(org,key)
  sentinel_local.run()
```
