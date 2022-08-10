import sys,os,json
from os.path import join, getsize
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from DataClassification.Extensions.Swaggers.SwaggerObj import SwaggerObj

class Oas3Handler:
    """
                Used for parsing definitions from 3.x versions of open api specification swagger files
                param parameter_descriptions provide descriptions for the parsed out swagger definitions
                param parameter_exclusion_list provides a list of params to excluded from parsing process
                """
    content_types=['application/json']
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
                        if 'content' in sobj.obj['paths'][endpoint][method]['responses'][response_code]:
                            for contentType in sobj.obj['paths'][endpoint][method]['responses'][response_code]['content']:
                                # if self.content_types.__contains__(contentType):
                                if 'schema' in sobj.obj['paths'][endpoint][method]['responses'][response_code]['content'][contentType]:
                                    for parameter in sobj.obj['paths'][endpoint][method]['responses'][response_code]['content'][contentType]['schema']:
                                        if parameter == 'properties':
                                            for item in (sobj.obj['paths'][endpoint][method]['responses'][response_code]['content'][contentType]['schema']['properties']).items():
                                                    if 'items' in item[1]:
                                                        if '$ref' in item[1]['items']:
                                                            parameters_list[method].append(item[1]['items']['$ref'])
                                                    elif 'type' in item[1]:
                                                        parameters_list[method].append(item[0])
                                                    else:
                                                        print('Hnhandled response parameter in file {} and endpoint {}: {}',format(sobj.shortPath, endpoint, item))
                                        elif parameter == 'items':
                                            for item in (sobj.obj['paths'][endpoint][method]['responses'][response_code]['content'][contentType]['schema']['items']).items():
                                                    if item[0] == '$ref':
                                                        parameters_list[method].append(item[1])
                                        elif parameter == '$ref':
                                            parameters_list[method].append(sobj.obj['paths'][endpoint][method]['responses'][response_code]['content'][contentType]['schema']['$ref'])
        return parameters_list
        
    def get_definitions(self, sobj: SwaggerObj):
        definitions_list = []
        if 'components' in sobj.obj:
            for schema in sobj.obj['components']['schemas']:
                if 'properties' in sobj.obj['components']['schemas'][schema]:
                    for p in sobj.obj['components']['schemas'][schema]['properties']:
                        dname = '{}/{}'.format(schema,p)
                        #definitions_list.append(dname)
                        if 'items' in sobj.obj['components']['schemas'][schema]['properties'][p]:
                            if '$ref' not in sobj.obj['components']['schemas'][schema]['properties'][p]['items']:
                                if '$ref' not in sobj.obj['components']['schemas'][schema]['properties'][p]:
                                    definitions_list.append(dname)
                                    if dname not in self.parameter_descriptions.keys():
                                        self.parameter_descriptions[dname] = []
                                    if {"file": sobj.shortPath, "description" : sobj.obj['components']['schemas'][schema]['properties'][p]["description"]} not in self.parameter_descriptions[dname]:
                                        self.parameter_descriptions[dname].append({"file": sobj.shortPath, "description" : sobj.obj['components']['schemas'][schema]['properties'][p]["description"]})
                        elif 'description' in sobj.obj['components']['schemas'][schema]['properties'][p]:
                            if '$ref' not in sobj.obj['components']['schemas'][schema]['properties'][p]:
                                definitions_list.append(dname)
                                if dname not in self.parameter_descriptions.keys():
                                    self.parameter_descriptions[dname] = []
                                if {"file": sobj.shortPath, "description" : sobj.obj['components']['schemas'][schema]['properties'][p]["description"]} not in self.parameter_descriptions[dname]:
                                    self.parameter_descriptions[dname].append({"file": sobj.shortPath, "description" : sobj.obj['components']['schemas'][schema]['properties'][p]["description"]})
                        elif 'title' in sobj.obj['components']['schemas'][schema]['properties'][p]:
                            if '$ref' not in sobj.obj['components']['schemas'][schema]['properties'][p]:
                                definitions_list.append(dname)
                                if dname not in self.parameter_descriptions.keys():
                                    self.parameter_descriptions[dname] = []
                                if {"file": sobj.shortPath, "description" : sobj.obj['components']['schemas'][schema]['properties'][p]["title"]} not in self.parameter_descriptions[dname]:
                                    self.parameter_descriptions[dname].append({"file": sobj.shortPath, "description" : sobj.obj['components']['schemas'][schema]['properties'][p]["title"]})
                        elif '$ref' not in sobj.obj['components']['schemas'][schema]['properties'][p]:
                            definitions_list.append(dname)
                            if dname not in self.parameter_descriptions.keys():
                                self.parameter_descriptions[dname] = []
                            if {"file": sobj.shortPath, "description" : p} not in self.parameter_descriptions[dname]:
                                self.parameter_descriptions[dname].append({"file": sobj.shortPath, "description" : p})
                elif 'enum' in sobj.obj['components']['schemas'][schema]:
                        dname = '{}/{}'.format(schema,'enum')
                        definitions_list.append(dname)
                elif 'allOf' in sobj.obj['components']['schemas'][schema]:
                    for pobjlist in sobj.obj['components']['schemas'][schema]['allOf']: #[1]['properties']:
                        for pobj in pobjlist:
                            if 'properties' in pobj:
                                for p in pobjlist['properties']:
                                    dname = '{}/{}'.format(schema,p)
                                    definitions_list.append(dname)
                                    if 'items' in pobjlist['properties'][p]:
                                        for item in pobjlist['properties'][p]['items']:
                                            if '$ref' not in item:
                                                raise ValueError('An issue occured with the structure of file {} and definition in item {}'.format(sobj.shortPath,item))
                                    elif 'description' in pobjlist['properties'][p]:
                                        if dname not in self.parameter_descriptions.keys():
                                            self.parameter_descriptions[dname] = []
                                        if {"file": sobj.shortPath, "description" : pobjlist['properties'][p]['description']} not in self.parameter_descriptions[dname]:
                                            self.parameter_descriptions[dname].append({"file": sobj.shortPath, "description" : pobjlist['properties'][p]['description']})
                                    elif 'title' in pobjlist['properties'][p]:
                                        if dname not in self.parameter_descriptions.keys():
                                            self.parameter_descriptions[dname] = []
                                        if {"file": sobj.shortPath, "description" : pobjlist['properties'][p]['title']} not in self.parameter_descriptions[dname]:
                                            self.parameter_descriptions[dname].append({"file": sobj.shortPath, "description" : pobjlist['properties'][p]['title']})
                                    elif '$ref' not in  pobjlist['properties'][p]:
                                        if dname not in self.parameter_descriptions.keys():
                                            self.parameter_descriptions[dname] = []
                                        if {"file": sobj.shortPath, "description" : p} not in self.parameter_descriptions[dname]:
                                            self.parameter_descriptions[dname].append({"file": sobj.shortPath, "description" : p})
                elif 'anyOf' in sobj.obj['components']['schemas'][schema]:
                    for pobjlist in sobj.obj['components']['schemas'][schema]['anyOf']: #[1]['properties']:
                        for pobj in pobjlist:
                            if 'properties' in pobj:
                                for p in pobjlist['properties']:
                                    dname = '{}/{}'.format(schema,p)
                                    definitions_list.append(dname)
                                    if 'items' in pobjlist['properties'][p]:
                                        for item in pobjlist['properties'][p]['items']:
                                            if '$ref' not in item:
                                                raise ValueError('An issue occured with the structure of file {} and definition in item {}'.format(sobj.path,item))
                                    elif 'description' in pobjlist['properties'][p]:
                                        if dname not in self.parameter_descriptions.keys():
                                            self.parameter_descriptions[dname] = []
                                        if {"file": sobj.shortPath, "description" : pobjlist['properties'][p]['description']} not in self.parameter_descriptions[dname]:
                                            self.parameter_descriptions[dname].append({"file": sobj.shortPath, "description" : pobjlist['properties'][p]['description']})
                                    elif 'title' in pobjlist['properties'][p]:
                                        if dname not in self.parameter_descriptions.keys():
                                            self.parameter_descriptions[dname] = []
                                        if {"file": sobj.shortPath, "description" : pobjlist['properties'][p]['title']} not in self.parameter_descriptions[dname]:
                                            self.parameter_descriptions[dname].append({"file": sobj.shortPath, "description" : pobjlist['properties'][p]['title']})
                                    elif '$ref' not in  pobjlist['properties'][p]:
                                        if dname not in self.parameter_descriptions.keys():
                                            self.parameter_descriptions[dname] = []
                                        if {"file": sobj.shortPath, "description" : p} not in self.parameter_descriptions[dname]:
                                            self.parameter_descriptions[dname].append({"file": sobj.shortPath, "description" : p})
                elif 'oneOf' in sobj.obj['components']['schemas'][schema]:
                    for pobjlist in sobj.obj['components']['schemas'][schema]['oneOf']: #[1]['properties']:
                        for pobj in pobjlist:
                            if 'properties' in pobj:
                                for p in pobjlist['properties']:
                                    dname = '{}/{}'.format(schema,p)
                                    definitions_list.append(dname)
                                    if 'items' in pobjlist['properties'][p]:
                                        for item in pobjlist['properties'][p]['items']:
                                            if '$ref' not in item:
                                                raise ValueError('An issue occured with the structure of file {} and definition in item {}'.format(sobj.path,item))
                                    elif 'description' in pobjlist['properties'][p]:
                                        if dname not in self.parameter_descriptions.keys():
                                            self.parameter_descriptions[dname] = []
                                        if {"file": sobj.shortPath, "description" : pobjlist['properties'][p]['description']} not in self.parameter_descriptions[dname]:
                                            self.parameter_descriptions[dname].append({"file": sobj.shortPath, "description" : pobjlist['properties'][p]['description']})
                                    elif 'title' in pobjlist['properties'][p]:
                                        if dname not in self.parameter_descriptions.keys():
                                            self.parameter_descriptions[dname] = []
                                        if {"file": sobj.shortPath, "description" : pobjlist['properties'][p]['title']} not in self.parameter_descriptions[dname]:
                                            self.parameter_descriptions[dname].append({"file": sobj.shortPath, "description" : pobjlist['properties'][p]['title']})
                                    elif '$ref' not in  pobjlist['properties'][p]:
                                        if dname not in self.parameter_descriptions.keys():
                                            self.parameter_descriptions[dname] = []
                                        if {"file": sobj.shortPath, "description" : p} not in self.parameter_descriptions[dname]:
                                            self.parameter_descriptions[dname].append({"file": sobj.shortPath, "description" : p})
                elif 'items' in sobj.obj['components']['schemas'][schema]:
                    if 'properties' in sobj.obj['components']['schemas'][schema]['items']:
                        for p in sobj.obj['components']['schemas'][schema]['items']['properties']:
                            dname = '{}/{}'.format(schema,p)
                            #definitions_list.append(dname)
                            if 'description' in sobj.obj['components']['schemas'][schema]['items']['properties'][p]:
                                if '$ref' not in sobj.obj['components']['schemas'][schema]['items']['properties'][p]:
                                    definitions_list.append(dname)
                                    if dname not in self.parameter_descriptions.keys():
                                        self.parameter_descriptions[dname] = []
                                    if {"file": sobj.shortPath, "description" : sobj.obj['components']['schemas'][schema]['items']['properties'][p]["description"]} not in self.parameter_descriptions[dname]:
                                        self.parameter_descriptions[dname].append({"file": sobj.shortPath, "description" : sobj.obj['components']['schemas'][schema]['items']['properties'][p]["description"]})
                            elif 'title' in sobj.obj['components']['schemas'][schema]['items']['properties'][p]:
                                if '$ref' not in sobj.obj['components']['schemas'][schema]['items']['properties'][p]:
                                    definitions_list.append(dname)
                                    if dname not in self.parameter_descriptions.keys():
                                        self.parameter_descriptions[dname] = []
                                    if {"file": sobj.shortPath, "description" : sobj.obj['components']['schemas'][schema]['items']['properties'][p]["title"]} not in self.parameter_descriptions[dname]:
                                        self.parameter_descriptions[dname].append({"file": sobj.shortPath, "description" : sobj.obj['components']['schemas'][schema]['items']['properties'][p]["title"]})
                            elif '$ref' not in sobj.obj['components']['schemas'][schema]['items']['properties'][p]:
                                definitions_list.append(dname)
                                if dname not in self.parameter_descriptions.keys():
                                    self.parameter_descriptions[dname] = []
                                if {"file": sobj.shortPath, "description" : p} not in self.parameter_descriptions[dname]:
                                    self.parameter_descriptions[dname].append({"file": sobj.shortPath, "description" : p})
                elif 'description' in sobj.obj['components']['schemas'][schema]:
                    definitions_list.append(schema)
                    if schema not in self.parameter_descriptions.keys():
                        self.parameter_descriptions[schema] = []
                    if {"file": sobj.shortPath, "description" : sobj.obj['components']['schemas'][schema]['description']} not in self.parameter_descriptions[schema]:
                        self.parameter_descriptions[schema].append({"file": sobj.shortPath, "description" : sobj.obj['components']['schemas'][schema]['description']})
                elif 'title' in sobj.obj['components']['schemas'][schema]:
                    definitions_list.append(schema)
                    if schema not in self.parameter_descriptions.keys():
                        self.parameter_descriptions[schema] = []
                    if {"file": sobj.shortPath, "description" : sobj.obj['components']['schemas'][schema]['title']} not in self.parameter_descriptions[schema]:
                        self.parameter_descriptions[schema].append({"file": sobj.shortPath, "description" : sobj.obj['components']['schemas'][schema]['title']})
                elif 'additionalProperties' in sobj.obj['components']['schemas'][schema]:
                    for ap in sobj.obj['components']['schemas'][schema]['additionalProperties']:
                        if '$ref' not in ap:
                            raise ValueError ("Unhandled 'addiotnal property' in definition name {} in file {}".format(ap, sobj.shortPath))
                elif 'pattern' in sobj.obj['components']['schemas'][schema] and 'type' in sobj.obj['components']['schemas'][schema]:
                    raise ValueError ("No description for the definition name {} in file {}".format(schema, sobj.shortPath))
                elif '$ref' not in sobj.obj['components']['schemas'][schema]:
                    definitions_list.append(schema)
                    if schema not in self.parameter_descriptions.keys():
                        self.parameter_descriptions[schema] = []
                    if {"file": sobj.shortPath, "description" : schema} not in self.parameter_descriptions[schema]:
                        self.parameter_descriptions[schema].append({"file": sobj.shortPath, "description" : schema})
                else:
                    print ("Unparsable definition {} in file {}".format(schema, sobj.shortPath))
        return definitions_list

    def get_parameters(self, sobj: SwaggerObj):
        parameters = []
        if 'components' in sobj.obj:
            if 'parameters' in sobj.obj['components']:
                for parameter in sobj.obj['components']['parameters']:
                    if parameter not in self.parameter_exclusion_list:
                        parameters.append(parameter)
                        if parameter not in self.parameter_descriptions.keys():
                            self.parameter_descriptions[parameter] = []
                        if 'description' in sobj.obj['components']['parameters'][parameter]:
                            if {"file": sobj.shortPath, "description" : sobj.obj['components']['parameters'][parameter]["description"]} not in self.parameter_descriptions[parameter]:
                                self.parameter_descriptions[parameter].append({"file": sobj.shortPath, "description" : sobj.obj['components']['parameters'][parameter]["description"]})
                        else:
                            if {"file": sobj.shortPath, "description" : parameter} not in self.parameter_descriptions[parameter]:
                                self.parameter_descriptions[parameter].append({"file": sobj.shortPath, "description" : parameter})
        return parameters

    def get_parameter_references(self, sobj: SwaggerObj):
        parameters = []
        if 'components' in sobj.obj:
            if 'parameters' in sobj.obj['components']:
                for parameter in sobj.obj['components']['parameters']:
                    if 'schema' in sobj.obj['components']['parameters'][parameter]:
                        if '$ref' in sobj.obj['components']['parameters'][parameter]['schema']:
                                parameters.append(sobj.obj['components']['parameters'][parameter]['schema']['$ref'])
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
                    if 'schema' in parameter and '$ref' in parameter['schema']:
                        parameters_list.append(parameter['schema']['$ref'])
                    #elif 'name' in parameter and 'schema' not in parameter:
                    elif 'name' in parameter:
                        pname = parameter['name']
                        parameters_list.append(pname)
                        if pname not in self.parameter_descriptions.keys():
                            self.parameter_descriptions[pname] = []
                        if 'description' in parameter:
                            if {"file": sobj.shortPath, "endpoint": endpoint, "description" : parameter['description']} not in self.parameter_descriptions[pname]:
                                self.parameter_descriptions[pname].append({"file": sobj.shortPath, "endpoint": endpoint, "description" : parameter['description']})
                        else:
                            if {"file": sobj.shortPath, "endpoint": endpoint, "description" : pname} not in self.parameter_descriptions[pname]:
                                self.parameter_descriptions[pname].append({"file": sobj.shortPath, "endpoint": endpoint, "description" : pname})
            if 'requestBody' in sobj.obj['paths'][endpoint][method]:
                    if 'content' in sobj.obj['paths'][endpoint][method]['requestBody']:
                        for contentType in sobj.obj['paths'][endpoint][method]['requestBody']['content']:
                                if 'schema' in sobj.obj['paths'][endpoint][method]['requestBody']['content'][contentType]:
                                    if '$ref' in sobj.obj['paths'][endpoint][method]['requestBody']['content'][contentType]['schema']:
                                        parameters_list.append(sobj.obj['paths'][endpoint][method]['requestBody']['content'][contentType]['schema']['$ref'])
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
                       if 'content' in sobj.obj['paths'][endpoint][method]['responses'][response_code]:
                            for contentType in sobj.obj['paths'][endpoint][method]['responses'][response_code]['content']:
                                # if self.content_types.__contains__(contentType):
                                if 'schema' in sobj.obj['paths'][endpoint][method]['responses'][response_code]['content'][contentType]:
                                    for parameter in sobj.obj['paths'][endpoint][method]['responses'][response_code]['content'][contentType]['schema']:
                                        if parameter == 'properties':
                                            for item in (sobj.obj['paths'][endpoint][method]['responses'][response_code]['content'][contentType]['schema']['properties']).items():
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
                                            for item in (sobj.obj['paths'][endpoint][method]['responses'][response_code]['content'][contentType]['schema']['items']).items():
                                                    if item[0] == '$ref':
                                                        parameters_list.append(item[1])
                                        elif parameter == '$ref':
                                            parameters_list.append(sobj.obj['paths'][endpoint][method]['responses'][response_code]['content'][contentType]['schema']['$ref'])
        except:
            raise ValueError('An issue occured with the structure of file {} and endpoint {}'.format(sobj.shortPath, endpoint))
        return parameters_list


    def get_definitions_references(self, sobj: SwaggerObj):
        deinitionref={}
        if 'components' in sobj.obj:
            if 'schemas' in sobj.obj['components']:
                for schema in sobj.obj['components']['schemas']:
                    deinitionref[schema]=[]
                    if 'properties' in sobj.obj['components']['schemas'][schema]:
                        for p in sobj.obj['components']['schemas'][schema]['properties']:
                            deinitionref[schema].append(p)
                            if '$ref' in sobj.obj['components']['schemas'][schema]['properties'][p]:
                                deinitionref[schema].append(sobj.obj['components']['schemas'][schema]['properties'][p]['$ref'])
                            if 'items' in sobj.obj['components']['schemas'][schema]['properties'][p]:
                                if '$ref' in  sobj.obj['components']['schemas'][schema]['properties'][p]['items']:
                                    deinitionref[schema].append(sobj.obj['components']['schemas'][schema]['properties'][p]['items']['$ref'])
                    elif 'allOf' in sobj.obj['components']['schemas'][schema]:
                        for pobjlist in sobj.obj['components']['schemas'][schema]['allOf']: #[1]['properties']:
                            for pobj in pobjlist:
                                if 'properties' in pobj:
                                    for p in pobjlist['properties']:
                                        deinitionref[schema].append(p)
                                        if 'items' in pobjlist['properties'][p]:
                                            for item in pobjlist['properties'][p]['items']:
                                                if '$ref' in item:
                                                    deinitionref[schema].append(pobjlist['properties'][p]['items']['$ref'])
                                elif '$ref' in pobj:
                                    deinitionref[schema].append(pobjlist['$ref'])
                    elif 'anyOf' in sobj.obj['components']['schemas'][schema]:
                        for pobjlist in sobj.obj['components']['schemas'][schema]['anyOf']: #[1]['properties']:
                            for pobj in pobjlist:
                                if 'properties' in pobj:
                                    for p in pobjlist['properties']:
                                        deinitionref[schema].append(p)
                                        if 'items' in pobjlist['properties'][p]:
                                            for item in pobjlist['properties'][p]['items']:
                                                if '$ref' in item:
                                                    deinitionref[schema].append(pobjlist['properties'][p]['items']['$ref'])
                    elif 'oneOf' in sobj.obj['components']['schemas'][schema]:
                        for pobjlist in sobj.obj['components']['schemas'][schema]['oneOf']: #[1]['properties']:
                            for pobj in pobjlist:
                                if 'properties' in pobj:
                                    for p in pobjlist['properties']:
                                        deinitionref[schema].append(p)
                                        if 'items' in pobjlist['properties'][p]:
                                            for item in pobjlist['properties'][p]['items']:
                                                if '$ref' in item:
                                                    deinitionref[schema].append(pobjlist['properties'][p]['items']['$ref'])
                    elif 'additionalProperties' in sobj.obj['components']['schemas'][schema]:
                        for ap in sobj.obj['components']['schemas'][schema]['additionalProperties']:
                            if '$ref' in ap:
                                deinitionref[schema].append(sobj.obj['components']['schemas'][schema]['additionalProperties']['$ref'])
                    elif 'items' in sobj.obj['components']['schemas'][schema] and 'title' in sobj.obj['components']['schemas'][schema]:
                        for i in sobj.obj['components']['schemas'][schema]['items']:
                            if '$ref' in i:
                                deinitionref[schema].append(sobj.obj['components']['schemas'][schema]['items']['$ref'])
                            elif 'properties' in i:
                                for p in sobj.obj['components']['schemas'][schema]['items']['properties']:
                                    if '$ref' in sobj.obj['components']['schemas'][schema]['items']['properties'][p]:
                                        deinitionref[schema].append(sobj.obj['components']['schemas'][schema]['items']['properties'][p]['$ref'])

        return deinitionref

