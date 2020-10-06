#!/usr/bin/env python3
"""
 Copyright (c) 2018 Intel Corporation.
 Permission is hereby granted, free of charge, to any person obtaining
 a copy of this software and associated documentation files (the
 "Software"), to deal in the Software without restriction, including
 without limitation the rights to use, copy, modify, merge, publish,
 distribute, sublicense, and/or sell copies of the Software, and to
 permit persons to whom the Software is furnished to do so, subject to
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

import os
import sys
import logging as log

from openvino.inference_engine import IECore

class Network():
    
    def __init__(self):

        self.plugin = None
        self.network = None
        self.exec_network = None
        self.input_blob = None
        self.output_blob = None
        self.infer_request_handle = None

    def load_model(self, model, device, num_requests, cpu_extension = None):

        # Indicate the path to model .xml and .bin file
        model_xml = model
        model_bin = os.path.splitext(model_xml)[0] + ".bin"

        # Initialize the plugin
        self.plugin = IECore()

        # Define the network
        self.network = self.plugin.read_network(model = model_xml, weights = model_bin)
        
        # To add necessary extensions
        if cpu_extension and "CPU" in device:
            self.plugin.add_extension(cpu_extension, "CPU")

        # Check for supported layers 
        supported_layers = self.plugin.query_network(network = self.network, device_name = "CPU")

        # Check for any unsupported layers, and let the user know if anything is missing. Exit the program, if so.
        unsupported_layers = [l for l in self.network.layers.keys() if l not in supported_layers]
        if len(unsupported_layers) != 0:
            print("Unsupported layers found: {}".format(unsupported_layers))
            print("Check whether extensions are available to add to IECore.")
            exit(1)

        # Define the executable network
        self.exec_network = self.plugin.load_network(self.network, device_name = device, num_requests = num_requests)

        # Get the layers
        self.input_blob = next(iter(self.network.inputs))
        self.output_blob = next(iter(self.network.outputs))

        return 

    def get_input_shape(self):

        return self.network.inputs[self.input_blob].shape

    def exec_net(self, request_id, image):

        self.infer_request_handle = self.exec_network.start_async(request_id = request_id, inputs = {self.input_blob: image})

        return self.exec_network

    def wait(self, request_id):

        return self.exec_network.requests[request_id].wait(-1)

    def extract_output(self, request_id, output = None):
        
        if output:
            result = self.infer_request_handle.outputs[output]
        else:
            result = self.exec_network.requests[request_id].outputs[self.output_blob]
          
        return result
