# Remaining File Formats Guide

This document describes the file formats from [README.md](/Users/alexa/Documents/repo/ml-file-formats/README.md) that still do not have generated sample artifacts in this repository, along with practical guidance for how to create them.

The goal here is not just to say "unsupported", but to capture:

- what the format is likely made from
- what toolchain is needed to create it
- what a realistic generation workflow looks like
- what is currently blocking generation in this repository

## Status Summary

The remaining formats are:

- `PyTorch v0.1.1`
- `PyTorch v0.1.10`
- `ExecuTorch`
- `GGML`
- `GGMF (deprecated)`
- `GGJT (deprecated)`
- `MLeap`
- `CoreML`
- `SurrealML`
- `Llamafile`
- `.prompt`
- `Nemo`
- `Riva`
- `Caffe`
- `ArmNN Flatbuffers`
- `Cambricon`
- `Circle`
- `CNTK v1 (deprecated)`
- `CNTK v2`
- `Darknet`
- `DL4J`
- `Deep Learning Container (DLC)`

## PyTorch v0.1.1

### What it is

The README describes this as a tar-based legacy PyTorch serialization layout containing entries such as `sys_info`, pickle payloads, storages, and tensors.

### How to create it

The most reliable path is:

1. Build or obtain a historically accurate PyTorch runtime from the `0.1.x` era.
2. Create a trivial model or tensor payload inside that runtime.
3. Save it using the original serialization path used at that time.
4. Verify the resulting file is a tar archive and contains the expected members.

### Tooling likely required

- A very old PyTorch build from the `0.1.x` timeframe
- Likely an old Python interpreter and old OS environment
- Potentially Linux rather than Windows

### Why it is still blocked here

Archived wheels available on this machine only got us back to `torch==0.4.1`, which does not emit the `v0.1.1` tar-based layout. Reaching this format likely requires:

- archived binaries outside the normal wheel index
- source builds from a historical commit
- a dedicated old environment or container

## PyTorch v0.1.10

### What it is

The README describes this as a stacked-pickle legacy PyTorch serialization format.

### How to create it

The likely workflow is:

1. Set up a historically accurate `0.1.x` PyTorch runtime.
2. Create a minimal tensor or model object.
3. Serialize it through the original save path.
4. Confirm the file structure is stacked pickle payloads rather than a tar or zip archive.

### Tooling likely required

- A specific `0.1.10`-era PyTorch runtime
- Old Python and dependency stack
- Possibly source build or archived binary recovery

### Why it is still blocked here

The available archived Windows wheels do not reach this old serializer implementation. This one likely requires:

- a reconstructed historical environment
- manual format recreation from source if old binaries are not recoverable

## ExecuTorch

### What it is

ExecuTorch exports `.pte` files. In practice, this is a flatbuffer-based program format with optional data sections.

### How to create it

The modern workflow is:

1. Install the `executorch` Python package.
2. Export a model with `torch.export`.
3. Lower it through `executorch.exir`.
4. Serialize the final Executorch program to `.pte`.

### Tooling likely required

- `executorch`
- `torch`
- The `flatc` compiler from FlatBuffers

### Why it is still blocked here

The Python package installs successfully, but actual `.pte` generation fails because Executorch shells out to `flatc`. To finish this one, install `flatc` and ensure it is on `PATH`.

## GGML

### What it is

GGML is an older llama.cpp/GGML tensor container format predating GGUF.

### How to create it

The realistic paths are:

1. Use an old llama.cpp conversion script from the period when GGML was still emitted.
2. Convert a tiny model checkpoint into `.ggml`.
3. Validate the resulting header and tensor blocks against the historical spec.

### Tooling likely required

- Historical llama.cpp conversion scripts
- A tiny source checkpoint to convert
- Possibly Python tooling from older repositories

### Why it is still blocked here

Current Python packages expose `GGUF` writing but not a maintained `GGML` writer. This format likely needs:

- old conversion scripts from llama.cpp or rustformers
- manual binary writer implementation from a historical spec

## GGMF (deprecated)

### What it is

GGMF is one of the deprecated historical GGML-family formats.

### How to create it

The only realistic approaches are:

1. Recover an older converter that still emits GGMF.
2. Reimplement the file format from historical docs and examples.

### Tooling likely required

- Historical llama.cpp or GGML tooling
- Archived documentation or example files

### Why it is still blocked here

No current writer library in the environment produces GGMF. This will likely require manual reconstruction from historical source code.

## GGJT (deprecated)

### What it is

GGJT is another deprecated historical GGML-family format.

### How to create it

The likely path is similar to GGMF:

