## Sentinel Laptop: Beta Version
import argparse
import os
import docker
import GPUtil
import json
import numpy as np
import os
from PIL import Image, ImageDraw
import requests
import tqdm
import time
import csv
from multiprocessing import Pool
import multiprocessing
from contextlib import closing
import glob
import sys
import shutil
import pandas as pd
from datetime import datetime

def generate_timelapse_file(opt):
    print('\nGenerating timelapse json file')
    shutil.copy('TimelapseTemplate.tdb', f"{opt.output}/TimelapseTemplate.tdb")

    df = pd.read_csv(f'{opt.output}/detections.csv')
    now = datetime.now()

    dict = {}

    dict['info'] = {"detector": f'{opt.org}_{opt.model}',
                    "detection_completion_time": now.strftime("%Y-%m-%d, %H:%M:%S"),
                    "format_version": "1.0"}

    dict['detection_categories'] = {"1": "rat"}
    dict['classification_categories'] = {"1": "rat"}


    image_list = []

    images = df['Path'].unique()
    pbar = tqdm.tqdm(total=len(images))
    k= 0
    while k < len(images):


        x = []
        bb = df[(df['Path']==images[k]) & (df['Confidence'] !=0)]
        m = 0
        while m < len(bb):


            if opt.output_style == 'flat':
                out_path = r'{}/{}'.format(opt.output,os.path.basename(bb['Path'][0]))
            elif opt.output_style == 'hierachy' or opt.output_style == 'timelapse':
                out_path = bb['Path'][0].replace(f'{opt.input}\\','')
            elif opt.output_style == 'none':
                out_path = bb['Path'][0]
            elif opt.output_style == 'class':
                out_path = r'{}/{}/{}'.format(opt.output,bb['Class'][0],os.path.basename(os.path.basename(bb['Path'][0])))

            bb_coco = eval(bb['Bounded Box'][m])
            md_bb_list = [bb_coco[1],bb_coco[0],bb_coco[3]-bb_coco[1],bb_coco[2]-bb_coco[0]]
            x.append({"category": str(int(float(bb['Class'][m]))), 
                    "conf": float(bb['Confidence'][m]),
                    "bbox": md_bb_list,
                    "classifications":[[str(int(float(bb['Class'][m]))),1]]})
            m = m + 1

        image_list.append({"file": out_path.replace('\\', '/'),
                        "max_detection_conf": float(bb['Confidence'].max()),
                        "detections":x})
        pbar.update(1)
        k = k + 1
    pbar.close()
    dict['images'] = image_list
    json_object = json.dumps(dict, indent = 3) 
    with open(r'{}/timelapse.json'.format(opt.output), 'w') as outfile:
        outfile.write(json_object)


