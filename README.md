# ffdc-data-classification-engine
![example workflow](https://github.com/fusionfabric/ffdc-data-classification-engine/actions/workflows/superlinter.yml/badge.svg)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Ffusionfabric%2Fffdc-data-classification-engine.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Ffusionfabric%2Fffdc-data-classification-engine?ref=badge_shield)
[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

ffdc-data-classification-engine lets you classify your datasets and API swaggers using custom definitions and rules that are defined via an exccel template and a dictionary file.

## Using Excel to define your master dictionary and the configuration template

## Quickstart

### Install from github-packages

```python
python -m pip install dataclassificationffdc
```

### Setting up the configuration files
There are two configuration files that need to be setup:
* Data Dictionary.xlsx - This file has three sheets:
  * Field Types: This sheet is used to define classifications with their Descriptions, Examples, Sensitivity and Guidelines
  * Rules: This sheet is used to setup the rules for the classification process
  * config_sheet: This sheet is used to define certain parameters such as classification header, encryption header, maturity status and a list of parameters which can be excluded from the classification process
* Dictionary Details.csv - This file is the master dictionary where we define the classifications for various parameters that will be found in swaggers or dataset
### Setting up the master dictionary file
