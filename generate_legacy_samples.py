#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Result:
    readme_name: str
    status: str
    relative_path: str
    notes: str


def generate_tf1_hub_format(output_dir: Path) -> None:
    import tensorflow as tf
    import tensorflow_hub as hub

    checkpoint_dir = output_dir.parent / "_tf1_hub_checkpoint"
    if checkpoint_dir.exists():
        shutil.rmtree(checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def module_fn():
        x = tf.placeholder(dtype=tf.float32, shape=[None, 4], name="input")
        y = tf.layers.dense(x, 2, name="dense")
        hub.add_signature(inputs={"x": x}, outputs={"y": y})

    spec = hub.create_module_spec(module_fn)

    with tf.Graph().as_default():
        hub.Module(spec)
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            checkpoint_path = tf.train.Saver().save(sess, str(checkpoint_dir / "module.ckpt"))

    spec.export(
        str(output_dir),
        checkpoint_path=checkpoint_path,
        name_transform_fn=lambda name: "module/" + name,
    )

    shutil.rmtree(checkpoint_dir)


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
    target = output_dir / "TF1HubFormatDeprecated"
    try:
        generate_tf1_hub_format(target)
    except Exception as exc:  # pragma: no cover
        results.append(
            Result(
                readme_name="TF1 Hub format (deprecated)",
                status="error",
                relative_path="TF1HubFormatDeprecated",
                notes=f"{type(exc).__name__}: {exc}",
            )
        )
    else:
        results.append(
            Result(
                readme_name="TF1 Hub format (deprecated)",
                status="generated",
                relative_path="TF1HubFormatDeprecated",
                notes="Directory containing tfhub_module.pb, saved_model.pb, and variables.",
            )
        )

    write_manifest(output_dir, results)
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate legacy/deprecated sample artifacts in an isolated legacy environment.")
    parser.add_argument(
        "--output-dir",
        default="legacy_samples",
        help="Directory where the generated legacy artifacts should be written.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = generate_all(Path(args.output_dir))
    generated = sum(result.status == "generated" for result in results)
    errors = sum(result.status == "error" for result in results)
    print(f"Generated {generated} legacy artifacts, {errors} errors.")


if __name__ == "__main__":
    main()
