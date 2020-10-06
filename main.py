"""People Counter."""
"""
 Copyright (c) 2018 Intel Corporation.
 Permission is hereby granted, free of charge, to any person obtaining
 a copy of this software and associated documentation files (the
 "Software"), to deal in the Software without restriction, including
 without limitation the rights to use, copy, modify, merge, publish,
 distribute, sublicense, and/or sell copies of the Software, and to
 permit person to whom the Software is furnished to do so, subject to
 the following conditions:
 The above copyright notice and this permission notice shall be
 included in all copies or substantial portions of the Software.
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
 LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
 WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import argparse
import cv2
import logging as log

import sys
import time
import socket
import paho.mqtt.client as mqtt
import json
import math
import os

from inference import Network

# Set the MQTT server environment variables
HOSTNAME = socket.gethostname()
IPADDRESS = socket.gethostbyname(HOSTNAME)
MQTT_HOST = IPADDRESS
MQTT_PORT = 1884
MQTT_KEEPALIVE_INTERVAL = 60

def connect_mqtt():

    client = mqtt.Client()
    client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)

    return client

def get_args():

    # Create the parser object
    parser = argparse.ArgumentParser()

    # Create the arguments
    # Required 
    parser.add_argument("-m", "--model", required = True, type = str, help = "The location of model .xml file")
    parser.add_argument("-i", "--input", required = True, type = str, help = "The path to input image or video")
    
    # Optional 
    parser.add_argument("-d", "--device", default = "CPU", type =str, help = "To specify target device used for inference, CPU, GPU, VPU etc.")
    parser.add_argument("-l", "--cpu_extension", required = False, type = str, default = None, help = "MKLDNN (CPU)-targeted custom layers. Absolute path to a shared library")
    parser.add_argument("-pt", "--prob_threshold", default = 0.5, type = float, help = "Probability threshold for detections filtering")
    parser.add_argument("-c", "--color", default = "GREEN", type = str, help = "The color of the bounding boxes to draw; RED, GREEN or BLUE")
    parser.add_argument("-at", "--alert_time", default = 20.0, type = float, help = "The duration people stay in the frame")

    args = parser.parse_args()

    return args

def infer_on_stream(args, client):

    # Set flag for the input 
    single_image_mode = False
    
    # Instantiate current inference request
    cur_request_id = 0
    
    # Initialize the plugin
    plugin = Network()

    # Load model, and get the input shape
    plugin.load_model(args.model, args.device, cur_request_id, args.cpu_extension)
    n, c, h, w = plugin.get_input_shape()

    ### Checking for the feed input file
    # CAM
    if args.input == 'CAM':
        input_stream = 0

    # Image
    elif args.input.endswith('.jpg') or args.input.endswith('.bmp') :
        single_image_mode = True
        input_stream = args.input

    # Video
    else:
        input_stream = args.input
        assert os.path.isfile(args.input), "Specified input file doesn't exist"
    
    # Create the VideoCapture object, and have it opened
    cap = cv2.VideoCapture(input_stream)

    if input_stream:
        cap.open(args.input)

    if not cap.isOpened():
        log.error("ERROR! Unable to open video source")
    ###

    # Grab the dimension of width and height
    global initial_w, initial_h
    initial_w = cap.get(3)
    initial_h = cap.get(4)

    # Set initial parameters
    temp = 0
    fp = 0
    last_count = 0
    total_count = 0
    duration = 0

    # Iterate the frame until the video ends
    while cap.isOpened():
        flag, frame = cap.read()
        if not flag:
            break
        key_pressed = cv2.waitKey(60)

        ### Preprocessing
        # Resize to model's input w x h
        p_frame = cv2.resize(frame, (w, h))

        # Transpose the layout from hwc to chw
        p_frame = p_frame.transpose((2, 0, 1))

        # Reshape to model's shape n x c x h x w
        p_frame = p_frame.reshape((n, c, h, w))
        ###

        # Perform async_inference
        plugin.exec_net(cur_request_id, p_frame)
        inf_start = time.time()

        # Get the output result
        if plugin.wait(cur_request_id) == 0:
            result = plugin.extract_output(cur_request_id)
            det_time = time.time() - inf_start

            # Draw the bounding box
            frame, current_count, d, fp = draw_boxes(frame, result, args, temp, fp)
    
            # Print the inference time
            inf_time_message = "Inference time: {:.3f}ms".format(det_time * 1000)
            cv2.putText(frame, inf_time_message, (15, 15), cv2.FONT_HERSHEY_COMPLEX, 0.5, (200, 10, 10), 1)

            ### People Counting ###
            # When new person enters into the frame
            if current_count > last_count: # New entry
                start_time = time.time()
                total_count = total_count + current_count - last_count
                client.publish("person", json.dumps({"total": total_count}))  
            
            if current_count < last_count:
                duration = int(time.time() - start_time)
                client.publish("person/duration", json.dumps({"duration": duration}))

            # To check lost frames for false positive cases           
            lost_info = "Lost frame: %d" %(fp - 1)
            cv2.putText(frame, lost_info, (15, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (200, 10, 10), 1)             
               
            # Warning if people staying time > alert time 
            if duration >= args.alert_time:
                cv2.putText(frame, 'CAUTION! Staying longer than ' + str(args.alert_time) + ' seconds', (15, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1)

            client.publish("person", json.dumps({"count": current_count}))
            last_count = current_count
            
            temp = d
            ###----------------###

            # Break if escape key is pressed
            if key_pressed == 27:
                break

        # Send the information to FFmpeg server
        sys.stdout.buffer.write(frame)
        sys.stdout.flush()

        # Image mode
        if single_image_mode:
            cv2.imwrite('output_image.jpg', frame)

    # Release all. Destroy OpenCV windows, and disconnect the MQTT
    cap.release()
    cv2.destroyAllWindows()
    client.disconnect()

def draw_boxes(frame, result, args, x, k):

    # Customize the color space of bounding box, if not assign default will be 'GREEN'
    colors = {"BLUE": (255, 0, 0), "GREEN": (0, 255, 0), "RED": (0, 0, 255)}
    if args.color: 
        draw_color = colors.get(args.color)
    else:
        draw_color = colors["GREEN"]

    current_count = 0
    distance = x

    for obj in result[0][0]:
        conf = obj[2]
        if conf >= args.prob_threshold:
            xmin = int(obj[3] * initial_w)
            ymin = int(obj[4] * initial_h)
            xmax = int(obj[5] * initial_w)
            ymax = int(obj[6] * initial_h)
            class_id = int(obj[1])
            
            # If the probability threshold is crossed, then count the people, and draw the bounding box
            current_count += 1
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), draw_color, 3)
           
            det_label = str(class_id)
            cv2.putText(frame, "label: " + det_label + ' ' + str(round(obj[2] * 100, 1)) + ' %', (xmin, ymin - 7), cv2.FONT_HERSHEY_COMPLEX, 0.6, draw_color, 2)
            enter_time = time.time()

            # To calculate the distance
            c_y = frame.shape[0] / 2    
            c_x = frame.shape[1] / 2
            
            mid_y = (ymin + ymax) / 2
            mid_x = (xmin + xmax) / 2
                
            distance =  math.sqrt(math.pow(mid_x - c_x, 2) +  math.pow(mid_y - c_y, 2) * 1.0) 
            k = 0

    if current_count < 1:
        k += 1
            
    if distance > 0 and k < 15:
        current_count = 1 
        k += 1 
        if k > 100:
            k = 0
                
    return frame, current_count, distance, k

def main():
    args = get_args()
    client = connect_mqtt()
    infer_on_stream(args, client)

if __name__ == "__main__":
    main()
