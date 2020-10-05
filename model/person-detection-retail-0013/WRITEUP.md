# Write-Up

The following address an explanation of the process behind converting any custom layers, as well as explaining the potential reasons for handling custom layers in a trained model.

## Explaining Custom Layers in OpenVINO™

According to [Custom Layers Guide](https://docs.openvinotoolkit.org/latest/openvino_docs_HOWTO_Custom_Layers_Guide.html), we learn that custom layers are layers that are not included in the list of known layers. If your topology contains any layers that are not in the list of known layers, the Model Optimizer classifies them as custom.

Before building the model's internal representation, the Model Optimizer will search the list of known layers for each layer contained in the input model topology, optimizing the model, and then producing the Intermediate Representation files.

The Inference Engine loads the layers from the input model IR files into the specified device plugin, which will search a list of known layer implementations for the device.

On the other hand, because Inference Engine use different data layouts of tensors compared to TensorFlow, so we'll have to do data preprocessing in advance. Then, these tensors are flattened out to required data format for inference. The results Intermediate Representation including .xml and .bin files, which detailing our topology and weights.

## Compare Model Performance

## Assess Model Use Cases

The use cases of a people counter app are quite extensive, such as:
- shopping malls
- metro station, retail chain, public venue, bank,
- 

Some of the potential use cases of the people counter app are, at the retail to keep a track of the people based on their interest, and at the traffic signal to make sure that people crosses safely.

Each of these use cases would be useful because, it allows us to improve marketing strategy of the retail and as well as safety of the pedestrian.