## Function to process the image (this is a threaded function)
def process(filename):
    detections = []
    # Convert Confidence Threshold to 0-1 from 0-100
    confidence_threshold = float(os.environ.get('THRESHOLD'))/100
    output = os.environ.get('OUTPUT')
    input  = os.environ.get('INPUT')
    output_size = os.environ.get('OUTPUT_SIZE')
    input_size  = int(os.environ.get('INPUT_SIZE'))
    output_style  = os.environ.get('OUTPUT_STYLE')
    model  = os.environ.get('MODEL')
    # Make pictures with bounded boxes if requested
    

    if len(glob.glob(f"{output}/**/{os.path.basename(filename)}")) != 0:
        return 'Processed'
    else:
        try:
            t1 = time.time()         
            img = Image.open(filename)      
            image = img.resize([input_size,input_size])
            if output_size != 'None':
                image_out = img.resize([int(output_size),int(output_size)])
            else:
                image_out = img
            width_out, height_out = image_out.size
            
            # Normalize and batchify the image
            im = np.expand_dims(np.array(image), 0).tolist()
            
            t2 = time.time() 

            url = 'http://localhost:8501/v1/models/{}:predict'.format(model)
            data = json.dumps({"signature_name": "serving_default", "instances": im})
            headers = {"content-type": "application/json"}
            json_response = requests.post(url, data=data, headers=headers)
            predictions = json.loads(json_response.text)['predictions'][0]
            t3 = time.time() 

            # Check there are any predictions
            if predictions['output_1'][0] > confidence_threshold:

                ## Continue to loop through predictions until the confidence is less than specified confidence threshold
                x = 0
                while True:
                    if predictions['output_1'][x]>confidence_threshold and x < len(predictions['output_1']):
                        bbox = [i / input_size for i in predictions['output_0'][x]]
                        class_id = predictions['output_2'][x]
                        confidence = predictions['output_1'][x]

                        class_name = class_id

                        # Make pictures with bounded boxes if requested
                        # Draw bounding_box
                        
                        if output_style != 'timelapse':
                            draw = ImageDraw.Draw(image_out)
                            draw.rectangle([(bbox[1]*width_out,bbox[0]*height_out),(bbox[3]*width_out,bbox[2]*height_out)],outline='red',width=3)

                            # Draw label and score
                            result_text = str(class_name) + ' (' + str(confidence) + ')'
                            draw.text((bbox[1] + 10, bbox[0] + 10),result_text,fill='red')
                        
                        detections.append([os.path.basename(filename),class_name,confidence,filename,bbox])

                        x = x + 1
                    else:
                        break
            else:
                class_id = 'Blank'
                detections.append([os.path.basename(filename),0,0,filename,''])


            if output_style == 'flat':
                out_path = r'{}/{}'.format(output,os.path.basename(filename))
            elif output_style == 'hierachy' or output_style == 'timelapse':
                out_path = r'{}/{}'.format(output,filename.replace(input,''))
            elif output_style == 'class':
                out_path = r'{}/{}/{}'.format(output,class_id,os.path.basename(filename))
            elif output_style == 'none':
                pass   
            else:
                print('Error: Output Style is incorrect') 
            
            if output_style != 'none':
                try:
                    image_out.save(out_path)
                except Exception as e:
                    os.makedirs(out_path.replace(os.path.basename(filename),''))
                    image_out.save(out_path)
            t4 = time.time() 
        except Exception as e:
            print(e)
            detections.append([os.path.basename(filename),99,0,filename,''])
        return detections


def main(opt,container=None):

    os.environ['THRESHOLD'] = str(opt.thresh)
    os.environ['OUTPUT'] = opt.output
    os.environ['INPUT'] = opt.input
    os.environ['OUTPUT_SIZE'] = str(opt.output_size)
    os.environ['INPUT_SIZE'] = str(opt.input_size)
    os.environ['OUTPUT_STYLE'] = str(opt.output_style)
    os.environ['MODEL'] = opt.model   

    # Check resources available on current machine
    try:
        GPU_num = len(GPUtil.getAvailable())
        if GPU_num == 0:
            print('Starting tensorflow container optimized for CPUs')
        else:
            print('GPU support does not yet exist')
    except Exception as e:
        print('Error')
        GPU_num = 'Unknown'
    print(f"CPUs Available: {os.cpu_count()} GPUs Available: {GPU_num}")
    time.sleep(3)


    ## Make list of files
    images = []

    for path, subdirs, files in os.walk(opt.input):
        for file in files:
            if file.endswith(".jpg") or file.endswith(".jpeg") or file.endswith(".png") or file.endswith(".JPG") or file.endswith(".JPEG") or file.endswith(".PNG"):
                images.append(os.path.join(path, file))
    if opt.max_images != None:
        images = images[:opt.max_images]
    
    if len(images) == 0:
        exit('No images found')




    num_workers = multiprocessing.cpu_count() - 2
    print(f'\nProcessing on {num_workers} parallel threads')
    pbar = tqdm.tqdm(total=len(images))
    image_count = 0
    empty_count = 0
    with open(f'{opt.output}/detections.csv', 'a',newline='') as file:
        fieldnames = [['File','Class','Confidence','Path','Bounded Box']]
        writer = csv.writer(file)
        writer.writerows(fieldnames)
        detection_count = 0
        with closing(multiprocessing.Pool(processes=num_workers)) as pool:
            detections = pool.imap_unordered(process,images)
            # open file and write out all rows from incoming lists of rows
            for detection in detections:
                detection_count = detection_count + 1
                if detection=='Processed':
                    pbar_text = 'Already Processed'
                if detection[0][2] != 0:
                    detection_count = detection_count + 1
                else:
                    empty_count = empty_count + 1
                pbar_text = f'Found {detection_count} objects in {image_count} images. {empty_count} empty images'
                writer.writerows(detection)
                
                pbar.set_description(pbar_text, refresh=True)
                pbar.update(1)
                image_count = image_count + 1

    pbar.close()

    if opt.output_style == 'timelapse':
        generate_timelapse_file(opt)
    