1. Identify an old converter revision that still writes GGJT.
2. Generate or convert a tiny model.
3. Verify the output against historical examples.

### Tooling likely required

- Historical llama.cpp tooling
- Old model conversion scripts

### Why it is still blocked here

No current maintained library in the environment writes GGJT directly.

## MLeap

### What it is

MLeap is a Spark-oriented model serialization bundle, commonly packaged as a `.mleap` archive.

### How to create it

Typical workflow:

1. Train or define a simple Spark/Scala pipeline.
2. Bundle it using the MLeap runtime.
3. Export the bundle to `.mleap`.

### Tooling likely required

- Java/Scala toolchain
- Spark
- MLeap libraries

### Why it is still blocked here

This is not a pure Python format. It needs a JVM-based stack and the MLeap packaging process.

## CoreML

### What it is

CoreML packages Apple model artifacts, often as `.mlmodel` or related packaged forms. The README row uses `.coreml`.

### How to create it

Typical workflow:

1. Create a small model in PyTorch, TensorFlow, or scikit-learn.
2. Convert it using `coremltools`.
3. Save the converted model artifact.

### Tooling likely required

- `coremltools`
- A compatible Python version for available `coremltools` releases
- Sometimes macOS-specific validation tooling

### Why it is still blocked here

The available `coremltools` releases did not install cleanly under the Python versions currently in use here. To finish this one, the cleanest path is a separate venv with a Python version known to work with the desired `coremltools` release, potentially on macOS.

## SurrealML

### What it is

SurrealML appears to be a SurrealDB-specific ML artifact format with `.surml`.

### How to create it

Likely workflow:

1. Install the SurrealML package and any compatible dependencies.
2. Build a tiny supported model payload.
3. Export through the SurrealML writer or CLI.

### Tooling likely required

- `surrealml`
- Its exact dependency stack

### Why it is still blocked here

The currently available `surrealml` wheels conflict with the NumPy requirements used by the rest of the repo's working venv. This is probably solvable with a dedicated isolated venv pinned to the package's expected stack.

## Llamafile

### What it is

Llamafile packages a model into a self-contained executable-style format.

### How to create it

Typical workflow:

1. Start from a GGUF model.
2. Use the llamafile packaging tool to wrap the runtime and model together.
3. Produce the `.llamafile` output.

### Tooling likely required

- Llamafile build/package tooling
- A source GGUF model

### Why it is still blocked here

This is not just a Python serialization format. It requires the external llamafile packaging toolchain.

## .prompt

### What it is

The README links to HumanLoop's prompt file format and uses the `.prompt` extension.

### How to create it

This likely requires:

1. Reading the exact schema expected by the format.
2. Constructing a minimal valid prompt artifact with the required metadata fields.
3. Saving it as `.prompt`.

### Tooling likely required

- The documented file schema
- Possibly only JSON/YAML authoring, depending on the spec

### Why it is still blocked here

This one is likely achievable, but the exact schema has not yet been implemented in our generator. It is more of a specification-work item than a tooling blocker.

## Nemo

### What it is

NVIDIA NeMo artifacts are usually model packages built through the NeMo framework.

### How to create it

Typical workflow:

1. Install NeMo and its dependencies.
2. Create or load a tiny NeMo model.
3. Save/export through the NeMo API.

### Tooling likely required

- NVIDIA NeMo
- Potentially PyTorch Lightning and other heavy dependencies

### Why it is still blocked here

The NeMo stack has not been installed or pinned in a dedicated environment yet, and it is a heavy ecosystem with a high risk of dependency churn.

## Riva

### What it is

Riva is NVIDIA's speech/AI serving stack, with its own packaging/export conventions.

### How to create it

Likely workflow:

1. Use NVIDIA Riva tooling or model repositories.
2. Export or package a supported model through the Riva pipeline.

### Tooling likely required

- NVIDIA Riva tooling
- Likely containerized or SDK-driven workflow

### Why it is still blocked here

Riva is not a simple Python file serializer; it typically requires NVIDIA-specific tooling and packaging flows.

## Caffe

### What it is

Caffe commonly involves `.caffemodel` plus `.prototxt`, with protobuf-based model definitions and weights.

### How to create it

Typical workflow:

1. Define a tiny network in `.prototxt`.
2. Instantiate or train it with Caffe.
3. Save the corresponding `.caffemodel`.

### Tooling likely required

- Caffe
- `caffe.proto`
- Protobuf compiler or Caffe runtime

### Why it is still blocked here

This requires Caffe-specific protobuf definitions and a compatible runtime, neither of which are installed here.

