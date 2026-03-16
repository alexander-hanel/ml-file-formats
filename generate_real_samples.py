#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import json
import os
import pickle
import shutil
import tarfile
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import avro.schema
import h5py
import joblib
import mlflow.sklearn
import netCDF4
import numpy as np
import onnx
import pyarrow as pa
import pyarrow.orc as pa_orc
import pyarrow.parquet as pa_parquet
import sklearn.linear_model
import torch
from avro.datafile import DataFileWriter
from avro.io import DatumWriter
from google.protobuf import descriptor_pb2
from gguf import GGUFWriter
from mlflow.models.signature import infer_signature
from mlflow.types.schema import Schema, TensorSpec
from safetensors.numpy import save_file as save_safetensors_file
from torch import nn
from torch.package import PackageExporter
from torch.utils.mobile_optimizer import optimize_for_mobile

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".mplconfig"))
import tensorflow as tf  # noqa: E402


@dataclass(frozen=True)
class FormatSpec:
    readme_name: str
    output_name: str | None
    generator: Callable[[Path], None] | None
    notes: str = ""


@dataclass
class Result:
    readme_name: str
    status: str
    relative_path: str
    notes: str


class TinyTorchModel(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.linear1 = nn.Linear(4, 3)
        self.relu = nn.ReLU()
        self.linear2 = nn.Linear(3, 2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.linear2(self.relu(self.linear1(x)))


def build_torch_model() -> TinyTorchModel:
    torch.manual_seed(7)
    model = TinyTorchModel()
    model.eval()
    return model


def build_numpy_arrays() -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed=7)
    return {
        "weights": rng.normal(size=(3, 4)).astype(np.float32),
        "bias": rng.normal(size=(3,)).astype(np.float32),
    }


def build_tf_model() -> tf.keras.Model:
    tf.random.set_seed(7)
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(4,)),
            tf.keras.layers.Dense(3, activation="relu"),
            tf.keras.layers.Dense(2),
        ]
    )
    model(np.zeros((1, 4), dtype=np.float32))
    return model


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def save_json(path: Path, payload: object) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2)


def generate_pytorch_v13(path: Path) -> None:
    model = build_torch_model()
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "metadata": {"format": "PyTorch v1.3 style state_dict archive"},
        },
        path,
    )


def generate_torchscript_v14(path: Path) -> None:
    model = build_torch_model()
    example = torch.randn(1, 4)
    scripted = torch.jit.trace(model, example)
    scripted.save(path.as_posix())


def generate_pytorch_model_archive(path: Path, mode: str) -> None:
    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        mar_inf = temp_dir / "MAR-INF"
        mar_inf.mkdir()

        model_path = temp_dir / "model.pth"
        generate_pytorch_v13(model_path)

        handler_path = temp_dir / "handler.py"
        handler_path.write_text(
            "def handle(data, context):\n"
            "    return {'received': len(data) if data else 0}\n",
            encoding="utf-8",
        )

        manifest = {
            "createdOn": "2026-03-15T00:00:00Z",
            "runtime": "python",
            "model": {
                "modelName": "tiny-model",
                "serializedFile": "model.pth",
                "handler": "handler.py",
                "version": "1.0",
            },
        }
        save_json(mar_inf / "MANIFEST.json", manifest)

        ensure_parent(path)
        if mode == "zip":
            with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for file_path in temp_dir.rglob("*"):
                    if file_path.is_file():
                        archive.write(file_path, file_path.relative_to(temp_dir))
            return

        with tarfile.open(path, "w") as archive:
            for file_path in temp_dir.rglob("*"):
                archive.add(file_path, arcname=file_path.relative_to(temp_dir))


def generate_pytorch_package(path: Path) -> None:
    model = build_torch_model()
    ensure_parent(path)
    with PackageExporter(path.as_posix()) as exporter:
        exporter.intern("**")
        exporter.save_pickle("artifacts", "model.pkl", model.state_dict())
        exporter.save_text("artifacts", "README.txt", "Tiny torch.package sample")


def generate_torch_export(path: Path) -> None:
    model = build_torch_model()
    example = (torch.randn(1, 4),)
    exported = torch.export.export(model, example)
    torch.export.save(exported, path.as_posix())


def generate_pytorch_mobile(path: Path) -> None:
    model = build_torch_model()
    scripted = torch.jit.script(model)
    optimized = optimize_for_mobile(scripted)
    optimized._save_for_lite_interpreter(path.as_posix())