## Set up the processing parameters and fill in anything not covered by CLI parameters with user input
def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--download', action='store_true',
                    help='Download image') 
    parser.add_argument('--org', type=str,
                        help='which org to run')                
    parser.add_argument('--model', type=str,
                        default=256, help='which model to run')                      
    parser.add_argument('--input', type=str,
                        help='Folder to be processed')
    parser.add_argument('--output', type=str,
                        help='Folder to where results are put')
    parser.add_argument('--key', type=str,
                        help='Path to auth key')                                                    
    parser.add_argument('--thresh', type=int,
                        default=40, help='threshold of model')
    parser.add_argument('--output_style', type=str,
                        default='class', help='Download image') 
    parser.add_argument('--input_size', type=int,
                        default=256, help='size of images into model')
    parser.add_argument('--max_images', type=int,
                        help='size of images into model')
    parser.add_argument('--output_size', type=int,
                        help='size of images into model')
    parser.add_argument('--overwrite', action='store_true',
                        help='size of images into model')
    parser.add_argument('--only_timelapse',action='store_true',
                        help='Only run timelapse json creation')               
    opt = parser.parse_args()

    if opt.only_timelapse:
        generate_timelapse_file(opt)
        sys.exit(1)
    

    
    client = docker.from_env()

    container_name = "us-west2-docker.pkg.dev/sentinel-project-278421/{}/{}".format(opt.org,opt.org)

    while True:
        ## Check Organization Bucket
        if opt.org is None:
            opt.org = input("Organization Name: ")
        try:
            containers = client.containers.list(filters={"name":f"sentinel_{opt.org}"})
            if len(containers) == 0:
                # Download and start container if necessary
                client.containers.prune()
                print('Starting container... (must be connected to internet for first time download)')
                container = client.containers.run(container_name,detach=True, name=f'sentinel_{opt.org}',ports={8501:8501},cpu_count=5,mem_limit='5g')    
                print('Container created successfully')
                time.sleep(5)
                break
            else:
                print('Attaching to existing container')
                container = client.containers.get(containers[0].name)
                break
        except Exception as e:
                
                if opt.key is None:
                    opt.key = input("Path to credential key: ")
                
                query = f'cat {opt.key} | docker login -u _json_key_base64 --password-stdin https://us-west2-docker.pkg.dev'
                print(query)
                os.system(query)
                try:
                    print(f'Downloading Image from Google Cloud Platform with {opt.key} credentials')
                    client.images.pull(container_name)
                except Exception as e:
                    print(e)
                    print('Error finding model. Please check organization and key.')
                    sys.exit()
                    
    
    if opt.model is None:
        opt.model = input("Model: ")

    while True:
        if opt.input is None:
            opt.input = input("Input Folder: ")
        # Check the input folder exists (exit if it doesnt)
        if not os.path.exists(opt.input):
            opt.input = input('Input folder does not exist... Please try again: ')
        else:
            break
        
    if opt.output is None:
        opt.output = input("Output Folder (leave blank if same as input folder): ")
        if opt.output == '':
            opt.output = opt.input
    if opt.output == 'input':
        opt.output = opt.input

    

    if opt.overwrite:
        try:
            shutil.rmtree(opt.output)
        except OSError as e:
            print("Error: %s : %s" % (opt.output, e.strerror))
    # Check if output folder exists, and create it if it doesn't
    if not os.path.exists(opt.output):
        print('Output folder does not exist... Creating.')
        os.makedirs(opt.output)
        client = docker.from_env()
    
    
    main(opt,container)
    
    ## Clean up
    print('\nShutting down container')
    container.kill()
    client.containers.prune()


if __name__ == '__main__':
    run()