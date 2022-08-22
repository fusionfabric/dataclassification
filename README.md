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
## Data Dictionary.xlsx - This file has three sheets:
* Field Types: This sheet is used to define classifications with their Descriptions, Examples, Sensitivity and Guidelines. Headers include:
  * Field Type: This is the name of the classification value
  * Description: A description about the classification value
  * Examples: Example values where this particular classification would be assigned
  * Sensitive: If the classification value falls under any of the defined rules then that rule is defined over here else "No Rule" is the defined value
  * Guidelines: Helpful guidelines for the reivewer of the output Generated Dictionary to help in assessment of classification
* Rules: This sheet is used to setup the rules for the classification process. Each row constitues one rule and it has the following 2 headers:
  * Allx: The Allx rules can be used as a combination of values. For example if a swagger file should only be classified sensitive if a combination of two classified definitions occurs in the swagger then we need to setup a rule row with two All values as shown in the sample file denoted by "First Name" and "Last Name". You can add another column and name it All3 and in the same row add "Middle Name" to make it a combination of 3 classified definitions
  * Anyx:
* config_sheet: This sheet is used to define certain parameters such as classification header, encryption header, maturity status and a list of parameters which can be excluded from the classification process
## Dictionary Details.csv - This file is the master dictionary where we define the classifications for various parameters that will be found in swaggers or dataset
### Setting up the master dictionary file
