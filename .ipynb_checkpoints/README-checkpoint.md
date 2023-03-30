# Sentinel: Command Line Interface
Command Line Interface and Python Library for running Sentinel algorithms locally on that old Toughbook you lugged out into the field (or your fancy desktop, or even the cloud!)


![gorillas (1)](https://user-images.githubusercontent.com/28448427/159202229-69af38ce-b487-46b4-9bea-53c477d7c5ab.gif)
> Example of customized behavioral model that can be run through this system. Custom species, sex, collar/no-collar models can also be created

## Purpose
The greatest issues conservationists face today include collecting and manually processing mountains of environmental data. These enormous costs come from collecting SD cards and manually processing hundreds of thousands of images. The slow time to get information from this collected data allows for no chance to take action directly on what’s going on. Solutions exist in the form of advancing artificial intelligence technologies but their technical difficulty puts them out of reach of conservationists. We seek to bridge that divide. Conservation X Labs aims to make the deployment of customized machine learning models as simple as possible across all endpoints (Sentinel Field-Hardware, Offline Laptops, Cloud). 

This software is designed to run custom offline machine learning models across many images/videos on customer laptops or desktops. This will likely be used in field scenarios where:
- Sorting into categories that you defined yourself! (This could include behavior (video), species, sex, collared - or anything else you like to seperate your data by)
- Data sorting is required without reliable internet connection
- Lighter-weight models that run on any old laptop
- Privacy is paramount 

In the near future we will offer common scenaros models as a free container. Right now this is only available to early Sentinel users. If you are interested in being an early user, please reach out to sentinel@conservationxlabs.org 

*Note: We recognize that requiring the use of the Command Line is not the most user friendly approach, so we are actively developing a graphical user interface (GUI). However this code will continue to be supported and form a defacto API of sorts.* 



## CLI Feature Progress
This tool is a work in progress. If there are feature requests (or bugs) please reach out to sentinel@conservationxlabs.org or add an issue.

- [x] Stable Command Line Interface to run image folders on custom Sentinel models 
- [x] Parallel processing
- [x] Integration into Timelapse workflow
- [ ] Creation of custom Timelapse template for auditing
- [ ] Publish pip package with entry points
- [ ] Python Scripting Capabilities
- [ ] Basic GUI
- [ ] Support for videos
- [ ] Model Feedback Loop

### Model Creation Progress
Models are currently made outside of this repository by Conservation X Labs, and served as Docker containers. Tools to create custom models will be published at a later date. However, our internal progress can be monitored here.

- [ ] GPU Support
- [ ] Creation of publicly available model(s) option for testing
- [ ] Integration of Megadetector and Megaclassifier
- [ ] Integration into Sentinel Model Marketplace


## High Level Overview

### Basic Controls (via Python)
This repo is the high-level functionality of the system, such as selecting:
- Organization/Model Selection
- Input Folders

>These instructions have been tested on Windows and Linux

### Docker: Organization-Specific Algorithms
We use Docker to manage the difficulties of different dependencies (Operating Systems, existing tensorflow installations) that will inevitably be present on people's systems. It also allows us to update/fix systems, algorithms on-the-go.

This wil be downloaded by the python script, so dont worry about downloading this, it will be done automatically. Each Conservation  X Labs customer will have a docker container with their most up-to-date algorithms pre-loaded with the latest TensorFlow libraries. As new/updated algorithms are made, your new algorithms can be found here.

>Please run the python script at least once before being offline to ensure your org's docker container is downloaded


## Instructions

Note: You will need around 2GB of spare space on your harddrive

### Installation

1. Install [Python](https://www.python.org/downloads/) OR (Optional) Install [Anaconda](https://www.anaconda.com/products/distribution) if you are concerned about your other code on your system. Anaconda also makes managing python versions and creating virtual environments very easy. (Make sure you are using Python 3!!)
2. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) 
3. Clone this repo either through command line (```git clone https://github.com/cxl-garage/sentinel-cli.git```) or use [GitHub Desktop](https://desktop.github.com/)
5. Open up a command line interface (PowerShell) (if you are using Anaconda, go to Prompt) 
6. Navigate to sentinel-cli github directory in command line
7. Download Sentinel Python Package ```pip install -r requirements.txt```
8. If using private algorithms (you should know if this is the case) - add the provided .json key to your setinel-cli directory
9. Make sure docker is running on your computer. If the program gives an API error, see more about starting docker [here](https://docs.docker.com/engine/install/linux-postinstall/)
10. Follow Usage Instructions below


## CLI (Command Line Interface) Example Command


### User Input (start with this)
```
  python app.py 
```
User will be prompted for paramaters in the command line. See API Guide below

### No user input (use this if you are running things again and again)
```
  python app.py --org <ORG_NAME> --model <MODEL_NAME> --input <INPUT_PATH> --output <OUTPUT_PATH> --thresh <CONFIDENCE_THRESHOLD> --output_style <HIERACHY>
```

Note: You should put your stuff between the <>

API Guide:

- --org: Name of organization that owns the algorithm (future public docker container will be "cxl"). Please reach out to Conservation X Labs if this is unknown
- --model: Model name (this should be known by org)
- --key: Path to credential key (provided by CXL to organization) (necessary to download model the first time) (Full and relative paths should work)
- --input: Input Directory Path (Full and relative paths should work)
- --output: Output Directory Path (Full and relative paths should work)
- --thresh: The confidence threshold (0-100) of the chosen model. Note that early models by CXL have not been normalized and so confidence may need to be set lower than normal (25-30)
- --output_style: How to display output data - files always have the same name as original input. 
  - "class": (default) images are tagged with bounded boxes and are saved into class (rat, cat, zebra etc.) and empty folders
  - "hierachy": images are tagged with bounded boxes and saved in same structure as the input directory (but in the output directory)
  - "flat": images are tagged with bounded boxes and are saved all in the output folder with no hierachy
  - "timelapse": images are saved in hierachy structure but an additional Timelapse .json is generated for input into Timelapse. No bounded boxes are tagged
  - "none": images are not saved. Only csv of detections is generated
- --input size: size of images into model (default is 256). If you want to change use 128 or 512.
- --output_size: size of images saved to output directory 
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