def generate_safetensors(path: Path) -> None:
    arrays = build_numpy_arrays()
    ensure_parent(path)
    save_safetensors_file(arrays, path.as_posix())


def generate_onnx(path: Path) -> None:
    input_tensor = onnx.helper.make_tensor_value_info("input", onnx.TensorProto.FLOAT, [1, 4])
    output_tensor = onnx.helper.make_tensor_value_info("output", onnx.TensorProto.FLOAT, [1, 2])

    weight = onnx.helper.make_tensor(
        name="weight",
        data_type=onnx.TensorProto.FLOAT,
        dims=[4, 2],
        vals=np.arange(8, dtype=np.float32),
    )
    bias = onnx.helper.make_tensor(
        name="bias",
        data_type=onnx.TensorProto.FLOAT,
        dims=[2],
        vals=np.array([0.1, -0.1], dtype=np.float32),
    )

    node = onnx.helper.make_node("Gemm", ["input", "weight", "bias"], ["output"])
    graph = onnx.helper.make_graph([node], "tiny-onnx-model", [input_tensor], [output_tensor], [weight, bias])
    model = onnx.helper.make_model(graph, producer_name="ml-file-formats")
    ensure_parent(path)
    onnx.save(model, path.as_posix())


def generate_keras_native(path: Path) -> None:
    model = build_tf_model()
    ensure_parent(path)
    model.save(path.as_posix())


def generate_tensorflow_saved_model(path: Path) -> None:
    model = build_tf_model()
    path.mkdir(parents=True, exist_ok=True)
    tf.saved_model.save(model, path.as_posix())


def generate_tensorflow_checkpoint(path: Path) -> None:
    model = build_tf_model()
    path.mkdir(parents=True, exist_ok=True)
    checkpoint = tf.train.Checkpoint(model=model)
    checkpoint.write((path / "ckpt").as_posix())


def generate_tflite(path: Path) -> None:
    model = build_tf_model()
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()
    ensure_parent(path)
    path.write_bytes(tflite_model)


