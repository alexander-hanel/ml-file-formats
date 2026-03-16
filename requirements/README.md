# Environment Requirements

These requirement files capture the Python environments used to generate samples in this repository.

## Files

- `requirements-main.txt`
Used for [`generate_real_samples.py`](../generate_real_samples.py) in `.venv`

- `requirements-tf1-legacy.txt`
Used for [`generate_legacy_samples.py`](../generate_legacy_samples.py) in `.venv-py37`

- `requirements-torch13-legacy.txt`
Used for archived `torch==1.3.1+cpu` generation in `.venv-torch13`

- `requirements-torch11-legacy.txt`
Used for archived `torch==1.1.0` generation in `.venv-torch11`

- `requirements-torch10-legacy.txt`
Used for archived `torch==1.0.1` generation in `.venv-torch10`

- `requirements-torch041-legacy.txt`
Used for archived `torch==0.4.1` probing in `.venv-torch041`

## Notes

- These files were generated from `pip freeze`, so they are intended for reproducibility rather than minimal dependency declaration.
- Some legacy environments depend on archived PyTorch wheels that are not available from plain PyPI. Recreating those environments may require using the PyTorch wheel index, for example `-f https://download.pytorch.org/whl/torch_stable.html`.
- The main environment includes some extra packages that were installed during exploration. It is reproducible, but not minimal.
