# List of ML File Formats

This repository lists file formats used in ML/AI systems. It can be used as a resource for tool development and vulnerability research. We aim to keep this list as up-to-date and accurate as possible. If you discover any missing file formats, inaccuracies, or if you have more details to contribute, please raise an [issue](https://github.com/trailofbits/ml-file-formats/issues) or submit a [pull request](https://github.com/trailofbits/ml-file-formats/pulls).


Generated sample artifacts are available in [`bin/`](bin). Some of them were produced by separate legacy generator scripts and legacy virtual environments, but the output artifacts are now consolidated under the same directory.

| Name | ML-specific | Framework/Organization (if applicable) | Identification Tooling | Extensions | Sample Status | Sample | Additional Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [PyTorch v1.3](https://github.com/pytorch/pytorch/issues/31877) | Yes | PyTorch | Fickling | .pt, .pth, .bin | Generated | [PyTorchV13.pt](bin/PyTorchV13.pt) | Description: ZIP file containing data.pkl (1 pickle file) |
| [PyTorch v0.1.1](https://github.com/pytorch/pytorch/issues/31877) | Yes | PyTorch | Fickling | .pt, .pth, .bin | Missing | - | Description: Tar file with sys_info, pickle, storages, and tensors |
| [PyTorch v0.1.10](https://github.com/pytorch/pytorch/issues/31877) | Yes | PyTorch | Fickling | .pt, .pth, .bin | Missing | - | Description: Stacked pickle files |
| [TorchScript v1.4](https://github.com/pytorch/pytorch/issues/31877) | Yes | PyTorch | Fickling | .pt, .pth, .bin | Generated | [TorchScriptV14.pt](bin/TorchScriptV14.pt) | Description: ZIP file with data.pkl, constants.pkl, and version (2 pickle files and a folder) |
| [TorchScript v1.3 (deprecated)](https://github.com/pytorch/pytorch/issues/31877) | Yes | PyTorch | Fickling | .pt, .pth, .bin | Generated | [TorchScriptV13Deprecated.pt](bin/TorchScriptV13Deprecated.pt) | Description: ZIP file with data.pkl and constants.pkl (2 pickle files) |
| [TorchScript v1.1 (deprecated)](https://github.com/pytorch/pytorch/issues/31877) | Yes | PyTorch | Fickling | .pt, .pth, .bin | Generated | [TorchScriptV11Deprecated.pt](bin/TorchScriptV11Deprecated.pt) | Description: ZIP file with model.json and attributes.pkl (a JSON file and a pickle file) |
| [TorchScript v1.0 (deprecated)](https://github.com/pytorch/pytorch/issues/31877) | Yes | PyTorch | Fickling | .pt, .pth, .bin | Generated | [TorchScriptV10Deprecated.pt](bin/TorchScriptV10Deprecated.pt) | Description: ZIP file with model.json |
| [PyTorch model archive format [ZIP]](https://github.com/pytorch/serve/tree/master/model-archiver#artifact-details) | Yes | PyTorch | Fickling | .mar | Generated | [PyTorchModelArchiveFormatZIP.mar](bin/PyTorchModelArchiveFormatZIP.mar) | Description: ZIP file that includes Python code files and pickle files |
| [PyTorch model archive format [TAR]](https://github.com/pytorch/serve/tree/master/model-archiver#artifact-details) | Yes | PyTorch | - | .mar | Generated | [PyTorchModelArchiveFormatTAR.mar](bin/PyTorchModelArchiveFormatTAR.mar) | Description: TAR file that includes Python code files and pickle files |
| [PyTorch Package](https://pytorch.org/docs/stable/package.html) | Yes | PyTorch | - | .pt, .pth, .bin | Generated | [PyTorchPackage.pt](bin/PyTorchPackage.pt) | Description: ZIP file that includes a pickled model, user files represented as a Python package, and framework files including serialized tensor data |
| [ExecuTorch](https://pytorch.org/executorch/main/pte-file-format.html) | Yes | PyTorch | - | .pte | Missing | - | Description: Modified binary flatbuffer file with optional data segments appended |
| [Torch.export](https://pytorch.org/docs/stable/export.html) | Yes | PyTorch | - | .pt2 | Generated | [TorchExport.pt2](bin/TorchExport.pt2) | Description: ZIP file with JSON files and Python code file |
| [PyTorch Mobile](https://pytorch.org/tutorials/recipes/mobile_perf.html?highlight=mobile) | Yes | PyTorch | - | .ptl | Generated | [PyTorchMobile.ptl](bin/PyTorchMobile.ptl) | Description: Modified binary flatbuffer file |
| [Safetensors](https://github.com/huggingface/safetensors) | Yes | - | PolyFile | .safetensors | Generated | [Safetensors.safetensors](bin/Safetensors.safetensors) | [Refer to our audit](https://github.com/trailofbits/publications/blob/master/reviews/2023-03-eleutherai-huggingface-safetensors-securityreview.pdf) |
| [ONNX](https://github.com/onnx/onnx) | Yes | - | - | .onnx | Generated | [ONNX.onnx](bin/ONNX.onnx) | [Refer to LobotoMI](https://github.com/alkaet/LobotoMl) |
| [Keras native file format](https://keras.io/guides/serialization_and_saving/#saving) | Yes | Keras | - | .keras | Generated | [KerasNativeFileFormat.keras](bin/KerasNativeFileFormat.keras) | Description: ZIP archive with 2 JSON files and 1 h5 file |
| [TensorFlow Saved Models](https://www.tensorflow.org/guide/saved_model) | Yes | TensorFlow | - | .pb | Generated | [TensorFlowSavedModels](bin/TensorFlowSavedModels) | [Description: Custom Protobuf format. Can result in arbitrary code execution.](https://hiddenlayer.com/research/models-are-code/) |
| [TensorFlow Checkpoint](https://www.tensorflow.org/guide/checkpoint) | Yes | TensorFlow | - | .ckpt | Generated | [TensorFlowCheckpoint](bin/TensorFlowCheckpoint) | [Description: Custom Protobuf format. Can result in arbitrary code execution.](https://hiddenlayer.com/research/models-are-code/) |
| [TFLite](https://www.tensorflow.org/lite/guide) | Yes | TensorFlow | - | .tflite | Generated | [TFLite.tflite](bin/TFLite.tflite) | Description: Modified binary flatbuffer file |
| [TFJS](https://www.tensorflow.org/js/guide/save_load) | Yes | TensorFlow | - | \- | Generated | [TFJS](bin/TFJS) | Description: JSON file and binary file with weights. Technically not a singular file format. |
| [TF1 Hub format (deprecated)](https://www.tensorflow.org/hub/tf1_hub_module#:~:text=The%20TF1%20Hub%20format%20is%20similar%20to%20the%20SavedModel%20format,different%20tagging%20conventions%20for%20metagraphs) | Yes | TensorFlow | - | \- | Generated | [TF1HubFormatDeprecated](bin/TF1HubFormatDeprecated) | Description: Custom Protobuf format. |
| [Tensorizer](https://github.com/coreweave/tensorizer) | Yes | CoreWeave | - | \- | Generated | [Tensorizer](bin/Tensorizer) | Not uncommon especially in private production systems |
| [TFRecords](https://www.tensorflow.org/tutorials/load_data/tfrecord) | Yes | TensorFlow | - | .tfrecords | Generated | [TFRecords.tfrecords](bin/TFRecords.tfrecords) | Description: Wrapper around a Protocol Buffer |
| [NPY](https://numpy.org/devdocs/reference/generated/numpy.lib.format.html) | Yes | NumPy | - | .npy | Generated | [NPY.npy](bin/NPY.npy) | Used to integrate pickle by default as well. |
| [NPZ](https://docs.scipy.org/doc/numpy-1.9.3/reference/generated/numpy.savez.html#:~:text=compressed%20.npz%20archive-,The%20.,npy%20format.) | Yes | NumPy | - | .npz | Generated | [NPZ.npz](bin/NPZ.npz) | Description: ZIP file of NPY files |
| [GGUF](https://github.com/ggerganov/ggml/blob/master/docs/gguf.md) | Yes | llama.cpp/GGML | - | .gguf | Generated | [GGUF.gguf](bin/GGUF.gguf) | \- |
| [GGML](https://github.com/rustformers/llm/blob/main/crates/ggml/README.md) | Yes | llama.cpp/GGML | - | .ggml | Missing | - | \- |
| [GGMF (deprecated)](https://github.com/ggerganov/ggml/blob/master/docs/gguf.md#historical-state-of-affairs) | Yes | llama.cpp/GGML | - | .ggmf | Missing | - | \- |
| [GGJT (deprecated)](https://github.com/ggerganov/ggml/blob/master/docs/gguf.md#historical-state-of-affairs) | Yes | llama.cpp/GGML | - | .ggjt | Missing | - | \- |
| [NetCDF](https://www.unidata.ucar.edu/software/netcdf/) | Yes | - | - | .nc | Generated | [NetCDF.nc](bin/NetCDF.nc) | \- |
| [PMML](https://en.wikipedia.org/wiki/Predictive_Model_Markup_Language) | Yes | - | - | \- | Generated | [PMML](bin/PMML) | \- |
| [MLeap](https://github.com/combust/mleap) | Yes | Spark | - | .mleap | Missing | - | \- |
| [CoreML](https://apple.github.io/coremltools/mlmodel/index.html) | Yes | Apple | - | .coreml | Missing | - | \- |
| MLFlow Format | Yes | MLFlow | - | \- | Generated | [MLFlowFormat](bin/MLFlowFormat) | \- |
| MLFlow TensorSpec input format | Yes | MLFlow | - | \- | Generated | [MLFlowTensorSpecInputFormat.json](bin/MLFlowTensorSpecInputFormat.json) | \- |
| [SurrealML](https://github.com/surrealdb/surrealml) | Yes | SurrealDB | - | .surml | Missing | - | \- |
| [Llamafile](https://github.com/Mozilla-Ocho/llamafile?tab=readme-ov-file) | Yes | - | - | .llamafile | Missing | - | \- |
| [.prompt](https://docs.humanloop.com/docs/prompt-file-format) | Yes | HumanLoop | - | .prompt | Missing | - | \- |
| [Pickle](https://docs.python.org/3/library/pickle.html) | No | Python | PolyFile | .pkl | Generated | [Pickle.pkl](bin/Pickle.pkl) | [Refer to Fickling](https://github.com/trailofbits/fickling) |
| Joblib | No | - | PolyFile | \- | Generated | [Joblib](bin/Joblib) | \- |
| Nemo | Yes | NVIDIA | - | \- | Missing | - | \- |
| Riva | Yes | NVIDIA | - | \- | Missing | - | \- |
| AVRO | No | - | - | \- | Generated | [AVRO](bin/AVRO) | \- |
| PARQUET | No | - | - | \- | Generated | [PARQUET](bin/PARQUET) | \- |
| ORC | No | - | - | \- | Generated | [ORC](bin/ORC) | \- |
| JSON | No | - | PolyFile | \- | Generated | [JSON](bin/JSON) | \- |
| CSV | No | - | - | \- | Generated | [CSV](bin/CSV) | \- |
| Protocol Buffers | No | - | - | \- | Generated | [ProtocolBuffers](bin/ProtocolBuffers) | Usually an underlying file format |
| HDF5 | No | - | - | .h5 | Generated | [HDF5.h5](bin/HDF5.h5) | \- |
| [Caffe](https://caffe.berkeleyvision.org/tutorial/net_layer_blob.html) | Yes | Caffe | - | .caffemodel & .prototxt | Missing | - | Description: Protobuf-based file format |
| [ArmNN Flatbuffers](https://arm-software.github.io/armnn/20.02/serializers.xhtml#S8_serializer) | Yes | ArmNN | - | \- | Missing | - | \- |
| [Cambricon](https://github.com/Cambricon/CNStream) | Yes | - | - | \- | Missing | - | \- |
| [Circle](https://nnfw.readthedocs.io/_/downloads/en/latest/pdf/) | Yes | - | - | \- | Missing | - | \- |
| ZIP | No | - | PolyFile | \- | Generated | [ZIP](bin/ZIP) | Usually an underlying file format |
| [CNTK v1 (deprecated)](https://learn.microsoft.com/en-us/cognitive-toolkit/cntk-library-api) | Yes | Microsoft Cognitive Toolkit | - | \- | Missing | - | \- |
| [CNTK v2](https://learn.microsoft.com/en-us/cognitive-toolkit/cntk-library-api) | Yes | Microsoft Cognitive Toolkit | - | \- | Missing | - | Description: Protobuf-based file format |
| [Darknet](https://github.com/hank-ai/darknet) | Yes | [Hank.ai](http://hank.ai/) Darknet | - | \- | Missing | - | \- |
| [DL4J](https://deeplearning4j.konduit.ai/v/en-1.0.0-beta7/getting-started/cheat-sheet) | Yes | DL4J | - | \- | Missing | - | Description: ZIP-based file format |
| [Deep Learning Container (DLC)](https://developer.qualcomm.com/software/qualcomm-neural-processing-sdk/learning-resources/developing-apps-with-neural-processing-sdk/working-with-machine-learning) | Yes | Qualcomm Neural Processing SDK | - | .dlc | Missing | - | \- |


## TODO

The following file formats still need to be done. 

- [ ] Python File Format Parser
- [ ] Yara rules 
- [ ] PyTorch v0.1.1
- [ ] PyTorch v0.1.10
- [ ] ExecuTorch
- [ ] GGML
- [ ] GGMF (deprecated)
- [ ] GGJT (deprecated)
- [ ] MLeap
- [ ] CoreML
- [ ] SurrealML
- [ ] Llamafile
- [ ] .prompt
- [ ] Nemo
- [ ] Riva
- [ ] Caffe
- [ ] ArmNN Flatbuffers
- [ ] Cambricon
- [ ] Circle
- [ ] CNTK v1 (deprecated)
- [ ] CNTK v2
- [ ] Darknet
- [ ] DL4J
- [ ] Deep Learning Container (DLC)


## Disclaimer
Vibecoded the code to create the ML file formats. 

## Status 
In progress. Will submit a pull request once all files have been generated. 