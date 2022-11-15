# dataclassification: A python package to classify OpenAPI 2.0 and 3.0
[![Linters](https://github.com/fusionfabric/dataclassification/actions/workflows/linters.yml/badge.svg)](https://github.com/fusionfabric/dataclassification/actions/workflows/linters.yml)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Ffusionfabric%2Fffdc-data-classification-engine.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Ffusionfabric%2Fffdc-data-classification-engine?ref=badge_shield)
[![Whitesource-Scan](https://github.com/fusionfabric/dataclassification/actions/workflows/ws-scan.yml/badge.svg)](https://github.com/fusionfabric/dataclassification/actions/workflows/ws-scan.yml)
[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

dataclassification is a python package that classifies OpenAPI 2.0 and 3.0 with custom-values based on user-defined definitions and rules.

## What is Data Classification?

Data classification is a method of assigning tags or labels to data fields such that they can be assigned a certain designation of risk, typically in alignment with an Enterprise Data Classification Policy. Many companies use a model with 3 or more classification categories, e.g., Public, Internal Use, and Restricted. Once a classification has been assigned to data, that data should then be secured with controls commensurate to the level of risk that is represented. For example, a company may require that all Restricted data is encrypted both at rest and in transit, while Internal Use data may be allowed to be stored without specific encryption, but still require encryption in transit. Public data is typically that which has been authorized for public disclosure by a company’s Communications, Legal or Marketing team, and due to its intended use, would not require encryption at all.

## Why is Data Classification important?

Data privacy regulations and the persistent threat of data loss or theft require that businesses know and secure their data, and in some cases the data of others (customers, partners, clients, etc.). Data Classification provides a layer of abstraction and a method for a business to designate the relative sensitivity of their data by using categories, or classifications based on a blend of permitted data use and representative risk of unauthorized exposure. As the cost of maintaining data security grows, it is most practical for companies to spend more of their budget and effort protecting the data that represents the most risk, hence a classification system provides a framework for assignment of standard security controls that are relative and appropriate to the sensitivity and value of the data being protected.

## dataclassification: Deep Dive

dataclassification is a set of scripts that compares a list of data elements (table/object names, field names) to a set of predefined and extensible mappings of data types to data classification values. A master dictionary file is maintained and augmented with each new data type review, such that precedential values from previous reviews can be used to assign a probable data type to new, unclassified fields. The master dictionary is augmented each time there are new fields that are classified manually, such that future classifications are more efficient. A process of trimming the master dictionary and “squashing” duplicative records helps to boost efficiency as well as reduce the overhead of maintaining it. In addition to mapping data types to data fields, user-configurable rules determine what field types are always Restricted (e.g., direct personal identifiers like Full Name, Driver’s License Number, etc.) or Restricted-only when in conjunction with other personal identifiers, e.g., a First Name is generally sensitive only when paired with a Surname, Home Address or other data that would compromise the privacy of an individual person.

## Flow Diagram

![DC-diagram](https://user-images.githubusercontent.com/65346396/200917679-478724a8-1c97-4055-8401-74ca75212de5.png)

## Quickstart: Setting up Python
### Instructions for Windows:
* Go to the [page](https://www.python.org/downloads/windows/) and find the latest stable release of Python
* On this page move to Files and download Windows x86-64 executable installer for 64-bit or Windows x86 executable installer for 32-bit
* Run the python installer
* Make sure to mark Add Python 3.x to PATH otherwise you will have to do it explicitly afterwards
* After installation is complete click on Close. You can launch python from start now to check that it is working.
### Instructions for Linux:
* On every Linux system including the following OS - Ubuntu, Linux Mint, Debian, openSUSE, CentOS, Fedora, Arch Linux, Python is already installed
* You can check it using the following command from the terminal
```bash
$ python --version
```
* You can upgrade to the required version by running the following command: $ sudo apt-get install python3.x
 * Note x denotes the a particular version of python, so if you want to install version 3.9 then command will be - $ sudo apt-get install python3.9
* To verify the installation enter the following commands in your Terminal - python3.x
 * This should open python in the terminal
### Instructions for MAC:
* Download and install Homebrew Package Manager if it isn't already installed
 * Open Terminal from Application -> Utilities. Enter following command in macOS terminal - /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
* Enter the system password if prompted. After you see a message called “Installation Successful”. You are ready to install python version 3 on your macOS.
* Open Terminal from Application -> Utilities and enter following command - brew install python3
* After command processing is complete,  enter following command in your Terminal app to verify - python
## Quickstart: Install from GitHub

### Instructions:
* Make sure python is installed on your machine
* Go to the GitHub repository and click on Code and then click on Download Zip
* Extract the Zip files to a location on your machine and locate the setup.py file
* Open shell/command prompt and navigate to the location of the setup.py file
* Run the following command:
```python
setup.py install
```

## Try it out
* Go to the GitHub repository and click on Code and then click on Download Zip
* Extract the Zip files to a location on your machine and locate the 'hello classification.py' file
* Run the 'hello classification.py' file
* In the folders/files extracted above, go to samples and then go to productdirectory. You can view all the results of the run over here.
We have also provided already classified versions of the sample swagger files for comparison [here](https://github.com/fusionfabric/dataclassification/tree/main/samples/classified%20swaggers%20for%20reference).

## Make it your own: Setting up the configuration files
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
## Make it your own: Running the Code

Once you are familiar with the process, you can make it your own by using the following code in a python file:
```python
from dataclassification.run import RunClassificationEngine

productDirectory="Enter the path to the product directory"
config_folder="Enter the path to the config folder"
app_name="Enter the name of your product or application"
ce=RunClassificationEngine(productDirectory, config_folder, app_name)
```

## Contributing
All contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome.

If you are simply looking to start working with the dataclassification codebase, navigate to the [GitHub "issues" tab](https://github.com/fusionfabric/dataclassification/issues) to find issues that interest you. When you start working on an issue, it’s a good idea to assign the issue to yourself, so nobody else duplicates the work on it.

If for whatever reason you are not able to continue working with the issue, please try to unassign it, so other people know it’s available again. You can check the list of assigned issues, since people may not be working in them anymore.
If you want to work on one that is assigned, feel free to kindly ask the current assignee if you can take it (please allow at least a week of inactivity before considering work in the issue discontinued).

Or maybe through using dataclassification you have an idea of your own or are looking for something in the documentation and thinking ‘this can be improved’...you can do something about it by raising your own issue!

## License
[MIT License](https://github.com/fusionfabric/dataclassification/blob/main/LICENSE)