def generate_tfjs(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    model_json = {
        "format": "layers-model",
        "generatedBy": "ml-file-formats",
        "convertedBy": "manual-generator",
        "modelTopology": {
            "keras_version": "3.x",
            "backend": "tensorflow",
            "model_config": {
                "class_name": "Sequential",
                "config": {
                    "name": "tiny_tfjs_model",
                    "layers": [
                        {
                            "class_name": "InputLayer",
                            "config": {
                                "batch_input_shape": [None, 4],
                                "dtype": "float32",
                                "name": "input_1",
                                "sparse": False,
                                "ragged": False,
                            },
                        },
                        {
                            "class_name": "Dense",
                            "config": {
                                "name": "dense",
                                "trainable": True,
                                "dtype": "float32",
                                "units": 2,
                                "activation": "linear",
                                "use_bias": True,
                            },
                        },
                    ],
                },
            },
        },
    }
    weights = np.arange(10, dtype=np.float32)
    model_json["weightsManifest"] = [
        {
            "paths": ["group1-shard1of1.bin"],
            "weights": [
                {
                    "name": "dense/kernel",
                    "shape": [4, 2],
                    "dtype": "float32",
                },
                {
                    "name": "dense/bias",
                    "shape": [2],
                    "dtype": "float32",
                },
            ],
        }
    ]
    save_json(path / "model.json", model_json)
    (path / "group1-shard1of1.bin").write_bytes(weights.tobytes())


def generate_tensorizer(path: Path) -> None:
    model = build_torch_model()
    ensure_parent(path)
    from tensorizer.serialization import TensorSerializer

    serializer = TensorSerializer(path)
    serializer.write_state_dict(model.state_dict())
    serializer.close()


def generate_tfrecords(path: Path) -> None:
    example = tf.train.Example(
        features=tf.train.Features(
            feature={
                "id": tf.train.Feature(int64_list=tf.train.Int64List(value=[1])),
                "values": tf.train.Feature(float_list=tf.train.FloatList(value=[0.25, 0.5, 0.75])),
                "label": tf.train.Feature(bytes_list=tf.train.BytesList(value=[b"tiny-record"])),
            }
        )
    )
    ensure_parent(path)
    with tf.io.TFRecordWriter(path.as_posix()) as writer:
        writer.write(example.SerializeToString())


def generate_npy(path: Path) -> None:
    ensure_parent(path)
    np.save(path, np.arange(12, dtype=np.float32).reshape(3, 4))


def generate_npz(path: Path) -> None:
    ensure_parent(path)
    np.savez(path, array=np.arange(8, dtype=np.int32), matrix=np.eye(3, dtype=np.float32))


def generate_netcdf(path: Path) -> None:
    ensure_parent(path)
    with netCDF4.Dataset(path.as_posix(), "w", format="NETCDF4") as dataset:
        dataset.createDimension("feature", 3)
        values = dataset.createVariable("values", "f4", ("feature",))
        values[:] = np.array([0.1, 0.2, 0.3], dtype=np.float32)


def generate_pmml(path: Path) -> None:
    ensure_parent(path)
    path.write_text(
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "<PMML version=\"4.4\" xmlns=\"http://www.dmg.org/PMML-4_4\">\n"
        "  <Header>\n"
        "    <Application name=\"ml-file-formats\" version=\"1.0\"/>\n"
        "  </Header>\n"
        "  <DataDictionary numberOfFields=\"1\">\n"
        "    <DataField name=\"x\" optype=\"continuous\" dataType=\"double\"/>\n"
        "  </DataDictionary>\n"
        "</PMML>\n",
        encoding="utf-8",
    )


def generate_pickle(path: Path) -> None:
    ensure_parent(path)
    with path.open("wb") as handle:
        pickle.dump({"weights": [1, 2, 3], "label": "tiny-pickle"}, handle, protocol=4)


def generate_joblib(path: Path) -> None:
    ensure_parent(path)
    joblib.dump({"weights": np.arange(4), "label": "tiny-joblib"}, path.as_posix())


def generate_avro(path: Path) -> None:
    ensure_parent(path)
    schema = avro.schema.parse(
        json.dumps(
            {
                "type": "record",
                "name": "TinyRecord",
                "fields": [
                    {"name": "id", "type": "int"},
                    {"name": "label", "type": "string"},
                ],
            }
        )
    )
    with path.open("wb") as handle:
        writer = DataFileWriter(handle, DatumWriter(), schema)
        writer.append({"id": 1, "label": "tiny-avro"})
        writer.close()


def arrow_table() -> pa.Table:
    return pa.table(
        {
            "id": pa.array([1, 2, 3], type=pa.int32()),
            "score": pa.array([0.1, 0.5, 0.9], type=pa.float32()),
        }
    )


def generate_parquet(path: Path) -> None:
    ensure_parent(path)
    pa_parquet.write_table(arrow_table(), path.as_posix())


def generate_orc(path: Path) -> None:
    ensure_parent(path)
    with path.open("wb") as handle:
        pa_orc.write_table(arrow_table(), handle)


def generate_json(path: Path) -> None:
    save_json(path, {"id": 1, "name": "tiny-json", "values": [1, 2, 3]})


def generate_csv(path: Path) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["id", "score"])
        writer.writerow([1, 0.25])
        writer.writerow([2, 0.75])


def generate_protobuf(path: Path) -> None:
    ensure_parent(path)
    file_set = descriptor_pb2.FileDescriptorSet()
    file_proto = file_set.file.add()
    file_proto.name = "tiny.proto"
    file_proto.package = "sample"
    message = file_proto.message_type.add()
    message.name = "TinyMessage"
    field = message.field.add()
    field.name = "id"
    field.number = 1
    field.label = descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
    field.type = descriptor_pb2.FieldDescriptorProto.TYPE_INT32
    path.write_bytes(file_set.SerializeToString())


def generate_hdf5(path: Path) -> None:
    ensure_parent(path)
    with h5py.File(path, "w") as handle:
        handle.create_dataset("weights", data=np.arange(6, dtype=np.float32).reshape(2, 3))


def generate_zip(path: Path) -> None:
    ensure_parent(path)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("metadata.json", json.dumps({"format": "zip", "ok": True}))


def generate_mlflow_format(path: Path) -> None:
    features = np.array(
        [
            [0.0, 0.0],
            [0.0, 1.0],
            [1.0, 0.0],
            [1.0, 1.0],
        ],
        dtype=np.float32,
    )
    labels = np.array([0, 0, 1, 1], dtype=np.int64)
    model = sklearn.linear_model.LogisticRegression(random_state=7)
    model.fit(features, labels)
    signature = infer_signature(features, model.predict(features))
    path.mkdir(parents=True, exist_ok=True)
    mlflow.sklearn.save_model(
        sk_model=model,
        path=path.as_posix(),
        signature=signature,
        input_example=features[:2],
    )


