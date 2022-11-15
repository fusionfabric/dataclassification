# dataclassification: A python package to classify API swaggers and datasets
[![Linters](https://github.com/fusionfabric/dataclassification/actions/workflows/linters.yml/badge.svg)](https://github.com/fusionfabric/dataclassification/actions/workflows/linters.yml)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Ffusionfabric%2Fffdc-data-classification-engine.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Ffusionfabric%2Fffdc-data-classification-engine?ref=badge_shield)
[![Whitesource-Scan](https://github.com/fusionfabric/dataclassification/actions/workflows/ws-scan.yml/badge.svg)](https://github.com/fusionfabric/dataclassification/actions/workflows/ws-scan.yml)
[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

dataclassification is a python package that classifies dataset schemas and API swaggers with user-defined custom definitions and rules.

## What is Data Classification?

Data classification is a method of assigning tags or labels to data fields such that they can be assigned a certain designation of risk, typically in alignment with an Enterprise Data Classification Policy. Many companies use a model with 3 or more classification categories, e.g., Public, Internal Use, and Restricted. Once a classification has been assigned to data, that data should then be secured with controls commensurate to the level of risk that is represented. For example, a company may require that all Restricted data is encrypted both at rest and in transit, while Internal Use data may be allowed to be stored without specific encryption, but still require encryption in transit. Public data is typically that which has been authorized for public disclosure by a company’s Communications, Legal or Marketing team, and due to its intended use, would not require encryption at all.

## Flow Diagram

![DC-diagram](https://user-images.githubusercontent.com/65346396/200917679-478724a8-1c97-4055-8401-74ca75212de5.png)

## Quickstart: Install from GitHub
### Prerequisite:
Python >= 3.7
### Instructions:
* Make sure python is installed on your machine
* Go to the GitHub repository and click on Code and then click on Download Zip
* Extract the Zip files to a location on your machine and locate the setup.py file
* Open shell/command prompt and navigate to the location of the setup.py file
* Run the following command:
```python
setup.py install
```

## Setting up the configuration files
There are two configuration files that need to be setup:
### [Data Dictionary.xlsx](https://github.com/fusionfabric/dataclassification/blob/main/samples/config_folder/Data%20Dictionary.xlsx)
This file has three sheets:
* Field Types: This sheet is used to define classifications with their Descriptions, Examples, Sensitivity and Guidelines. Headers include:
  * Field Type: This is the name of the classification value
  * Description: A description about the classification value
  * Examples: Example values where this particular classification would be assigned
  * Sensitive: If the classification value falls under any of the defined rules then that rule is defined over here else "No Rule" is the defined value
  * Guidelines: Helpful guidelines for the reivewer of the output Generated Dictionary to help in assessment of classification
* Rules: This sheet is used to setup the rules for the classification process. Each row constitutes one rule and it has the following 4 headers:
  * Allx: The Allx rule  headers can be used as a combination of values. For example if a swagger file should only be classified sensitive if a combination of two classified definitions occurs in the swagger then we need to setup a rule row with two All values as shown in the sample file denoted by "First Name" and "Last Name".
  You can add another column and name it All3 and in the same row add "Middle Name" to make it a combination of 3 classified definitions
  * Anyx: The Anyx rule headers can be used independent of each other. So if you want the occurence of even 1 classification definition out of a group of 12 to be classified as sensitive you can define all 12 in a single row with Any1, Any2.....Any12 as the headers
  * Tag1: This is the value given to the classification header which is defined in the config_sheet below
  * Tag2: This is the value give to the encryption header which is defined in the config_sheet below
  * Important point to remember is not to mix All and Any rules in the same row as in this case All rules will take precedence rendering Any header values useless
* config_sheet: This sheet is used to define certain parameters such as classification header, encryption header, maturity status and a list of parameters which can be excluded from the classification process
  * classification_header: This is the header value that gets added to the parameter containing sensitive information
  * encryption_header: This is the header value that gets added to the parameter contatining sensitive information where encryption is also needed(in the case of datasets)
  * maturity_status: A value to define the maturity level of your swagger file
  * parameter_exclusion_list: A list of parameters to be excluded from classification process. Standard values include - X-Request-ID,ETag,If-Match,Idempotency-Key
### [Dictionary Details.csv](https://github.com/fusionfabric/dataclassification/blob/main/samples/config_folder/Dictionary%20Details.csv)
This file is the master dictionary where we define the classifications for various parameters that will be found in swaggers or dataset. It contains the following headers:
* Field Type: This is the classification defintion assigned to the parameter
* Technical Name: This is the technical name for the parsed parameter, it follows the definition/name or object/property naming convention
* Object: This is the Definition or Object value from the above Technical Name
* Field: This is the Name or Property value from the above Technical Name
* Exceptions - Array - API Name: This column is used when we need to assign two different classification definitions for the same technical name in the master dicitonary. In this scenario, we assign the more commonly used definition out of the two cases normally but for the other definition we also define the name of the APIs that will use this specific definition in the exceptions column.
Names are always defined like "test-api-v" so that they are version agnostic and in the case of multiple APIs needing to be defined we use a ";" delimeter. So example would be "test-api1-v;test-api2-v;test-api3-v". This can also be seen in row 21 of the sample Dictionary Details.csv file
## [Folder structure required for swaggers](https://github.com/fusionfabric/dataclassification/tree/main/samples/productdirectory)
The product directory needs to have a defined structure as shown under the samples. It has the following structure:
* productdirectory: The name of this directory represents the product name. For as many APIs we have under this product, we will have equal number of subfolders with those API names
  * apiname1-version: It is a folder that represents the API name along with the version number
  * apiname2-version: Same as above just for a different API
  * APIConfig.json: This file contains information about the various APIs under the product. This information includeds name, path and versions
    * name: This is the name of the API
    * path: This is the path to the API
    * versions: This is an array which contains information about the various API versions, their APIId, releaseDataClassifier and if they are obsolete
      * apiId: Unique identified for the APIs
      * releaseDataClassifier: This is important as "release" value means the API should go through classification whereas "skip" value prevents the API from undergoing classification process
      * obsolete: This is important as it identifies if an API is in use or not. If false only then API goes through classification process
## Try it out
Use the following code with the samples provided to test the process out:

```python
from dataclassification.run import RunClassificationEngine

productDirectory="Enter the path to the product directory"
config_folder="Enter the path to the config folder"
app_name="Enter the name of your product or application"
ce=RunClassificationEngine(productDirectory, config_folder, app_name)
```
Following the run, you wil be able to view the results in the product directory itself. Already classified versions of the sample swagger files have been uploaded for comparison [here](https://github.com/fusionfabric/dataclassification/tree/main/samples/classified%20swaggers%20for%20reference).
## Contributing
All contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome.

If you are simply looking to start working with the dataclassification codebase, navigate to the [GitHub "issues" tab](https://github.com/fusionfabric/dataclassification/issues) to find issues that interest you. When you start working on an issue, it’s a good idea to assign the issue to yourself, so nobody else duplicates the work on it.

If for whatever reason you are not able to continue working with the issue, please try to unassign it, so other people know it’s available again. You can check the list of assigned issues, since people may not be working in them anymore.
If you want to work on one that is assigned, feel free to kindly ask the current assignee if you can take it (please allow at least a week of inactivity before considering work in the issue discontinued).

Or maybe through using dataclassification you have an idea of your own or are looking for something in the documentation and thinking ‘this can be improved’...you can do something about it by raising your own issue!

## License
[MIT License](https://github.com/fusionfabric/dataclassification/blob/main/LICENSE)
