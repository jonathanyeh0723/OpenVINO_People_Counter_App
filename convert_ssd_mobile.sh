#!/bin/bash
python3 /opt/intel/openvino_2020.3.194/deployment_tools/model_optimizer/mo.py \
        --input_model frozen_inference_graph.pb \
        --tensorflow_use_custom_operations_config /opt/intel/openvino_2020.3.194/deployment_tools/model_optimizer/extensions/front/tf/ssd_v2_support.json \
        --tensorflow_object_detection_api_pipeline_config pipeline.config --reverse_input_channels \
        -o ../model/ssd_mobilenet_v2
