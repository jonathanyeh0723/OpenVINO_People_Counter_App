# Write-Up

The following address an explanation of the process behind converting any custom layers, as well as explaining the potential reasons for handling custom layers in a trained model.

## Explaining Custom Layers in OpenVINO™

According to [Custom Layers Guide](https://docs.openvinotoolkit.org/latest/openvino_docs_HOWTO_Custom_Layers_Guide.html), we learn that custom layers are layers that are not included in the list of known layers. If your topology contains any layers that are not in the list of known layers, the Model Optimizer classifies them as custom.

Before building the model's internal representation, the Model Optimizer will search the list of known layers for each layer contained in the input model topology, optimizing the model, and then producing the Intermediate Representation files.

The Inference Engine loads the layers from the input model IR files into the specified device plugin, which will search a list of known layer implementations for the device.

On the other hand, because Inference Engine use different data layouts of tensors compared to TensorFlow, so we'll have to do data preprocessing in advance. Then, these tensors are flattened out to required data format for inference. The results Intermediate Representation including .xml and .bin files, which detailing our topology and weights.

![custom_layer](./images/custom_layer.jpg)

## Compare Model Performance

My method(s) to compare model performance before and after conversion is to checking the memory size. It seems that they are almost the same so I bet this is not a proper approach. 

As for differences between Edge and Cloud computing, Edge Computing is chosen for operations with privacy and low latency concerns. On the other hand, Cloud Computing is more suitable for dealing with big data.

## Assess Model Use Cases the given scenario.

The use cases of a people counter app are quite extensive, such as:
- metro station
- retail chain
- public venue
- bank system
- airline

For example, we can customize an alarm or notification once the counter detects above a certain number of people on video, or people are on camera longer than a certain length of time.

## Assess Effects on End User Needs

To deploy people counter app to the edge, we must consider end user requirement with great attention. These factors are lighting, model accuracy, camera focal length/image size, and so forth. Since it does exist some trade-off between performance and cost, the best fit is depended on given scenario.

For instance, imagine a public venue host would like to control the total people in the active area to maintain the quality of this event. Since the budget is limited, it would be great to have a cost-effective and lightweight smart IoT device to count person automatically in the entrance, rather than hiring a guard to watch the surveillance system and do calculations manually. 

In this case, we can suppose the hardware requirement is not that critical and some performance deviation is acceptable, so probably a Raspberry Pi + NCS2 will be a suitable solution.

## Documenting Model Research

Before using Intel existing IR to feed to the inference engine, I’ve tried three approaches. These steps are detailed as following:


- **Model 1: SSD MobileNet V1 COCO**
  - [Click to Download](http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v1_coco_2018_01_28.tar.gz)
  - Using the following commands to download public model, unpack the file, and utilize the Model Optimizer to convert it to the Intermediate Representation.
  
  ```
  wget http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v1_coco_2018_01_28.tar.gz
  tar ssd_mobilenet_v1_coco_2018_01_28.tar.gz
  cd cd ssd_mobilenet_v1_coco_2018_01_28/
  python3 /opt/intel/openvino/deployment_tools/model_optimizer/mo.py --input_model frozen_inference_graph.pb --tensorflow_object_detection_api_pipeline_config pipeline.config --reverse_input_channels --tensorflow_use_custom_operations_config /opt/intel/openvino/deployment_tools/model_optimizer/extensions/front/tf/ssd_support.json
  ```
  
  We should be able to see the following, if successful:
  
  ```
  [ SUCCESS ] Generated IR version 10 model.
  [ SUCCESS ] XML file: /home/intel/tmp/1001/people-counter-python/model/ssd_mobilenet_v1_coco_2018_01_28/./frozen_inference_graph.xml
  [ SUCCESS ] BIN file: /home/intel/tmp/1001/people-counter-python/model/ssd_mobilenet_v1_coco_2018_01_28/./frozen_inference_graph.bin
  [ SUCCESS ] Total execution time: 27.04 seconds. 
  [ SUCCESS ] Memory consumed: 455 MB.
  ```
  
  - Checking the results: Apparently this is not an appropriate model to this application. There are too many bounding boxes popped out when running the code, thus resulting in failed inference.
  
- **Model 2: SSD Inception V2 COCO**
  - [Click to Download](http://download.tensorflow.org/models/object_detection/ssd_inception_v2_coco_2018_01_28.tar.gz)
  - Using the following commands to download public model, unpack the file, and utilize the Model Optimizer to convert it to the Intermediate Representation.
  
  ```
  wget http://download.tensorflow.org/models/object_detection/ssd_inception_v2_coco_2018_01_28.tar.gz
  tar xvf ssd_inception_v2_coco_2018_01_28.tar.gz
  cd ssd_inception_v2_coco_2018_01_28
  python3 /opt/intel/openvino/deployment_tools/model_optimizer/mo.py --input_model frozen_inference_graph.pb --tensorflow_object_detection_api_pipeline_config pipeline.config --reverse_input_channels --tensorflow_use_custom_operations_config /opt/intel/openvino/deployment_tools/model_optimizer/extensions/front/tf/ssd_v2_support.json
  ```

  We should be able to see the following, if successful:
  
  ```
  [ SUCCESS ] Generated IR version 10 model.
  [ SUCCESS ] XML file: /home/intel/tmp/1001/people-counter-python/model/ssd_inception_v2_coco_2018_01_28/./frozen_inference_graph.xml
  [ SUCCESS ] BIN file: /home/intel/tmp/1001/people-counter-python/model/ssd_inception_v2_coco_2018_01_28/./frozen_inference_graph.bin
  [ SUCCESS ] Total execution time: 33.72 seconds. 
  [ SUCCESS ] Memory consumed: 758 MB.
  ```

  - Checking the results: This model works better than the first one but lack accuracy as the bounding box sometimes will disappear so that the app can't count people correctly. 
  
  - I tried to adjust the probability threshold but in vain. It seems the results do not get better.

- **Model 3: SSD MobileNet V2 COCO**
  - [Click to Download](http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v2_coco_2018_03_29.tar.gz)
  - Using the following commands to download public model, unpack the file, and utilize the Model Optimizer to convert it to the Intermediate Representation.
  
  ```
  wget http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v2_coco_2018_03_29.tar.gz
  tar xvf ssd_mobilenet_v2_coco_2018_03_29.tar.gz
  cd ssd_mobilenet_v2_coco_2018_03_29
  python3 /opt/intel/openvino_2020.3.194/deployment_tools/model_optimizer/mo.py --input_model frozen_inference_graph.pb --tensorflow_use_custom_operations_config /opt/intel/openvino_2020.3.194/deployment_tools/model_optimizer/extensions/front/tf/ssd_v2_support.json --tensorflow_object_detection_api_pipeline_config pipeline.config --reverse_input_channels
  ```

  We should be able to see the following, if successful:
  
  ```
  [ SUCCESS ] Generated IR version 10 model.
  [ SUCCESS ] XML file: /home/intel/tmp/1001/people-counter-python/model/ssd_mobilenet_v2_coco_2018_03_29/./frozen_inference_graph.xml
  [ SUCCESS ] BIN file: /home/intel/tmp/1001/people-counter-python/model/ssd_mobilenet_v2_coco_2018_03_29/./frozen_inference_graph.bin
  [ SUCCESS ] Total execution time: 38.33 seconds. 
  [ SUCCESS ] Memory consumed: 660 MB.
  ```
  
  - Checking the results: Similarly, this model can capture person from the frame. However, it still loses some accuacy.
  
  - The attempt to raising the confidence threshold does not seem improvement.
  
- **Model 4: Intel Pre-trained model: person-detection-retail-0013**
  - [Check out this link](https://docs.openvinotoolkit.org/latest/omz_models_intel_person_detection_retail_0013_description_person_detection_retail_0013.html)
  - Using the Model Downloader to get Intermediate Representation directly.
  
  ```
  python3 /opt/intel/openvino/deployment_tools/tools/model_downloader/downloader.py --name person-detection-retail-0013 --precision FP32
  ```

  The IR files will be downloaded to intel/person-detection-retail-0013/FP2
  
  We shall be able to locate the binary file and model structure there.
  ```
  person-detection-retail-0013.bin  person-detection-retail-0013.xml
  ```
  
  - Checking the results: The model works very well with this app. We can see obvious improvement from the results.
