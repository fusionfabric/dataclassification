import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__), "..",".."))

from DataClassification.Extensions.Swaggers.SwaggerHandler import SwaggerObj
import  copy

class Oas3Classifier:
    """
                Used for classifying 3.x versions of open api specification swagger files
                param classification_header provides classification header
                """
    def __init__(self, classification_header):
        self.classification_header = classification_header

    def classify_request_parameters(self, sobj: SwaggerObj, endpoint: str, tags: list):
        sobj_new = copy.deepcopy(sobj)
        for method in sobj.obj['paths'][endpoint]:
            param_counter = 0
            if 'parameters' in sobj.obj['paths'][endpoint][method]:
                for parameter in sobj.obj['paths'][endpoint][method]['parameters']:
                    if 'name' in parameter:
                        pname = parameter['name']
                        if pname in tags:
                            sobj_new.obj['paths'][endpoint][method]['parameters'][param_counter][self.classification_header] = self.__get__parameter_tags(tags, pname)
                    param_counter += 1
        return sobj_new

    def classify_response_parameters(self, sobj: SwaggerObj, endpoint: str, tags: list):
        sobj_new = copy.deepcopy(sobj)
        covered_responses = ['200', '201','202']
        content_types=['application/json']
        for method in sobj.obj['paths'][endpoint]:
            for response_code in covered_responses:
                if response_code in sobj.obj['paths'][endpoint][method]['responses']:
                    if 'content' in sobj.obj['paths'][endpoint][method]['responses'][response_code]:
                        for contentType in sobj.obj['paths'][endpoint][method]['responses'][response_code]['content']:
                            if content_types.__contains__(contentType):
                                if 'schema' in sobj.obj['paths'][endpoint][method]['responses'][response_code]['content'][contentType]:
                                    for parameter in sobj.obj['paths'][endpoint][method]['responses'][response_code]['content'][contentType]['schema']:
                                        if parameter == 'properties':
                                            for item in (sobj.obj['paths'][endpoint][method]['responses'][response_code]['content'][contentType]['schema'][parameter]).items():
                                                    if 'type' in item[1] and item[0] in tags:
                                                        # sobj_new.obj['paths'][endpoint][method]['responses'][response_code]['schema']['properties'][self.classification_header] = self.__get__parameter_tags(tags, item[0])
                                                        sobj_new.obj['paths'][endpoint][method]['responses'][response_code]['content'][contentType]['schema'][self.classification_header] = self.__get__parameter_tags(tags, item[0])
        return sobj_new
    
    def classify_definitions(self, sobj: SwaggerObj,tags: list):
        sobj_new = copy.deepcopy(sobj)
        if 'components' in sobj.obj:
            if 'schemas' in sobj.obj['components']:
                for schema in sobj.obj['components']['schemas']:
                    if 'properties' in sobj.obj['components']['schemas'][schema]:
                        for p in sobj.obj['components']['schemas'][schema]['properties']:
                            dname = '{}/{}'.format(schema,p)
                            if dname in tags:
                                sobj_new.obj['components']['schemas'][schema]['properties'][p][self.classification_header] = self.__get__parameter_tags(tags, dname)
                    elif 'allOf' in sobj.obj['components']['schemas'][schema]:
                        list_counter = 0
                        for pobjlist in sobj.obj['components']['schemas'][schema]['allOf']: #[1]['properties']:
                            if 'properties' in sobj_new.obj['components']['schemas'][schema]['allOf'][list_counter]:
                                for p in sobj_new.obj['components']['schemas'][schema]['allOf'][list_counter]['properties']:
                                    dname = '{}/{}'.format(schema,p)
                                    if dname in tags:
                                        sobj_new.obj['components']['schemas'][schema]['allOf'][list_counter]['properties'][p][self.classification_header] = self.__get__parameter_tags(tags,dname)
                            list_counter += 1
                    elif 'anyOf' in sobj.obj['components']['schemas'][schema]:
                        list_counter = 0
                        for pobjlist in sobj.obj['components']['schemas'][schema]['anyOf']: #[1]['properties']:
                            if 'properties' in sobj_new.obj['components']['schemas'][schema]['anyOf'][list_counter]:
                                for p in sobj_new.obj['components']['schemas'][schema]['anyOf'][list_counter]['properties']:
                                    dname = '{}/{}'.format(schema,p)
                                    if dname in tags:
                                        sobj_new.obj['components']['schemas'][schema]['anyOf'][list_counter]['properties'][p][self.classification_header] = self.__get__parameter_tags(tags,dname)
                            list_counter += 1
                    elif 'oneOf' in sobj.obj['components']['schemas'][schema]:
                        list_counter = 0
                        for pobjlist in sobj.obj['components']['schemas'][schema]['oneOf']: #[1]['properties']:
                            if 'properties' in sobj_new.obj['components']['schemas'][schema]['oneOf'][list_counter]:
                                for p in sobj_new.obj['components']['schemas'][schema]['oneOf'][list_counter]['properties']:
                                    dname = '{}/{}'.format(schema,p)
                                    if dname in tags:
                                        sobj_new.obj['components']['schemas'][schema]['oneOf'][list_counter]['properties'][p][self.classification_header] = self.__get__parameter_tags(tags,dname)
                            list_counter += 1
                    elif 'items' in sobj.obj['components']['schemas'][schema]:
                        if 'properties' in sobj.obj['components']['schemas'][schema]['items']:
                            for p in sobj.obj['components']['schemas'][schema]['items']['properties']:
                                dname = '{}/{}'.format(schema,p)
                                if dname in tags:
                                        sobj_new.obj['components']['schemas'][schema]['items']['properties'][p][self.classification_header] = self.__get__parameter_tags(tags,dname)
                    elif 'description' in sobj.obj['components']['schemas'][schema] and schema in tags:
                        sobj_new.obj['components']['schemas'][schema][self.classification_header] = self.__get__parameter_tags(tags,schema)
                    elif 'title' in sobj.obj['components']['schemas'][schema] and schema in tags:
                        sobj_new.obj['components']['schemas'][schema][self.classification_header] = self.__get__parameter_tags(tags,schema)
                    elif '$ref' not in sobj.obj['components']['schemas'][schema] and schema in tags:
                        sobj_new.obj['components']['schemas'][schema][self.classification_header] = self.__get__parameter_tags(tags,schema)
        return sobj_new
    
    def classify_parameters(self, sobj: SwaggerObj, tags: list):
        sobj_new = copy.deepcopy(sobj)
        if 'components' in sobj.obj:
            if 'parameters' in sobj.obj['components']:
                for parameter in sobj.obj['components']['parameters']:
                    if parameter in tags:
                        sobj_new.obj['components']['parameters'][parameter][self.classification_header] = self.__get__parameter_tags(tags,parameter)
        return sobj_new
    

    def __get__parameter_tags(self, tags, parameter_name):
        return tags[parameter_name]
