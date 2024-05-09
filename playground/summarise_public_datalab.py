"""WARNING: this costs money

You will need to an ANTHROPIC_API_KEY and a DATALAB_API_KEY.

"""
from codeinterpreterapi import CodeInterpreterSession, File, settings
from pathlib import Path

settings.MODEL = "claude-3-haiku-20240307"
settings.CUSTOM_PACKAGES = ["datalab-api"]

README = """
A simple Python API that can interact with [*datalab*](https://github.com/the-grey-group/datalab) instances.

The idea here is to provide a set of utility functions and models for manipulating samples, cells, inventory, files, users and metadata associated with *datalab* entries in an automated way.

This API may not expose all the functionality available in a given *datalab* instance, and the idea would be that this package can support multiple versions of the underlying [*datalab* REST API](https://the-datalab.readthedocs.io/en/latest/rest_api/).
This means that the API is primarily *functional* in nature, as opposed to object-oriented, since *datalab* instances are free to use their own custom data models.
The available schemas are reported as instance metadata and in the future object-oriented models may be able to be genereated directly in the client (so e.g., the returned data would be Python objects like `Sample` rather than JSON data).

The issue tracker here will be used to track development of features, as well as bug reports.
If you have any suggestions or feedback, please post it there.

## Installation

The API can be used by installing this repository with `pip`, ideally in a fresh Python 3.9+ environment (created using e.g., conda, virtualenv or other related tools -- if you're not sure about this, ask).

Either from PyPI, for the latest released version:

```shell
pip install datalab-api
```

or for the latest development version from GitHub:

```shell
git clone git@github.com:datalab-org/datalab-api
cd datalab-api
pip install .
```

## Usage

Example usage as a Jupyter notebook can be found in the `examples` directory or
in the [online documentation](https://datalab-api.readthedocs.io/), as
well as the full [API
documentation](https://datalab-api.readthedocs.io/en/latest/reference/).

### Authentication

Currently the only supported authentication method is via an API key.
You can generate one for your account for a given *datalab* instance by visiting the `/get-api-key` endpoint of your chosen instance, or, if using a recent version of *datalab*, by visiting your account settings in the browser.

This API key can be set via the environment variable `DATALAB_API_KEY`.
To suport the use case of needing to interact with multiple datalab instances, the client will also check prefixed environment variables that use the [`IDENTIFIER_PREFIX` of the chosen datalab instance](https://the-datalab.readthedocs.io/en/latest/config/#mandatory-settings), e.g., `GREY_DATALAB_API_KEY` or `PUBLIC_DATALAB_API_KEY`.
Only keys that match will be read (e.g., other environment variables starting with `PUBLIC_` will be ignored, when connecting to the [public demo datalab](https://public.datalab.odbx.science)).

### Python API

This package implements basic functionality for displaying and manipulating entries:

```python
from datalab_api import DatalabClient

with DatalabClient("https://public.api.odbx.science") as client:

    # List all items of a given type
    items = client.get_items()

    # Get more info on a particular item
    item = client.get_item(item_id="test")

    # Upload a file to an item
    file_response = client.upload_file(filepath="my_echem_data.mpr", item_id="test")

```"""

SYSTEM_PROMPT = f"""

Use the datalab Python API package to query entries on the public datalab instance.
Each method of the DatalabClient class will return a dictionary constructed directly
from the JSON response of the Datalab API.

$(TASK)

The rest of this prompt contains the README for the datalab_api package, which you already have installed.
Here is the README\n:{README}"""

while True:
    with CodeInterpreterSession(
        verbose=True,
    ) as session:
        # generate a response based on user input
        task = input("$: ")
        response = session.generate_response(SYSTEM_PROMPT.replace("$(TASK)", task))
        # output the response
        response.show()
