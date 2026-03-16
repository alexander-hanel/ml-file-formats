#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import textwrap
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Result:
    readme_name: str
    status: str
    relative_path: str
    notes: str


def run_python(python_exe: Path, code: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [str(python_exe), "-c", code, str(output_path)],
        check=True,
        text=True,
    )


def generate_torchscript_v13(output_path: Path) -> None:
    code = textwrap.dedent(
        """
        import sys
        import torch
        from torch import nn

        class M(nn.Module):
            def __init__(self):
                super().__init__()
                self.linear = nn.Linear(4, 2)

            def forward(self, x):
                return self.linear(x)

        model = M().eval()
        scripted = torch.jit.trace(model, torch.randn(1, 4))
        torch.jit.save(scripted, sys.argv[1])
        """
    )
    run_python(Path(".venv-torch13/Scripts/python.exe"), code, output_path)


def generate_torchscript_v11(output_path: Path) -> None:
    code = textwrap.dedent(
        """
        import sys
        import torch
        from torch import nn

        class M(nn.Module):
            def __init__(self):
                super().__init__()
                self.linear = nn.Linear(4, 2)

            def forward(self, x):
                return self.linear(x)

        model = M().eval()
        scripted = torch.jit.trace(model, torch.randn(1, 4))
        torch.jit.save(scripted, sys.argv[1])
        """
    )
    run_python(Path(".venv-torch11/Scripts/python.exe"), code, output_path)


def generate_torchscript_v10(output_path: Path) -> None:
    code = textwrap.dedent(
        """
        import sys
        import torch
        from torch import nn

        class M(nn.Module):
            def __init__(self):
                super().__init__()
                self.linear = nn.Linear(4, 2)

            def forward(self, x):
                return self.linear(x)

        model = M().eval()
        scripted = torch.jit.trace(model, torch.randn(1, 4))
        torch.jit.save(scripted, sys.argv[1])
        """
    )
    run_python(Path(".venv-torch10/Scripts/python.exe"), code, output_path)


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

    specs = [
        (
            "TorchScript v1.3 (deprecated)",
            "TorchScriptV13Deprecated.pt",
            generate_torchscript_v13,
            "Generated with archived torch 1.3.1.",
        ),
        (
            "TorchScript v1.1 (deprecated)",
            "TorchScriptV11Deprecated.pt",
            generate_torchscript_v11,
            "Generated with archived torch 1.1.0.",
        ),
        (
            "TorchScript v1.0 (deprecated)",
            "TorchScriptV10Deprecated.pt",
            generate_torchscript_v10,
            "Generated with archived torch 1.0.1.",
        ),
    ]

    results: list[Result] = []
    for readme_name, relative_path, generator, notes in specs:
        try:
            generator(output_dir / relative_path)
        except Exception as exc:  # pragma: no cover
            results.append(
                Result(
                    readme_name=readme_name,
                    status="error",
                    relative_path=relative_path,
                    notes=f"{notes} {type(exc).__name__}: {exc}".strip(),
                )
            )
        else:
            results.append(
                Result(
                    readme_name=readme_name,
                    status="generated",
                    relative_path=relative_path,
                    notes=notes,
                )
            )

    results.extend(
        [
            Result(
                readme_name="PyTorch v0.1.1",
                status="unsupported",
                relative_path="",
                notes="Archived wheels available on this Windows setup do not reach the historical tar-based serializer layout.",
            ),
            Result(
                readme_name="PyTorch v0.1.10",
                status="unsupported",
                relative_path="",
                notes="Archived wheels available on this Windows setup do not reach the historical stacked-pickle serializer layout.",
            ),
        ]
    )

    write_manifest(output_dir, results)
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate deprecated Torch/TorchScript sample artifacts in isolated legacy environments.")
    parser.add_argument(
        "--output-dir",
        default="legacy_torch_samples",
        help="Directory where the generated legacy Torch artifacts should be written.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = generate_all(Path(args.output_dir))
    generated = sum(result.status == "generated" for result in results)
    unsupported = sum(result.status == "unsupported" for result in results)
    errors = sum(result.status == "error" for result in results)
    print(f"Generated {generated} legacy torch artifacts, {unsupported} unsupported entries, {errors} errors.")


if __name__ == "__main__":
    main()