def generate_mlflow_tensorspec(path: Path) -> None:
    ensure_parent(path)
    schema = Schema(
        [
            TensorSpec(np.dtype(np.float32), (-1, 4), name="input_tensor"),
        ]
    )
    path.write_text(schema.to_json(), encoding="utf-8")


def generate_gguf(path: Path) -> None:
    ensure_parent(path)
    writer = GGUFWriter(path, arch="llama")
    writer.add_name("tiny-gguf-model")
    writer.add_description("Minimal GGUF sample generated for format testing")
    writer.add_context_length(16)
    writer.add_embedding_length(4)
    writer.add_block_count(1)
    writer.add_feed_forward_length(8)
    writer.add_head_count(1)
    writer.add_tensor("token_embd.weight", np.arange(16, dtype=np.float32).reshape(4, 4))
    writer.write_header_to_file()
    writer.write_kv_data_to_file()
    writer.write_tensors_to_file()


def build_specs() -> list[FormatSpec]:
    return [
        FormatSpec("PyTorch v1.3", "PyTorchV13.pt", generate_pytorch_v13),
        FormatSpec("PyTorch v0.1.1", None, None, "Historical serializer not available in modern torch."),
        FormatSpec("PyTorch v0.1.10", None, None, "Historical serializer not available in modern torch."),
        FormatSpec("TorchScript v1.4", "TorchScriptV14.pt", generate_torchscript_v14),
        FormatSpec("TorchScript v1.3 (deprecated)", None, None, "Deprecated TorchScript layout is version-specific."),
        FormatSpec("TorchScript v1.1 (deprecated)", None, None, "Deprecated TorchScript layout is version-specific."),
        FormatSpec("TorchScript v1.0 (deprecated)", None, None, "Deprecated TorchScript layout is version-specific."),
        FormatSpec("PyTorch model archive format [ZIP]", "PyTorchModelArchiveFormatZIP.mar", lambda path: generate_pytorch_model_archive(path, "zip")),
        FormatSpec("PyTorch model archive format [TAR]", "PyTorchModelArchiveFormatTAR.mar", lambda path: generate_pytorch_model_archive(path, "tar")),
        FormatSpec("PyTorch Package", "PyTorchPackage.pt", generate_pytorch_package),
        FormatSpec("ExecuTorch", None, None, "ExecuTorch export additionally requires the flatc compiler, which is not available in this environment."),
        FormatSpec("Torch.export", "TorchExport.pt2", generate_torch_export),
        FormatSpec("PyTorch Mobile", "PyTorchMobile.ptl", generate_pytorch_mobile),
        FormatSpec("Safetensors", "Safetensors.safetensors", generate_safetensors),
        FormatSpec("ONNX", "ONNX.onnx", generate_onnx),
        FormatSpec("Keras native file format", "KerasNativeFileFormat.keras", generate_keras_native),
        FormatSpec("TensorFlow Saved Models", "TensorFlowSavedModels", generate_tensorflow_saved_model, "Directory containing saved_model.pb and variables."),
        FormatSpec("TensorFlow Checkpoint", "TensorFlowCheckpoint", generate_tensorflow_checkpoint, "Directory containing checkpoint shards."),
        FormatSpec("TFLite", "TFLite.tflite", generate_tflite),
        FormatSpec("TFJS", "TFJS", generate_tfjs, "Directory containing model.json and a binary weight shard."),
        FormatSpec("TF1 Hub format (deprecated)", None, None, "Requires deprecated TensorFlow 1 Hub tooling."),
        FormatSpec("Tensorizer", "Tensorizer", generate_tensorizer),
        FormatSpec("TFRecords", "TFRecords.tfrecords", generate_tfrecords),
        FormatSpec("NPY", "NPY.npy", generate_npy),
        FormatSpec("NPZ", "NPZ.npz", generate_npz),
        FormatSpec("GGUF", "GGUF.gguf", generate_gguf),
        FormatSpec("GGML", None, None, "Requires GGML writer or spec-specific implementation."),
        FormatSpec("GGMF (deprecated)", None, None, "Requires deprecated GGML-era serializer."),
        FormatSpec("GGJT (deprecated)", None, None, "Requires deprecated GGML-era serializer."),
        FormatSpec("NetCDF", "NetCDF.nc", generate_netcdf),
        FormatSpec("PMML", "PMML", generate_pmml),
        FormatSpec("MLeap", None, None, "Requires Spark/MLeap bundle tooling."),
        FormatSpec("CoreML", None, None, "Requires coremltools and CoreML conversion support."),
        FormatSpec("MLFlow Format", "MLFlowFormat", generate_mlflow_format, "Directory containing MLmodel metadata and serialized model artifacts."),
        FormatSpec("MLFlow TensorSpec input format", "MLFlowTensorSpecInputFormat.json", generate_mlflow_tensorspec),
        FormatSpec("SurrealML", None, None, "Requires SurrealML-specific exporter."),
        FormatSpec("Llamafile", None, None, "Requires llamafile packaging toolchain."),
        FormatSpec(".prompt", None, None, "Prompt format details are not implemented yet."),
        FormatSpec("Pickle", "Pickle.pkl", generate_pickle),
        FormatSpec("Joblib", "Joblib", generate_joblib),
        FormatSpec("Nemo", None, None, "Requires NVIDIA NeMo tooling."),
        FormatSpec("Riva", None, None, "Requires NVIDIA Riva tooling."),
        FormatSpec("AVRO", "AVRO", generate_avro),
        FormatSpec("PARQUET", "PARQUET", generate_parquet),
        FormatSpec("ORC", "ORC", generate_orc),
        FormatSpec("JSON", "JSON", generate_json),
        FormatSpec("CSV", "CSV", generate_csv),
        FormatSpec("Protocol Buffers", "ProtocolBuffers", generate_protobuf),
        FormatSpec("HDF5", "HDF5.h5", generate_hdf5),
        FormatSpec("Caffe", None, None, "Requires caffe.proto definitions and compatible serializers."),
        FormatSpec("ArmNN Flatbuffers", None, None, "Requires ArmNN flatbuffer schema and writer."),
        FormatSpec("Cambricon", None, None, "Requires Cambricon tooling or schema details."),
        FormatSpec("Circle", None, None, "Requires Circle flatbuffer schema and writer."),
        FormatSpec("ZIP", "ZIP", generate_zip),
        FormatSpec("CNTK v1 (deprecated)", None, None, "Requires deprecated CNTK tooling."),
        FormatSpec("CNTK v2", None, None, "Requires CNTK tooling."),
        FormatSpec("Darknet", None, None, "Requires Darknet config and weight writers."),
        FormatSpec("DL4J", None, None, "Requires DL4J model packaging conventions."),
        FormatSpec("Deep Learning Container (DLC)", None, None, "Requires Qualcomm Neural Processing SDK tooling."),
    ]


