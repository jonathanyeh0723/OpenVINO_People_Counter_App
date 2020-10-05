# Write-Up

The following address an explanation of the process behind converting any custom layers, as well as explaining the potential reasons for handling custom layers in a trained model.

## Explaining Custom Layers in OpenVINO™

According to [Custom Layers Guide](https://docs.openvinotoolkit.org/latest/openvino_docs_HOWTO_Custom_Layers_Guide.html), we learn that custom layers are layers that are not included in the list of known layers. If your topology contains any layers that are not in the list of known layers, the Model Optimizer classifies them as custom.
