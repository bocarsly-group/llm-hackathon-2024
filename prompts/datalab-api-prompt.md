Use the datalab Python API package to query entries on the public datalab instance.
Each method of the DatalabClient class will return a dictionary constructed directly
from the JSON response of the Datalab API.

Datalab uses "data blocks" to take a file attached to a sample, parse it
according to some scientific schema, and then make a plot.

The rest of this prompt contains the README for the datalab API package (called `datalab-api` on PyPI, accessible via module `datalab_api`), which you already have installed.

Here is the README:

A simple Python API that can interact with [*datalab*](https://github.com/the-grey-group/datalab) instances.

## Usage

Example usage as a Jupyter notebook can be found in the `examples` directory or
in the [online documentation](https://datalab-api.readthedocs.io/), as
well as the full [API
documentation](https://datalab-api.readthedocs.io/en/latest/reference/).

### Python API

This package implements basic functionality for displaying and manipulating entries:

```python
from datalab_api import DatalabClient

with DatalabClient("https://public.api.odbx.science") as client:

    # List all items of a given type
    # Types can be 'samples' or 'starting_materials'
    items = client.get_items(item_type="samples")

    # Get more info on a particular item called 'test'
    item = client.get_item(item_id="test")

    # Create a new item
    client.create_item

    # Attach a file to an item and get the uploaded ID
    file_response = client.upload_file(filepath="my_echem_data.mpr", item_id="test")
    file_id = file_response["file_id"]

    # Create a data block for a sample, then show the plot
    client.create_data_block(item_id="test", file_ids=file_id)

    # Now fetch the item again with blocks enabled and see the plot
    client.get_item(item_id="test1", load_blocks=True, display=True)

```
