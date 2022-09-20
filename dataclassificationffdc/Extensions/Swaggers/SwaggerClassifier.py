import sys, os, logging
sys.path.append(os.path.join(os.path.dirname(__file__), "..",".."))

from DataClassification.Extensions.Swaggers.SwaggerHandler import SwaggerObj, SwaggerHandler
from DataClassification.Extensions.Swaggers.OAS2.Oas2Classifier import Oas2Classifier
from DataClassification.Extensions.Swaggers.OAS3.Oas3Classifier import Oas3Classifier
from DataClassification.BusinessRulesEngine.ClassificationLogic import ClassificationEngine
import csv, json, copy

class SwaggerClassifier:
    """
            Works through all the swagger files by calling the different versions of swagger handlers and classifiers
            to parse params and classify them as per the rules declared by the user
            param swagger_folder_path is used to supply the location of the swagger files
            param classification_header provides the value for classification header
            param encryption_header provides the value for encryption header
            param parameter_exclusion_list provides a list for excluding certain custom swagger definitions
            param rules_file_path provides the path to the rules.json file
            param filenames provides the types of files supported
            param tags_list provides the list of tags gathered from the template file
            """

    def __init__(self, swagger_folder_path, classification_header, encryption_header, maturity_status, parameter_exclusion_list, rules_file_path,filenames,tags_list):
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(filename=swagger_folder_path + '/data-classification.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
        self.classification_header = classification_header
        self.encryption_header = encryption_header
        self.sh = SwaggerHandler(swagger_folder_path,maturity_status,parameter_exclusion_list,filenames)
        self.ce = ClassificationEngine(swagger_folder_path,rules_file_path)
        self.filenames=filenames
        self.oas2Classifier=Oas2Classifier(classification_header, encryption_header, tags_list)
        self.oas3Classifier=Oas3Classifier(classification_header)
        self.references={}
        self.tags_type_list=tags_list

    def execute(self, root_directory):
        self.__execute_json_files(root_directory)

    def classify(self, api_directory, sobj: SwaggerObj):
        if 'swagger' in self.filenames:
            sobj = self.classify_API_and_endpoints(api_directory, sobj)
            for endpoint in self.sh.get_endpoints(sobj):
                sobj = self.classify_parameters(api_directory, sobj)
                sobj = self.classify_definitions(api_directory, sobj)
                sobj = self.classify_request_parameters(api_directory, sobj, endpoint)
                sobj = self.classify_response_parameters(api_directory, sobj, endpoint)
            return sobj
        else:
            sobj=self.classify_DataSet(sobj)
            return sobj

    def __execute_json_files(self,root_directory):
        all_params = []
        logging.info("Found {} json swaggers.".format(len(self.sh.json_list)))
        print ("Found {} json swaggers.".format(len(self.sh.json_list)))
        for swagger_file in self.sh.json_list:
            try:
                api_directory = swagger_file.rsplit("/", 2)[1]
                swagger_obj = self.sh.get_json(root_directory,swagger_file)
                self.sh.write_file(self.classify(api_directory, swagger_obj))
            except BaseException as exc:
                logging.exception(exc)
                print (exc)
        logging.info("Swagger/Event files have been classified and output as Swagger-classified.json and events-classified.json files respectively")
        return all_params

    def classify_request_parameters(self, api_directory, sobj: SwaggerObj, endpoint: str):
        tags = self.__get_all_parameters_in_swagger(api_directory, sobj)
        if 'swagger' in sobj.obj and sobj.obj['swagger'] == '2.0':
            sobj_new = self.oas2Classifier.classify_request_parameters(sobj,endpoint,tags)
        else:
            sobj_new = self.oas3Classifier.classify_request_parameters(sobj,endpoint,tags)
        return sobj_new

    def classify_response_parameters(self, api_directory, sobj: SwaggerObj, endpoint: str):
        tags = self.__get_all_parameters_in_swagger(api_directory, sobj)
        if 'swagger' in sobj.obj and sobj.obj['swagger'] == '2.0':
            sobj_new = self.oas2Classifier.classify_response_parameters(sobj,endpoint,tags)
        else:
            sobj_new = self.oas3Classifier.classify_response_parameters(sobj,endpoint,tags)
        return sobj_new

    def classify_definitions(self, api_directory, sobj: SwaggerObj):
        tags = self.__get_all_parameters_in_swagger(api_directory, sobj)
        if 'swagger' in sobj.obj and sobj.obj['swagger'] == '2.0':
            sobj_new = self.oas2Classifier.classify_definitions(sobj,tags)
        else:
            sobj_new = self.oas3Classifier.classify_definitions(sobj,tags)
        return sobj_new

    def classify_parameters(self, api_directory, sobj: SwaggerObj):
        tags = self.__get_all_parameters_in_swagger(api_directory, sobj)
        if 'swagger' in sobj.obj and sobj.obj['swagger'] == '2.0':
            sobj_new = self.oas2Classifier.classify_parameters(sobj,tags)
        else:
            sobj_new = self.oas3Classifier.classify_parameters(sobj,tags)
        return sobj_new

    def classify_API_and_endpoints(self, api_directory, sobj: SwaggerObj):
        sobj_new = copy.deepcopy(sobj)
        self.references=self.sh.get_definitions_references(sobj_new)
        api_tags = []
        for endpoint in sobj.obj['paths']:
            for method in sobj.obj['paths'][endpoint]:
                endpoint_tags = self.__get_endpoint_tags(api_directory, sobj,endpoint, method)
                if len(endpoint_tags) > 0 :
                    sobj_new.obj['paths'][endpoint][method][self.classification_header] = endpoint_tags
                    api_tags += endpoint_tags
        if len(api_tags) > 0:
            sobj_new.obj['info'][self.classification_header] = list(set(api_tags))
        return sobj_new
        
    def classify_DataSet(self, sobj: SwaggerObj):
        sobj_new = copy.deepcopy(sobj)
        d = self.sh.get_dataset_definitions(sobj)
        api_directory = []
        dataset_tags = self.ce.get_tags(api_directory, d)
        tags_list = []
        for parameter in dataset_tags.keys():
            tags_list += dataset_tags[parameter]
        tags=list(set(tags_list))
        tag_handling=self._get_matching_tag_for_header(tags)
        if "tag1" in tag_handling.keys():
            if len(tag_handling["tag1"])>0:
                sobj_new.obj['info'][self.classification_header] = tag_handling["tag1"]
        if "tag2" in tag_handling.keys():
            if len(tag_handling["tag2"])>0:
                sobj_new.obj['info'][self.encryption_header] = tag_handling["tag2"]
        sobj = self.oas2Classifier.classify_datasetdefinitions(sobj_new, dataset_tags)
        return sobj

    def __get_all_parameters_in_swagger(self, api_directory, sobj: SwaggerObj):
        all_parameters = []
        for endpoint in self.sh.get_endpoints(sobj):
            parameters = self.sh.get_parameters(sobj)
            definitions = self.sh.get_definitions(sobj)
            request_parameters = self.sh.get_extended_request_parameters(sobj, endpoint)
            response_parameters = self.sh.get_extended_response_parameters(sobj,endpoint)
            all_parameters = all_parameters + parameters + definitions + request_parameters + response_parameters
        all_references = [i for i in all_parameters if '#/' in i]
        all_params_no_referencs = list(set(all_parameters) - set(all_references))
        return self.ce.get_tags(api_directory, all_params_no_referencs)

    def __get_endpoint_tags(self, api_directory, sobj: SwaggerObj, endpoint: str, method: str):
        parameters = []
        p = self.sh.get_parameters(sobj)
        d = self.sh.get_definitions(sobj)
        param_refernced = self.sh.get_parameter_references(sobj)
        request_parameters = self.sh.get_extended_request_parameters_by_method(sobj, endpoint, method)
        response_parameters = self.sh.get_extended_response_parameters_by_method(sobj,endpoint, method)
        all_params = request_parameters + response_parameters + param_refernced    
        all_referenced = p + d
        for rq in all_params:
            if '#/' in rq:
                if 'swagger' in sobj.obj and sobj.obj['swagger'] == '2.0':
                    rq_unreferenced = rq.replace('#/parameters/','').replace('#/definitions/','')
                else:
                    rq_unreferenced = rq.replace('#/parameters/','').replace('#/components/schemas/','')
                reflist=[]
                self.get_referenced_params(rq_unreferenced,reflist)
                if rq_unreferenced in all_referenced:
                    parameters.append(rq_unreferenced)
                else:
                    rq_unreferenced += '/'
                    ref_params = [i for i in all_referenced if i.startswith(rq_unreferenced)] 
                    parameters += ref_params

                ref_params =[]
                for item in reflist:
                    if item in all_referenced:
                         parameters.append(item)
                    else:
                        ref_params += [i for i in all_referenced if i.startswith(item+'/')] 
                        parameters += ref_params
            else:
                parameters.append(rq)
      
       
        endpoint_tags = self.ce.get_tags(api_directory, parameters)
        tags_list = []
        for parameter in endpoint_tags.keys():
            tags_list += endpoint_tags[parameter]
        return list(set(tags_list))

    def get_referenced_params(self, definition: str,reflist:[]):
        if definition in self.references:
            refitems=self.references[definition]
            for item in refitems:
                if item.startswith('#/definitions/'):
                    rq_unreferenced = item.replace('#/definitions/','')
                    if rq_unreferenced != definition:
                        reflist.append(rq_unreferenced)
                        self.get_referenced_params(rq_unreferenced,reflist)
                elif item.startswith('#/components/schemas/'):
                    rq_unreferenced = item.replace('#/components/schemas/','')
                    if rq_unreferenced != definition:
                        reflist.append(rq_unreferenced)
                        self.get_referenced_params(rq_unreferenced,reflist)
    def _get_matching_tag_for_header(self,tags):
        tags_by_type={}
        for tag_name in tags:
            if tag_name in self.tags_type_list["tag1"]:
                if "tag1" not in  tags_by_type.keys():
                    tags_by_type["tag1"]=[]
                    tags_by_type["tag1"].append(tag_name)
                else:
                    tags_by_type["tag1"].append(tag_name)
            if "tag2" in self.tags_type_list and tag_name in self.tags_type_list["tag2"]:
                if "tag2" not in  tags_by_type.keys():
                    tags_by_type["tag2"]=[]
                    tags_by_type["tag2"].append(tag_name)
                else:
                    tags_by_type["tag2"].append(tag_name)
        return tags_by_type
            
        