## ArmNN Flatbuffers

### What it is

This is a flatbuffer-based ArmNN serialization format.

### How to create it

The likely workflow is:

1. Obtain the ArmNN flatbuffer schema.
2. Use ArmNN serialization tooling or generate Python bindings from the schema.
3. Populate a minimal model object and serialize it.

### Tooling likely required

- ArmNN schema files
- `flatc`
- Possibly ArmNN SDK components

### Why it is still blocked here

We do not currently have the schema, generated bindings, or ArmNN-specific tooling.

## Cambricon

### What it is

Cambricon model formats are vendor-specific and tied to Cambricon tooling.

### How to create it

Likely workflow:

1. Obtain the vendor SDK or conversion tool.
2. Convert a tiny supported model.
3. Export the resulting artifact.

### Tooling likely required

- Cambricon SDK
- Vendor documentation

### Why it is still blocked here

No Cambricon schema or SDK is installed.

## Circle

### What it is

Circle is a Samsung/ONE-family flatbuffer-based format.

### How to create it

Likely workflow:

1. Obtain the Circle flatbuffer schema or conversion tool.
2. Convert a tiny model into Circle.
3. Validate the binary structure.

### Tooling likely required

- Circle schema or ONE conversion tooling
- `flatc`

### Why it is still blocked here

We do not currently have the schema or the official conversion pipeline.

## CNTK v1 (deprecated)

### What it is

CNTK v1 is a deprecated Microsoft Cognitive Toolkit format.

### How to create it

Likely workflow:

1. Install an old CNTK build that still supports v1 serialization.
2. Create a tiny model.
3. Save it in the v1 format.

### Tooling likely required

- Historical CNTK runtime
- A compatible old Python and system environment

### Why it is still blocked here

CNTK is not installed, and the deprecated version would likely require a dedicated historical environment.

## CNTK v2

### What it is

CNTK v2 is a newer protobuf-based CNTK model format.

### How to create it

Typical workflow:

1. Install CNTK v2.
2. Build a tiny model.
3. Save/export it through CNTK.

### Tooling likely required

- CNTK runtime

### Why it is still blocked here

CNTK is not installed and would need a dedicated environment.

## Darknet

### What it is

Darknet typically uses `.cfg` plus weight files, or related Darknet packaging conventions.

### How to create it

Typical workflow:

1. Create a tiny Darknet config.
2. Initialize a tiny network.
3. Save the weights file.

### Tooling likely required

- Darknet runtime or conversion tooling

### Why it is still blocked here

No Darknet toolchain is installed, and the format usually depends on Darknet-specific configs and writers.

## DL4J

### What it is

DL4J uses Java-oriented model packaging, often zip-based.

### How to create it

Typical workflow:

1. Use Deeplearning4j to create a tiny model.
2. Save it through the DL4J serializer.
3. Package the resulting artifact.

### Tooling likely required

- Java
- DL4J libraries

### Why it is still blocked here

This is a JVM ecosystem format and is not directly handled by the current Python-focused setup.

## Deep Learning Container (DLC)

### What it is

The Qualcomm Neural Processing SDK emits `.dlc` files.

### How to create it

Typical workflow:

1. Create or obtain a supported source model.
2. Use Qualcomm conversion tooling to compile/export to `.dlc`.
3. Validate with the SDK's inspection tools.

### Tooling likely required

- Qualcomm Neural Processing SDK
- Vendor converters

### Why it is still blocked here

The Qualcomm SDK is not installed, and `.dlc` generation is vendor-tool-driven rather than a generic Python serialization step.

## Practical Next Steps

If the goal is to finish the remaining formats, the most practical order is:

1. `.prompt`
Reason: likely only needs schema implementation, not a heavy toolchain.

2. `SurrealML`
Reason: likely solvable with a dedicated isolated venv that does not share the current NumPy stack.

3. `ExecuTorch`
Reason: we are one external binary (`flatc`) away from likely success.

4. `CoreML`
Reason: likely solvable with a Python-version-specific venv, or more easily on macOS.

5. `GGML` / `GGMF` / `GGJT`
Reason: likely needs historical format reconstruction or old conversion scripts.

6. JVM/vendor formats (`MLeap`, `DL4J`, `Caffe`, `CNTK`, `DLC`, `Riva`, `Cambricon`, `Circle`, `ArmNN`)
Reason: these will need external SDKs, schemas, or non-Python toolchains.

7. `PyTorch v0.1.1` and `PyTorch v0.1.10`
Reason: these are the hardest because they require very old serializer behavior not reachable from the archived Windows wheels we were able to use.
