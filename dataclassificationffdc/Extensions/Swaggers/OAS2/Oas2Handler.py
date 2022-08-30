import sys,os, json, copy
from os.path import join, getsize
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from DataClassification.Extensions.Swaggers.SwaggerObj import SwaggerObj

class Oas2Handler:
    """
                Used for parsing definitions from 2.x versions of open api specification swagger files
                """
    def __init__(self,parameter_descriptions=[],parameter_exclusion_list=[]):
        self.parameter_descriptions=parameter_descriptions
        self.parameter_exclusion_list=parameter_exclusion_list

    def get_request_parameters1(self, sobj: SwaggerObj, endpoint: str):
        parameters_list = {}
        for method in sobj.obj['paths'][endpoint]:
            parameters_list[method] = []
            for parameter in sobj.obj['paths'][endpoint][method]['parameters']:
                if '$ref' in parameter :
                    parameters_list[method].append(parameter['$ref'])
                elif 'name' in parameter:
                    parameters_list[method].append(parameter['name'])
        return parameters_list

    def get_response_parameters1(self, sobj: SwaggerObj, endpoint: str):
        parameters_list = {}
        covered_responses = ['200', '201','202']
        for method in sobj.obj['paths'][endpoint]:
                parameters_list[method] = []
                for response_code in covered_responses:
                    if response_code in sobj.obj['paths'][endpoint][method]['responses']:
                        for parameter in sobj.obj['paths'][endpoint][method]['responses'][response_code]['schema']:
                            if parameter == 'properties':
                                for item in (sobj.obj['paths'][endpoint][method]['responses'][response_code]['schema']['properties']).items():
                                        if 'items' in item[1]:
                                            if '$ref' in item[1]['items']:
                                                parameters_list[method].append(item[1]['items']['$ref'])
                                        elif 'type' in item[1]:
                                            parameters_list[method].append(item[0])
                                        else:
                                            print('Hnhandled response parameter in file {} and endpoint {}: {}',format(sobj.shortPath, endpoint, item))
                            elif parameter == 'items':
                                for item in (sobj.obj['paths'][endpoint][method]['responses'][response_code]['schema']['items']).items():
                                        if item[0] == '$ref':
                                            parameters_list[method].append(item[1])
                            elif parameter == '$ref':
                                parameters_list[method].append(sobj.obj['paths'][endpoint][method]['responses'][response_code]['schema']['$ref'])
        return parameters_list
        
    def get_definitions(self, sobj: SwaggerObj):
        definitions_list = []
        if 'definitions' in sobj.obj:
            for definition in sobj.obj['definitions']:
                if 'properties' in sobj.obj['definitions'][definition]:
                    for p in sobj.obj['definitions'][definition]['properties']:
                        dname = '{}/{}'.format(definition,p)
                        #definitions_list.append(dname)
                        if 'items' in sobj.obj['definitions'][definition]['properties'][p]:
                            if '$ref' not in sobj.obj['definitions'][definition]['properties'][p]['items']:
                                if '$ref' not in sobj.obj['definitions'][definition]['properties'][p]:
                                    definitions_list.append(dname)
                                    if dname not in self.parameter_descriptions.keys():
                                        self.parameter_descriptions[dname] = []
                                    if {"file": sobj.shortPath, "description" : sobj.obj['definitions'][definition]['properties'][p]["description"]} not in self.parameter_descriptions[dname]:
                                        self.parameter_descriptions[dname].append({"file": sobj.shortPath, "description" : sobj.obj['definitions'][definition]['properties'][p]["description"]})
                        elif 'description' in sobj.obj['definitions'][definition]['properties'][p]:
                            if '$ref' not in sobj.obj['definitions'][definition]['properties'][p]:
                                definitions_list.append(dname)
                                if dname not in self.parameter_descriptions.keys():
                                    self.parameter_descriptions[dname] = []
                                if {"file": sobj.shortPath, "description" : sobj.obj['definitions'][definition]['properties'][p]["description"]} not in self.parameter_descriptions[dname]:
                                    self.parameter_descriptions[dname].append({"file": sobj.shortPath, "description" : sobj.obj['definitions'][definition]['properties'][p]["description"]})
                        elif 'title' in sobj.obj['definitions'][definition]['properties'][p]:
                            if '$ref' not in sobj.obj['definitions'][definition]['properties'][p]:
                                definitions_list.append(dname)
                                if dname not in self.parameter_descriptions.keys():
                                    self.parameter_descriptions[dname] = []
                                if {"file": sobj.shortPath, "description" : sobj.obj['definitions'][definition]['properties'][p]["title"]} not in self.parameter_descriptions[dname]:
                                    self.parameter_descriptions[dname].append({"file": sobj.shortPath, "description" : sobj.obj['definitions'][definition]['properties'][p]["title"]})
                        elif '$ref' not in sobj.obj['definitions'][definition]['properties'][p]:
                            definitions_list.append(dname)
                            if dname not in self.parameter_descriptions.keys():
                                self.parameter_descriptions[dname] = []
                            if {"file": sobj.shortPath, "description" : p} not in self.parameter_descriptions[dname]:
                                self.parameter_descriptions[dname].append({"file": sobj.shortPath, "description" : p})
                    # elif 'enum' in sobj.obj['definitions'][definition]:
                    #         definitions_list.append(definition)
                elif 'allOf' in sobj.obj['definitions'][definition]:
                    for pobjlist in sobj.obj['definitions'][definition]['allOf']: #[1]['properties']:
                        for pobj in pobjlist:
                            if 'properties' in pobj:
                                for p in pobjlist['properties']:
                                    dname = '{}/{}'.format(definition,p)
                                  
                                    if 'items' in pobjlist['properties'][p]:
                                        definitions_list.append(dname)
                                        for item in pobjlist['properties'][p]['items']:
                                            if '$ref' not in item:
                                                raise ValueError('An issue occured with the structure of file {} and definition in item {}'.format(sobj.shortPath,item))
                                    elif 'description' in pobjlist['properties'][p]:
                                        if '$ref' not in pobjlist['properties'][p]:
                                            definitions_list.append(dname)
                                            if dname not in self.parameter_descriptions.keys():
                                                self.parameter_descriptions[dname] = []
                                            if {"file": sobj.shortPath, "description" : pobjlist['properties'][p]['description']} not in self.parameter_descriptions[dname]:
                                                self.parameter_descriptions[dname].append({"file": sobj.shortPath, "description" : pobjlist['properties'][p]['description']})
                                    elif 'title' in pobjlist['properties'][p]:
                                        if '$ref' not in pobjlist['properties'][p]:
                                            definitions_list.append(dname)
                                            if dname not in self.parameter_descriptions.keys():
                                                self.parameter_descriptions[dname] = []
                                            if {"file": sobj.shortPath, "description" : pobjlist['properties'][p]['title']} not in self.parameter_descriptions[dname]:
                                                self.parameter_descriptions[dname].append({"file": sobj.shortPath, "description" : pobjlist['properties'][p]['title']})
                                    elif '$ref' not in pobjlist['properties'][p]:
                                        definitions_list.append(dname)
                                        if dname not in self.parameter_descriptions.keys():
                                            self.parameter_descriptions[dname] = []
                                        if {"file": sobj.shortPath, "description" : p} not in self.parameter_descriptions[dname]:
                                            self.parameter_descriptions[dname].append({"file": sobj.shortPath, "description" : p})
                elif 'items' in sobj.obj['definitions'][definition]:
                    if 'properties' in sobj.obj['definitions'][definition]['items']:
                        for p in sobj.obj['definitions'][definition]['items']['properties']:
                            dname = '{}/{}'.format(definition,p)
                            if 'description' in sobj.obj['definitions'][definition]['items']['properties'][p]:
                                if '$ref' not in sobj.obj['definitions'][definition]['items']['properties'][p]:
                                    definitions_list.append(dname)
                                    if dname not in self.parameter_descriptions.keys():
                                        self.parameter_descriptions[dname] = []
                                    if {"file": sobj.shortPath, "description" : sobj.obj['definitions'][definition]['items']['properties'][p]["description"]} not in self.parameter_descriptions[dname]:
                                        self.parameter_descriptions[dname].append({"file": sobj.shortPath, "description" : sobj.obj['definitions'][definition]['items']['properties'][p]["description"]})
                            elif 'title' in sobj.obj['definitions'][definition]['items']['properties'][p]:
                                if '$ref' not in sobj.obj['definitions'][definition]['items']['properties'][p]:
                                    definitions_list.append(dname)
                                    if dname not in self.parameter_descriptions.keys():
                                        self.parameter_descriptions[dname] = []
                                    if {"file": sobj.shortPath, "description" : sobj.obj['definitions'][definition]['items']['properties'][p]["title"]} not in self.parameter_descriptions[dname]:
                                        self.parameter_descriptions[dname].append({"file": sobj.shortPath, "description" : sobj.obj['definitions'][definition]['items']['properties'][p]["title"]})
                            elif '$ref' not in sobj.obj['definitions'][definition]['items']['properties'][p]:
                                definitions_list.append(dname)
                                if dname not in self.parameter_descriptions.keys():
                                    self.parameter_descriptions[dname] = []
                                if {"file": sobj.shortPath, "description" : p} not in self.parameter_descriptions[dname]:
                                    self.parameter_descriptions[dname].append({"file": sobj.shortPath, "description" : p})
                elif 'description' in sobj.obj['definitions'][definition]:
                    if '$ref' not in sobj.obj['definitions'][definition]:
                        definitions_list.append(definition)
                        if definition not in self.parameter_descriptions.keys():
                            self.parameter_descriptions[definition] = []
                        if {"file": sobj.shortPath, "description" : sobj.obj['definitions'][definition]['description']} not in self.parameter_descriptions[definition]:
                            self.parameter_descriptions[definition].append({"file": sobj.shortPath, "description" : sobj.obj['definitions'][definition]['description']})
                elif 'title' in sobj.obj['definitions'][definition]:
                    if '$ref' not in sobj.obj['definitions'][definition]:
                        definitions_list.append(definition)
                        if definition not in self.parameter_descriptions.keys():
                            self.parameter_descriptions[definition] = []
                        if {"file": sobj.shortPath, "description" : sobj.obj['definitions'][definition]['title']} not in self.parameter_descriptions[definition]:
                            self.parameter_descriptions[definition].append({"file": sobj.shortPath, "description" : sobj.obj['definitions'][definition]['title']})
                elif 'additionalProperties' in sobj.obj['definitions'][definition]:
                    for ap in sobj.obj['definitions'][definition]['additionalProperties']:
                        if '$ref' not in ap:
                            raise ValueError ("Unhandled 'addiotnal property' in definition name {} in file {}".format(ap, sobj.shortPath))
                elif 'pattern' in sobj.obj['definitions'][definition] and 'type' in sobj.obj['definitions'][definition]:
                    raise ValueError ("No description for the definition name {} in file {}".format(definition, sobj.shortPath))
                elif '$ref' not in sobj.obj['definitions'][definition]:
                    definitions_list.append(definition)
                    if definition not in self.parameter_descriptions.keys():
                        self.parameter_descriptions[definition] = []
                    if {"file": sobj.shortPath, "description" : definition} not in self.parameter_descriptions[definition]:
                        self.parameter_descriptions[definition].append({"file": sobj.shortPath, "description" : definition})
                else:
                    print ("Unparsable definition {} in file {}".format(definition, sobj.shortPath))
        return definitions_list

    def get_parameters(self, sobj: SwaggerObj):
        parameters = []
        if 'parameters' in sobj.obj:
            for parameter in sobj.obj['parameters']:
                if parameter not in self.parameter_exclusion_list:
                    parameters.append(parameter)
                    if parameter not in self.parameter_descriptions.keys():
                        self.parameter_descriptions[parameter] = []
                    if "description" in sobj.obj['parameters'][parameter]:
                        if {"file": sobj.shortPath, "description" : sobj.obj['parameters'][parameter]["description"]} not in self.parameter_descriptions[parameter]:
                            self.parameter_descriptions[parameter].append({"file": sobj.shortPath, "description" : sobj.obj['parameters'][parameter]["description"]})
                    else:
                        if {"file": sobj.shortPath, "description" : parameter} not in self.parameter_descriptions[parameter]:
                            self.parameter_descriptions[parameter].append({"file": sobj.shortPath, "description" : parameter})
        return parameters
        
    def get_parameter_references(self, sobj: SwaggerObj):
        parameters = []
        if 'parameters' in sobj.obj:
            for parameter in sobj.obj['parameters']:
                if 'schema' in sobj.obj['parameters'][parameter]:
                    if '$ref' in sobj.obj['parameters'][parameter]['schema']:
                            parameters.append(sobj.obj['parameters'][parameter]['schema']['$ref'])
        return parameters

    def get_extended_request_parameters(self, sobj: SwaggerObj, endpoint: str):
            parameters_list = []
            for method in sobj.obj['paths'][endpoint]:
                parameters_list += self.get_extended_request_parameters_by_method(sobj, endpoint, method)
            return parameters_list

    def get_extended_request_parameters_by_method(self, sobj: SwaggerObj, endpoint: str, method: str):
            parameters_list = []
            if 'parameters' in sobj.obj['paths'][endpoint][method]:
                for parameter in sobj.obj['paths'][endpoint][method]['parameters']:
                    if '$ref' in parameter :
                        parameters_list.append(parameter['$ref'])
                    elif 'name' in parameter and 'schema' not in parameter:
                        pname = parameter['name']
                        parameters_list.append(pname)
                        if pname not in self.parameter_descriptions.keys():
                            self.parameter_descriptions[pname] = []
                        if "description" in parameter:
                            if {"file": sobj.shortPath, "endpoint": endpoint, "description" : parameter['description']} not in self.parameter_descriptions[pname]:
                                self.parameter_descriptions[pname].append({"file": sobj.shortPath, "endpoint": endpoint, "description" : parameter['description']})
                        else:
                            if {"file": sobj.shortPath, "endpoint": endpoint, "description" : pname} not in self.parameter_descriptions[pname]:
                                self.parameter_descriptions[pname].append({"file": sobj.shortPath, "endpoint": endpoint, "description" : pname})
                    elif 'schema' in parameter:
                        if '$ref' in parameter['schema']:
                            item=parameter['schema']['$ref']
                            parameters_list.append(item)
            return parameters_list

    def get_extended_response_parameters(self, sobj: SwaggerObj, endpoint: str):
        parameters_list = []
        for method in sobj.obj['paths'][endpoint]:
            parameters_list += self.get_extended_response_parameters_by_method(sobj,endpoint, method )
        return parameters_list

    def get_extended_response_parameters_by_method(self, sobj: SwaggerObj, endpoint: str, method: str):
        parameters_list = []
        covered_responses = ['200', '201','202']
        try:
            for int_response_code in covered_responses:
                if int_response_code in sobj.obj['paths'][endpoint][method]['responses']:
                    response_code = int_response_code
                else:
                    response_code = str(int_response_code)
                if response_code in sobj.obj['paths'][endpoint][method]['responses']:
                    if 'schema' in sobj.obj['paths'][endpoint][method]['responses'][response_code]:
                        for parameter in sobj.obj['paths'][endpoint][method]['responses'][response_code]['schema']:
                            if parameter == 'properties':
                                for item in (sobj.obj['paths'][endpoint][method]['responses'][response_code]['schema']['properties']).items():
                                        if 'items' in item[1]:
                                            if '$ref' in item[1]['items']:
                                                parameters_list.append(item[1]['items']['$ref'])
                                        elif 'type' in item[1]:
                                            pname = item[0]
                                            parameters_list.append(pname)
                                            if pname not in self.parameter_descriptions.keys():
                                                self.parameter_descriptions[pname] = []
                                            if {"file": sobj.shortPath, "endpoint": endpoint, "description" : item[1]["description"]} not in self.parameter_descriptions[pname]:
                                                self.parameter_descriptions[pname].append({"file": sobj.shortPath, "endpoint": endpoint, "description" : item[1]["description"]})
                            elif parameter == 'items':
                                for item in (sobj.obj['paths'][endpoint][method]['responses'][response_code]['schema']['items']).items():
                                        if item[0] == '$ref':
                                            parameters_list.append(item[1])
                            elif parameter == '$ref':
                                parameters_list.append(sobj.obj['paths'][endpoint][method]['responses'][response_code]['schema']['$ref'])
                            elif parameter == 'type':
                                isfile=sobj.obj['paths'][endpoint][method]['responses'][response_code]['schema']['type']
                                if isfile=='file':
                                    if 'file' not in self.parameter_descriptions.keys():
                                        self.parameter_descriptions['file'] = []
                                        if {"file": sobj.shortPath, "endpoint": endpoint, "description" : 'file'} not in self.parameter_descriptions['file']:
                                            self.parameter_descriptions['file'].append({"file": sobj.shortPath, "endpoint": endpoint, "description" : 'file'})
                                    parameters_list.append(sobj.obj['paths'][endpoint][method]['responses'][response_code]['schema']['type'])
                    elif "$ref" in sobj.obj['paths'][endpoint][method]['responses'][response_code]:
                        ref=sobj.obj['paths'][endpoint][method]['responses'][response_code]["$ref"]
                        items=ref.split('/')
                        if len(items)>1:
                            responses=items[1]
                            response_schema=items[2]
                            if responses in sobj.obj:
                                if response_schema in sobj.obj[responses]:
                                    if 'schema' in sobj.obj[responses][response_schema]:
                                        if '$ref' in sobj.obj[responses][response_schema]['schema']:
                                            parameters_list.append(sobj.obj[responses][response_schema]['schema']['$ref'])
                    elif 'content' in sobj.obj['paths'][endpoint][method]['responses'][response_code]:
                        parameters_list.append(sobj.obj['paths'][endpoint][method]['responses'][response_code]['content']['application/json']['schema']['$ref'])
        except:
            raise ValueError('An issue occured with the structure of file {} and endpoint {}'.format(sobj.shortPath, endpoint))
        return parameters_list

    def get_definitions_references(self, sobj: SwaggerObj):
        definitionsref={}
        try:
            if 'definitions' in sobj.obj:
                for definition in sobj.obj['definitions']:
                    definitionsref[definition]=[]
                    if 'properties' in sobj.obj['definitions'][definition]:
                        for p in sobj.obj['definitions'][definition]['properties']:
                            definitionsref[definition].append(p)
                            if '$ref' in sobj.obj['definitions'][definition]['properties'][p]:
                                definitionsref[definition].append(sobj.obj['definitions'][definition]['properties'][p]['$ref'])
                            if 'items' in sobj.obj['definitions'][definition]['properties'][p]:
                                if '$ref' in  sobj.obj['definitions'][definition]['properties'][p]['items']:
                                    definitionsref[definition].append(sobj.obj['definitions'][definition]['properties'][p]['items']['$ref'])
                    elif 'allOf' in sobj.obj['definitions'][definition]:
                        for pobjlist in sobj.obj['definitions'][definition]['allOf']: #[1]['properties']:
                            for pobj in pobjlist:
                                if 'properties' in pobj:
                                    for p in pobjlist['properties']:
                                        definitionsref[definition].append(p)
                                        if 'items' in pobjlist['properties'][p]:
                                            for item in pobjlist['properties'][p]['items']:
                                                if '$ref' in item:
                                                    definitionsref[definition].append(pobjlist['properties'][p]['items']['$ref'])
                                        elif '$ref' in  pobjlist['properties'][p]:
                                            definitionsref[definition].append(pobjlist['properties'][p]['$ref'])
                                elif '$ref' in pobj:
                                    definitionsref[definition].append(pobjlist['$ref'])
                    elif 'additionalProperties' in sobj.obj['definitions'][definition]:
                        for ap in sobj.obj['definitions'][definition]['additionalProperties']:
                            if '$ref' in ap:
                                definitionsref[definition].append(sobj.obj['definitions'][definition]['additionalProperties']['$ref'])
                    elif 'items' in sobj.obj['definitions'][definition] and 'title' in sobj.obj['definitions'][definition]:
                        for i in sobj.obj['definitions'][definition]['items']:
                            if '$ref' in i:
                                definitionsref[definition].append(sobj.obj['definitions'][definition]['items']['$ref'])
                            elif 'properties' in i:
                                for p in sobj.obj['definitions'][definition]['items']['properties']:
                                    if '$ref' in sobj.obj['definitions'][definition]['items']['properties'][p]:
                                        definitionsref[definition].append(sobj.obj['definitions'][definition]['items']['properties'][p]['$ref'])
        except ValueError  as exc:
            raise exc
        return definitionsref

    def get_dataset_definitions(self, sobj: SwaggerObj):
        definitions_list = []
        if 'definitions' in sobj.obj:
            for definition in sobj.obj['definitions']:
                sobj_new = copy.deepcopy(sobj.obj['definitions'][definition])
                self.get_dataset_properties(definition,sobj_new,definitions_list,sobj.shortPath,False)
        return definitions_list

    def get_dataset_properties(self, definition: str,sobj: SwaggerObj,  definitions_list:[],path:str,hasParent:bool):
        if 'properties' in sobj:
            for p in sobj['properties']:
                if definition:
                    dname = '{}/{}'.format(definition,p)
                else:
                    dname = '{}'.format(p)
                if 'description' in sobj['properties'][p]:
                    if '$ref' not in sobj['properties'][p] and 'properties' not in sobj['properties'][p]:
                        definitions_list.append(dname)
                        if dname not in self.parameter_descriptions.keys():
                            self.parameter_descriptions[dname] = []
                        if {"file": path, "description" : sobj['properties'][p]["description"]} not in self.parameter_descriptions[dname]:
                            self.parameter_descriptions[dname].append({"file": path, "description" : sobj['properties'][p]["description"]})
                elif 'title' in sobj['properties'][p]:
                    if '$ref' not in sobj['properties'][p] and 'properties' not in sobj['properties'][p]:
                        definitions_list.append(dname)
                        if dname not in self.parameter_descriptions.keys():
                            self.parameter_descriptions[dname] = []
                        if {"file": path, "description" : sobj['properties'][p]["title"]} not in self.parameter_descriptions[dname]:
                            self.parameter_descriptions[dname].append({"file": path, "description" : sobj['properties'][p]["title"]})
                else:
                    if '$ref' not in sobj['properties'][p] and 'properties' not in sobj['properties'][p]:
                        definitions_list.append(dname)
                        if dname not in self.parameter_descriptions.keys():
                            self.parameter_descriptions[dname] = []
                        if {"file": path, "description" : p} not in self.parameter_descriptions[dname]:
                            self.parameter_descriptions[dname].append({"file": path, "description" : p})
                self.get_dataset_properties(p,sobj['properties'][p],definitions_list,path,True)
        elif 'items' in sobj:
            for item in sobj['items']:
                if 'properties' in item:
                    for p in sobj['items']['properties']:
                        if definition:
                            dname = '{}/{}'.format(definition,p)
                        else:
                            dname = '{}'.format(p)
                        if 'description' in sobj['items']['properties'][p]:
                            if '$ref' not in sobj['items']['properties'][p] and 'properties' not in sobj['items']['properties'][p] and 'items' not in sobj['items']['properties'][p]:
                                definitions_list.append(dname)
                                if dname not in self.parameter_descriptions.keys():
                                    self.parameter_descriptions[dname] = []
                                if {"file": path, "description" : sobj['items']['properties'][p]["description"]} not in self.parameter_descriptions[dname]:
                                    self.parameter_descriptions[dname].append({"file": path, "description" : sobj['items']['properties'][p]["description"]})
                        elif 'title' in sobj[definition]['properties'][p]:
                            if '$ref' not in sobj['items']['properties'][p] and 'properties' not in sobj['items']['properties'][p] and 'items' not in sobj['items']['properties'][p]:
                                definitions_list.append(dname)
                                if dname not in self.parameter_descriptions.keys():
                                    self.parameter_descriptions[dname] = []
                                if {"file": path, "description" : sobj['items']['properties'][p]["title"]} not in self.parameter_descriptions[dname]:
                                    self.parameter_descriptions[dname].append({"file": path, "description" : sobj['items']['properties'][p]["title"]})
                        else:
                            if '$ref' not in sobj['items']['properties'][p] and 'properties' not in sobj['items']['properties'][p] and 'items' not in sobj['items']['properties'][p]:
                                definitions_list.append(dname)
                                if dname not in self.parameter_descriptions.keys():
                                    self.parameter_descriptions[dname] = []
                                if {"file": path, "description" : p} not in self.parameter_descriptions[dname]:
                                    self.parameter_descriptions[dname].append({"file": path, "description" : p})
                        self.get_dataset_properties(p,sobj['items']['properties'][p],definitions_list,path,True)
        else:
            if hasParent is False:
                dname = '{}'.format(definition)    
                if 'description' in sobj:
                    if '$ref' not in sobj and 'properties' not in sobj:
                        definitions_list.append(dname)
                        if dname not in self.parameter_descriptions.keys():
                            self.parameter_descriptions[dname] = []
                        if {"file": path, "description" : sobj["description"]} not in self.parameter_descriptions[dname]:
                            self.parameter_descriptions[dname].append({"file": path, "description" : sobj["description"]})
                elif 'title' in sobj:
                    if '$ref' not in sobj and 'properties' not in sobj:
                        definitions_list.append(dname)
                        if dname not in self.parameter_descriptions.keys():
                            self.parameter_descriptions[dname] = []
                        if {"file": path, "description" : sobj["title"]} not in self.parameter_descriptions[dname]:
                            self.parameter_descriptions[dname].append({"file": path, "description" : sobj["title"]})
                else:
                    if '$ref' not in sobj and 'properties' not in sobj:
                        definitions_list.append(dname)
                        if dname not in self.parameter_descriptions.keys():
                            self.parameter_descriptions[dname] = []
                        if {"file": path, "description" : p} not in self.parameter_descriptions[dname]:
                            self.parameter_descriptions[dname].append({"file": path, "description" : p})



   
