# ProActuary – <span style="font-size:0.75em">Package to read and operate on actuarial file formats</span>

This Python package provides utilities tailored for specialized text formats frequently encountered in actuarial work.

## Background

Within the actuarial domain, there's specific file formats that, at a glance, appears similar to a CSV. However, it incorporates some unique characteristics:

* Allows for preamble content before the header.
* Allows for type annotations.
* Supports metadata appended after the main content.
* Starting any data line with an asterisk.
* Enforces headers not to be surrounded by quotes, while all other data strings should be.

Given the intricate nature of this format and the emphasis on data integrity in actuarial work, there's a demand for a toolset that can seamlessly handle such files. Enter ProActuary.

## Features

* **Read Functionality**: Efficiently convert specialized actuarial text files into a pandas DataFrame.
* **Write Functionality**: Export pandas DataFrames back into the specialized actuarial text format, adhering to its nuances.
* **Flexibility**: Additional parameters can be passed via kwargs, making the package adaptable and extensible.
* **Consistency**: Adopts a naming convention similar to `pandas`, ensuring familiarity and ease of use.

## Installation

To install ProActuary:

```
pip install proactuary
```

## Usage

### Reading Files

```python
from proactuary import read_pro

df = read_pro("path_to_file.pro")
```

You can pass additional parameters via kwargs to tailor the reading process to specific needs.

### Writing Files

```python
from proactuary import to_pro

to_pro(df, "output_filename.pro")
```

Writing ensures that the file conforms to the specialized format's requirements, such as the specific handling of headers and quoted strings.

## Dependencies

While the package is self-sufficient for most tasks, it relies on `pandas` for DataFrame operations. Detailed dependencies can be found in the `requirements.txt` file.

## Contribution & Future Development

This package is an ongoing effort to streamline the process of handling actuarial file formats. Contributions, feedback, and suggestions are most welcome! Fork the repository and submit a pull request or open an issue.

## License

ProActuary is licensed under the MIT License. For more details, consult the LICENSE file.