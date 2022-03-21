# Sentinel: Command Line Interface
Command Line Interface and Python Library for running Sentinel algorithms locally

## Purpose
Conservation X Labs aims to make the deployment of customized machine learning models as simple as possible across all endpoints (Sentinel Field-Hardware, Offline Laptops, Cloud). 

In the near future we will offer common models as a free container

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

## CLI (Command Line Interface) Example Command

### User Input 
```
  python app.py 
  
```
User will be prompted for paramaters in the command line. See API Guide below

### No user input
```
  python app.py --org <ORG_NAME> --model <MODEL_NAME> --input <INPUT_PATH> --output <OUTPUT_PATH> --thresh <CONFIDENCE_THRESHOLD> --output_style <HIERACHY>
  
```

API Guide:

- --org: Name of organization that owns the algorithm (future public docker container will be "cxl"). Please reach out to Conservation X Labs if this is unknown
- --model: Model name (this should be known by org)
- --key: Path to credential key (provided by CXL to organization) (necessary to download model the first time)
- --input: Input Directory Path
- --output: Output Directory Path
- --thresh: The confidence threshold (0-100) of the chosen model. Note that early models by CXL have not been normalized and so confidence may nned set be lower than normal (25-30)
- --output_style: How to display output data - files always have the same name as original input. 
  - "hierachy": (default) images are tagged with bounded boxes and saved in same structure as the input directory (but in the output directory)
  - "flat": images are tagged with bounded boxes and are saved all in the output folder with no hierachy
  - "class": images are tagged with bounded boxes and are saved into class (rat, cat, zebra etc.) and empty folders
  - "timelapse": images are saved in hierachy structure but an additional Timelapse .json is generated for input into Timelapse. No bounded boxes are tagged
  - "none": images are not saved. Only csv of detections is generated
- --max_images: limit the number of images to process. Default behavior is to process all images in directory (and subdirectories)
- --overwrite: clear the output directory (useful if re-running the script)
- --only_timelapse: run the timelapse generator only (note that other variables are still needed)


Tips:
- Put quotes around the input/output paths
- Paramaters can be left blank, but user will be prompted 
- Your system may require python3 instead of python


## Python Scripting (coming soon...)
```
  import sentinel_local
```
