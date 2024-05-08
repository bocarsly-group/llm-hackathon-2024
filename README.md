# llm-hackathon-2024

Working repository for team datalab in the 2024 materials/chemistry LLM hackathon

## Setup

Make a Python environment (with whatever method you prefer) and install the
deps from the `requirements.txt` file, e.g., using the standard library:

```shell
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

or using something like [`uv`](https://github.com/astral-sh/uv):

```shell
uv venv
uv pip install -r requirements.txt
. .venv/bin/activate
```

If you want to add a dependency, you can add it there.
Occasionally we will also generate a lockfile to make sure all have compatible
requirements.

Generate lock:

```shell
uv pip-compile -r requirements.txt > requirements-lock.txt
```

Install lock (`uv`):

```shell
uv pip install -r requirements-lock.txt
````

or directly in your virtual environment:

```shell
pip install -r requirements-lock.txt
```
