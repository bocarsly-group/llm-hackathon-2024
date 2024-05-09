# llm-hackathon-2024

Working repository for Team [*datalab*](https://github.com/the-grey-group/datalab) in the [2024 LLM Hackathon for Applications in Materials & Chemistry](https://www.eventbrite.com/e/llm-hackathon-for-applications-in-materials-and-chemistry-tickets-868303598437).

## Plan

Create an LLM-based agent that can interact with the [datalab Python API](https://github.com/datalab-org/datalab-api) so we don't have to implement things ourselves (as developers of datalab).
This follows on from our work on *Whinchat* 🐦 last year, where we integrated GPT-based models from OpenAI with [*datalab*](https://github.com/the-grey-group/datalab) such that users can interact conversationally with their raw data (see Jablonka *et al*., [0.1039/D3DD00113J](https://doi.org/10.1039/D3DD00113J)).

Potential applications:

- Using datalab to parse datafiles, return e.g., dataframes then using the LLM to create plots of data we don't support as blocks, like comparing XRD data from multiple samples
- Upload a picture of a lab notebook page, then use the LLM to read it and make the appropriate API call to add it to datalab
- Many more! (pls add them)

### Log of experiments

- [`playground/summarise_public_datalab.py`] Using [shroominic/codeinterpreter-api](https://github.com/shroominic/codeinterpreter-api/blob/main/pyproject.toml) to generate Python scripts that are executed locally that do the prompted task.
   - Works up to a point (at least with latest models, e.g., Claude 3 Opus [expensive]) but requires lots of back-and-forth to generate valid code.
   - Most of the problems are related to either
      1. eccentricities of our API (e.g., needing to know ahead of time magic strings for item types and otherwise)
      2. weird behaviour where syntactically invalid code is created for the first few iterations
    - Therefore, at least some time during this hackathon will be made making
      our API package more bot- (and hopefully human-)friendly, via more examples and more ergonomic tweaks (e.g., automatically pluralising item types if the singular is given).


## Setup

### Install dependencies

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
uv pip compile --prerelease=allow -r requirements.txt > requirements-lock.txt
```

Install lock (`uv`):

```shell
uv pip install ---prerelease=allow -r requirements-lock.txt
````

or directly in your virtual environment:

```shell
pip install -r requirements-lock.txt
```

### Running the Streamlit app

After dependencies have been installed, you can launch the Streamlit app with:

```shell
streamlit run streamlit_app/app.py
```

