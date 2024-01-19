# F5500 Python Module

The F5500 Python module simplifies the process of downloading, storing, reading, and managing F5500 datasets published by the Department of Labor. This project is currently a work in progress.
Installation

To install the module, run the following command in the terminal:

```python
pip install ./F5500_module
```

## Usage

Here's a brief overview of the module's functionalities:

### Downloading F5500 Datasets

To download a specific F5500 dataset, use the download function. For example:

```python
from f5500_module import download

# Example: Download the dataset for schedule "SCH_SB" in the year 2021 using the "Latest" modality.
download(schedule="SCH_SB", year="2021", modality="Latest", overwrite=False, archive="Datasets")
```

### Cleaning Datasets

The clean function is available to remove older versions of datasets, keeping only the most recent ones:

```python
from f5500_module import clean

# Example: Clean the 'Datasets' folder by removing outdated zip files.
clean(archive="Datasets")
```

### Reading F5500 Datasets

Use the read function to load a specific F5500 dataset into a Pandas DataFrame:

```python
from f5500_module import read

# Example: Read the dataset for schedule "SCH_SB" in the year 2021 using the "Latest" modality.
df = read(schedule="SCH_SB", year="2021", modality="Latest", mod_date="Latest", archive="Datasets")
```

### Workflow Demo

Explore the workflow_demo.ipynb file in this repository for a demonstration of a basic workflow using the F5500 module.

### Contributing

Feel free to contribute to the development of this module by submitting issues or pull requests.

### License

This project is licensed under the MIT License.
