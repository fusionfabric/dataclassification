import os, json, sys, logging
from os.path import join, getsize

from DataClassification.Extensions.Swaggers.SwaggerObj import SwaggerObj
from DataClassification.Extensions.Swaggers.OAS2.Oas2Handler import Oas2Handler
from DataClassification.Extensions.Swaggers.OAS3.Oas3Handler import Oas3Handler

# Assumptions:
# The swagger files are located in a folder, with or without subfolders.
# At this point, only OpenAPI v2 is supported.
class SwaggerHandler:
    """
        Works through each swagger file and parses out their swagger definitions which can then be used for
        classification process, it does so by using the various versions of swagger handlers available to the engine
        param root_folder is used to supply the location of the swagger files
        param parameter_exclusion_list provides a list of swagger definitions to be excluded from parsing
        param filenames provides a list of supported file types
        """

    def __init__(self, root_folder, maturity_status, parameter_exclusion_list, filenames):
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(filename=root_folder + '/data-classification.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
        self.parameter_descriptions = {}
        self.maturity_status = maturity_status
        self.filenames=filenames
        self.files_list = []
        self.json_list = []
        self.parameter_exclusion_list=parameter_exclusion_list
        self.oas2=Oas2Handler(self.parameter_descriptions,self.parameter_exclusion_list)
        self.oas3=Oas3Handler(self.parameter_descriptions,self.parameter_exclusion_list)
        #Get the list of APIs from LOB repository
        #Iterate through the APIs list and add the swaggers to the json_list, only
        #the apis which are opted to do classification(only if releaseDataClassifier is "test"/"release")
        try:
            if 'tmp' in root_folder:
                swaggerFilePath=root_folder+"/swagger.json"
                if os.path.isfile(swaggerFilePath):
                    self.json_list.append(swaggerFilePath)
            elif 'swagger' in filenames:
                with open(root_folder+"/APIConfig.json") as apiConfig:
                    apis=json.load(apiConfig)
                    for api in apis["apis"]:
                        for version in api["versions"]:
                            if "obsolete" not in version or version["obsolete"]==False:
                                apiDirectory=api["name"]+"-"+version["apiVersion"]
                                if "releaseDataClassifier" not in version:
                                    releaseDataClassifier="skip"
                                else:
                                    releaseDataClassifier= version["releaseDataClassifier"]
                                    if releaseDataClassifier == "test" or  releaseDataClassifier == "release":
                                            swaggerFilePath=root_folder+"/"+apiDirectory+"/Swagger.json"
                                            if os.path.isfile(swaggerFilePath):
                                                self.json_list.append(swaggerFilePath)
                                                if 'events' in filenames:
                                                    eventsFilePath=root_folder+"/"+apiDirectory+"/events.json"
                                                    if os.path.isfile(eventsFilePath):
                                                        self.json_list.append(eventsFilePath)
            else:
                #Get the list of datasets from LOB dataset repository
                with os.scandir(root_folder) as entries:
                    for entry in entries:
                        if entry.is_dir():
                            for files in os.walk(entry):
                                for file in files[2]:
                                        for filename in filenames:
                                                if filename.lower()+'.json' == file.lower() and '.json' in file.lower() and '.log' not in file.lower() and '-classified' not in file.lower():
                                                    self.json_list.append('{}/{}/{}'.format(root_folder,entry.name, file))
            logging.info("json_list of all swaggers/events has been compiled")                                        
        except Exception as e:
            logging.error(e)
            sys.exit(e)

    def write_file(self,sobj: SwaggerObj):
        file_name, file_extension = os.path.splitext(sobj.path)
        path = file_name + "-classified" + file_extension
        with open(path, 'w') as file:
            jsonObject = json.dumps(sobj.obj, indent = 4)
            if 'dataset-schema-OAS' in self.filenames:
                jsonObject=jsonObject.replace("x-legalTerms","legalTerms").replace("x-id","$id").replace("x-additionalProperties","additionalProperties").replace("x-additionalItems","additionalItems").replace("/definitions/","/properties/")
            file.write(jsonObject)

    def get_json(self,root_directory, path):
        with open(path,encoding='utf-8-sig') as json_file:
            try:
                jsonConvert=json.load(json_file)
                sobj = SwaggerObj(root_directory,path, jsonConvert)
                if 'info' in sobj.obj and self.maturity_status in sobj.obj['info'] and sobj.obj['info'][self.maturity_status] =="DEPRECATED":
                    logging.error("This API is deprecated and cannot be considered by the tool {}".format(path))
                    raise ValueError("This API is deprecated and cannot be considered by the tool {}".format(path))
                # if 'swagger' in sobj.obj and sobj.obj['swagger'] == '2.0':
                #     return sobj
                # else:
                #     raise ValueError("Script does not support OAS 3 yet. Cannot handle {}".format(path))
                return sobj
            except json.JSONDecodeError as exc:
                logging.error("Error reading or decoding the file {}: {}".format(path,exc))
                raise ValueError("Error reading or decoding the file {}: {}".format(path,exc))

    def get_endpoints(self, sobj: SwaggerObj):
        endpoints = []
        for path in sobj.obj['paths']:
            endpoints.append(path)
        return endpoints

    def get_request_parameters1(self, sobj: SwaggerObj, endpoint: str):
        parameters_list = {}
        if 'swagger' in sobj.obj and sobj.obj['swagger'] == '2.0':
            parameters_list=self.oas2.get_request_parameters1(sobj,endpoint)
        else:
            parameters_list=self.oas3.get_request_parameters1(sobj,endpoint)
        return parameters_list

    def get_response_parameters1(self, sobj: SwaggerObj, endpoint: str):
        parameters_list = {}
        if 'swagger' in sobj.obj and sobj.obj['swagger'] == '2.0':
            parameters_list=self.oas2.get_response_parameters1(sobj,endpoint)
        else:
            parameters_list=self.oas3.get_response_parameters1(sobj,endpoint)
        return parameters_list

    def get_definitions(self, sobj: SwaggerObj):
        definitions_list = []
        if 'swagger' in sobj.obj and sobj.obj['swagger'] == '2.0':
            definitions_list=self.oas2.get_definitions(sobj)
        else:
            definitions_list=self.oas3.get_definitions(sobj)
        return definitions_list

    def get_parameters(self, sobj: SwaggerObj):
        parameters = []
        if 'swagger' in sobj.obj and sobj.obj['swagger'] == '2.0':
            parameters=self.oas2.get_parameters(sobj)
        else:
            parameters=self.oas3.get_parameters(sobj)
        return parameters

    def get_parameter_references(self, sobj: SwaggerObj):
        parameters = []
        if 'swagger' in sobj.obj and sobj.obj['swagger'] == '2.0':
            parameters=self.oas2.get_parameter_references(sobj)
        else:
            parameters=self.oas3.get_parameter_references(sobj)
        return parameters

    def get_extended_request_parameters(self, sobj: SwaggerObj, endpoint: str):
            parameters_list = []
            if 'swagger' in sobj.obj and sobj.obj['swagger'] == '2.0':
                parameters_list=self.oas2.get_extended_request_parameters(sobj,endpoint)
            else:
                parameters_list=self.oas3.get_extended_request_parameters(sobj,endpoint)
            return parameters_list

    def get_extended_request_parameters_by_method(self, sobj: SwaggerObj, endpoint: str, method: str):
            parameters_list = []
            if 'swagger' in sobj.obj and sobj.obj['swagger'] == '2.0':
                parameters_list=self.oas2.get_extended_request_parameters_by_method(sobj,endpoint,method)
            else:
                parameters_list=self.oas3.get_extended_request_parameters_by_method(sobj,endpoint,method)
            return parameters_list

    def get_extended_response_parameters(self, sobj: SwaggerObj, endpoint: str):
        parameters_list = []
        if 'swagger' in sobj.obj and sobj.obj['swagger'] == '2.0':
            parameters_list=self.oas2.get_extended_response_parameters(sobj,endpoint)
        else:
            parameters_list=self.oas3.get_extended_response_parameters(sobj,endpoint)
        return parameters_list

    def get_extended_response_parameters_by_method(self, sobj: SwaggerObj, endpoint: str, method: str):
        parameters_list = []
        if 'swagger' in sobj.obj and sobj.obj['swagger'] == '2.0':
            parameters_list=self.oas2.get_extended_response_parameters_by_method(sobj,endpoint,method)
        else:
            parameters_list=self.oas3.get_extended_response_parameters_by_method(sobj,endpoint,method)
        return parameters_list

    def get_definitions_references(self, sobj: SwaggerObj):
        reference_list=[]
        if 'swagger' in sobj.obj and sobj.obj['swagger'] == '2.0':
            reference_list=self.oas2.get_definitions_references(sobj)
        else:
            reference_list=self.oas3.get_definitions_references(sobj)
        return reference_list

    def get_dataset_definitions(self, sobj: SwaggerObj):
        definitions_list = []
        definitions_list=self.oas2.get_dataset_definitions(sobj)
        return definitions_list