def write_manifest(output_dir: Path, results: list[Result]) -> None:
    manifest_path = output_dir / "manifest.tsv"
    with manifest_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["readme_name", "status", "relative_path", "notes"])
        for result in results:
            writer.writerow([result.readme_name, result.status, result.relative_path, result.notes])


def generate_all(output_dir: Path) -> list[Result]:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results: list[Result] = []
    for spec in build_specs():
        if spec.generator is None or spec.output_name is None:
            results.append(
                Result(
                    readme_name=spec.readme_name,
                    status="unsupported",
                    relative_path="",
                    notes=spec.notes,
                )
            )
            continue

        target = output_dir / spec.output_name
        try:
            spec.generator(target)
        except Exception as exc:  # pragma: no cover - generator failures are surfaced in manifest
            results.append(
                Result(
                    readme_name=spec.readme_name,
                    status="error",
                    relative_path=spec.output_name,
                    notes=f"{spec.notes} {type(exc).__name__}: {exc}".strip(),
                )
            )
            continue

        results.append(
            Result(
                readme_name=spec.readme_name,
                status="generated",
                relative_path=spec.output_name,
                notes=spec.notes,
            )
        )

    write_manifest(output_dir, results)
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate real sample artifacts for supported ML file formats.")
    parser.add_argument(
        "--output-dir",
        default="bin",
        help="Directory where the generated artifacts should be written.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = generate_all(Path(args.output_dir))
    generated = sum(result.status == "generated" for result in results)
    unsupported = sum(result.status == "unsupported" for result in results)
    errors = sum(result.status == "error" for result in results)
    print(f"Generated {generated} artifacts, {unsupported} unsupported entries, {errors} errors.")


if __name__ == "__main__":
    main()
