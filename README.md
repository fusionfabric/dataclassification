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

## Setting up the configuration files
There are two configuration files that need to be setup:
### Data Dictionary.xlsx - 
This file has three sheets:
* Field Types: This sheet is used to define classifications with their Descriptions, Examples, Sensitivity and Guidelines. Headers include:
  * Field Type: This is the name of the classification value
  * Description: A description about the classification value
  * Examples: Example values where this particular classification would be assigned
  * Sensitive: If the classification value falls under any of the defined rules then that rule is defined over here else "No Rule" is the defined value
  * Guidelines: Helpful guidelines for the reivewer of the output Generated Dictionary to help in assessment of classification
* Rules: This sheet is used to setup the rules for the classification process. Each row constitues one rule and it has the following 2 headers:
  * Allx: The Allx rule  headers can be used as a combination of values. For example if a swagger file should only be classified sensitive if a combination of two classified definitions occurs in the swagger then we need to setup a rule row with two All values as shown in the sample file denoted by "First Name" and "Last Name". You can add another column and name it All3 and in the same row add "Middle Name" to make it a combination of 3 classified definitions
  * Anyx: The Anyx rule headers can be used independent of each other. So if you want the occurence of even 1 classification definition out of a group of 12 to be classified as sensitive you can define all 12 in a single row with Any1, Any2.....Any12 as the headers
  * Tag1: This is the value given to the classification header which is defined in the config_sheet below
  * Tag2: This is the value give to the encryption header which is defined in the config_sheet below
  * Important point to remember is not to mix All and Any rules in the same row as in this case All rules will take precedence rendering Any header values useless
* config_sheet: This sheet is used to define certain parameters such as classification header, encryption header, maturity status and a list of parameters which can be excluded from the classification process
  * classification_header: This is the header value that gets added to the parameter containing sensitive information
  * encryption_header: This is the header value that gets added to the parameter contatining sensitive information where encryption is also needed(in the case of datasets)
  * maturity_status: A value to define the maturity level of your swagger file
  * parameter_exclusion_list: A list of parameters to be excluded from classification process. Standard values include - X-Request-ID,ETag,If-Match,Idempotency-Key
### Dictionary Details.csv - (https://github.com/fusionfabric/ffdc-data-classification-engine/blob/main/samples/config_folder/Dictionary%20Details.csv)
This file is the master dictionary where we define the classifications for various parameters that will be found in swaggers or dataset. It contains the following headers:
* Field Type: This is the classification defintion assigned to the parameter
* Technical Name: This is the technical name for the parsed parameter, it follows the definition/name or object/property naming convention
* Object: This is the Definition or Object value from the above Technical Name
* Field: This is the Name or Property value from the above Technical Name
* Exceptions - Array - API Name: This column is used when we need to assign two different classification definitions for the same technical name in the master dicitonary. In this scenario, we assign the more commonly used definition out of the two cases normally but for the other definition we also define the name of the apis that will use this specific definition in the exceptions column. Names are always defined like "test-api-v" so that they are version agnostic and in the case of multiple apis needing to be defined we use a ";" delimeter. So example would be "test-api1-v;test-api2-v;test-api3-v". This can also be seen in row 21 of the sample Dictionary Details.csv file
### Folder structure required for swaggers
