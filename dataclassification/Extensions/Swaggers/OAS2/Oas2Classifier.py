import copy
import os
import sys

from dataclassification.Extensions.Swaggers.SwaggerHandler import SwaggerObj


class Oas2Classifier:
    """
    Used for classifying 2.x versions of open-api-specification swagger files
    param classification_header provides classification header
    param encryption_header provides encryption header
    param tags_type provides list of tags
    """

    def __init__(self, classification_header, encryption_header, tags_type: list):
        self.classification_header = classification_header
        self.encryption_header = encryption_header
        self.tags_type = tags_type

    def classify_request_parameters(self, sobj: SwaggerObj, endpoint: str, tags: list):
        sobj_new = copy.deepcopy(sobj)
        for method in sobj.obj["paths"][endpoint]:
            param_counter = 0
            if "parameters" in sobj.obj["paths"][endpoint][method]:
                for parameter in sobj.obj["paths"][endpoint][method]["parameters"]:
                    if "name" in parameter:
                        pname = parameter["name"]
                        if pname in tags:
                            sobj_new.obj["paths"][endpoint][method]["parameters"][
                                param_counter
                            ][self.classification_header] = self.__get__parameter_tags(
                                tags, pname
                            )
                    param_counter += 1
        return sobj_new

    def classify_response_parameters(self, sobj: SwaggerObj, endpoint: str, tags: list):
        sobj_new = copy.deepcopy(sobj)
        covered_responses = ["200", "201", "202"]
        for method in sobj.obj["paths"][endpoint]:
            for response_code in covered_responses:
                if response_code in sobj.obj["paths"][endpoint][method]["responses"]:
                    if (
                        "schema"
                        in sobj.obj["paths"][endpoint][method]["responses"][
                            response_code
                        ]
                    ):
                        for parameter in sobj.obj["paths"][endpoint][method][
                            "responses"
                        ][response_code]["schema"]:
                            if parameter == "properties":
                                for item in (
                                    sobj.obj["paths"][endpoint][method]["responses"][
                                        response_code
                                    ]["schema"][parameter]
                                ).items():
                                    if "type" in item[1] and item[0] in tags:
                                        sobj_new.obj["paths"][endpoint][method][
                                            "responses"
                                        ][response_code]["schema"][
                                            self.classification_header
                                        ] = self.__get__parameter_tags(
                                            tags, item[0]
                                        )
                            elif parameter == "type":
                                isfile = sobj_new.obj["paths"][endpoint][method][
                                    "responses"
                                ][response_code]["schema"]["type"]
                                if isfile == "file":
                                    sobj_new.obj["paths"][endpoint][method][
                                        "responses"
                                    ][response_code]["schema"][
                                        self.classification_header
                                    ] = self.__get__parameter_tags(
                                        tags, "file"
                                    )
        return sobj_new

    def classify_definitions(self, sobj: SwaggerObj, tags: list):
        sobj_new = copy.deepcopy(sobj)
        if "definitions" in sobj.obj:
            for definition in sobj.obj["definitions"]:
                if "properties" in sobj.obj["definitions"][definition]:
                    for p in sobj.obj["definitions"][definition]["properties"]:
                        dname = "{}/{}".format(definition, p)
                        if dname in tags:
                            sobj_new.obj["definitions"][definition]["properties"][p][
                                self.classification_header
                            ] = self.__get__parameter_tags(tags, dname)
                elif "allOf" in sobj.obj["definitions"][definition]:
                    list_counter = 0
                    for pobjlist in sobj.obj["definitions"][definition]["allOf"]:
                        if (
                            "properties"
                            in sobj_new.obj["definitions"][definition]["allOf"][
                                list_counter
                            ]
                        ):
                            for p in sobj_new.obj["definitions"][definition]["allOf"][
                                list_counter
                            ]["properties"]:
                                dname = "{}/{}".format(definition, p)
                                if dname in tags:
                                    sobj_new.obj["definitions"][definition]["allOf"][
                                        list_counter
                                    ]["properties"][p][
                                        self.classification_header
                                    ] = self.__get__parameter_tags(
                                        tags, dname
                                    )
                        list_counter += 1
                elif "items" in sobj.obj["definitions"][definition]:
                    if "properties" in sobj.obj["definitions"][definition]["items"]:
                        for p in sobj.obj["definitions"][definition]["items"][
                            "properties"
                        ]:
                            dname = "{}/{}".format(definition, p)
                            if dname in tags:
                                sobj_new.obj["definitions"][definition]["items"][
                                    "properties"
                                ][p][
                                    self.classification_header
                                ] = self.__get__parameter_tags(
                                    tags, dname
                                )
                elif (
                    "description" in sobj.obj["definitions"][definition]
                    and definition in tags
                ):
                    sobj_new.obj["definitions"][definition][
                        self.classification_header
                    ] = self.__get__parameter_tags(tags, definition)
        return sobj_new

    def classify_datasetdefinitions(self, sobj: SwaggerObj, tags: list):
        sobj_new = copy.deepcopy(sobj)
        if "definitions" in sobj_new.obj:
            for definition in sobj_new.obj["definitions"]:
                self.classify_datasetdefinitions_recursive(
                    sobj_new.obj["definitions"][definition], definition, tags
                )
        return sobj_new

    def classify_datasetdefinitions_recursive(
        self, sobj: SwaggerObj, definition: str, tags: list
    ):
        if "properties" in sobj:
            for p in sobj["properties"]:
                if definition:
                    dname = "{}/{}".format(definition, p)
                else:
                    dname = "{}".format(p)
                if "properties" in sobj["properties"][p]:
                    self.classify_datasetdefinitions_recursive(
                        sobj["properties"][p], p, tags
                    )
                elif "items" in sobj["properties"][p]:
                    if sobj["properties"][p]["items"]["type"] == "object":
                        self.classify_datasetdefinitions_recursive(
                            sobj["properties"][p]["items"], p, tags
                        )
                    else:
                        if dname in tags:
                            param_tag = self._get_matching_tag_for_header(tags, dname)
                            if "tag1" in param_tag.keys():
                                if len(param_tag["tag1"]) > 0:
                                    sobj["properties"][p][
                                        self.classification_header
                                    ] = param_tag["tag1"]
                            if "tag2" in param_tag.keys():
                                if len(param_tag["tag2"]) > 0:
                                    sobj["properties"][p][
                                        self.encryption_header
                                    ] = param_tag["tag2"]
                else:
                    if dname in tags:
                        param_tag = self._get_matching_tag_for_header(tags, dname)
                        if "tag1" in param_tag.keys():
                            if len(param_tag["tag1"]) > 0:
                                sobj["properties"][p][
                                    self.classification_header
                                ] = param_tag["tag1"]
                        if "tag2" in param_tag.keys():
                            if len(param_tag["tag2"]) > 0:
                                sobj["properties"][p][
                                    self.encryption_header
                                ] = param_tag["tag2"]
        elif "items" in sobj:
            if sobj["items"]["type"] == "object":
                self.classify_datasetdefinitions_recursive(
                    sobj["items"], definition, tags
                )
            else:
                if definition:
                    dname = "{}/{}".format(definition, p)
                else:
                    dname = "{}".format(p)
                if dname in tags:
                    param_tag = self._get_matching_tag_for_header(tags, dname)
                    if "tag1" in param_tag.keys():
                        if len(param_tag["tag1"]) > 0:
                            sobj[self.classification_header] = param_tag["tag1"]
                    if "tag2" in param_tag.keys():
                        if len(param_tag["tag2"]) > 0:
                            sobj[self.encryption_header] = param_tag["tag2"]

        elif "allOf" in sobj:
            list_counter = 0
            for pobjlist in sobj["allOf"]:
                if "properties" in sobj["allOf"][list_counter]:
                    self.classify_datasetdefinitions_recursive(
                        sobj["allOf"][list_counter], definition, tags
                    )
                list_counter += 1
        else:
            dname = "{}".format(definition)
            if dname in tags:
                param_tag = self._get_matching_tag_for_header(tags, dname)
                if "tag1" in param_tag.keys():
                    if len(param_tag["tag1"]) > 0:
                        sobj[self.classification_header] = param_tag["tag1"]
                if "tag2" in param_tag.keys():
                    if len(param_tag["tag2"]) > 0:
                        sobj[self.encryption_header] = param_tag["tag2"]

    def classify_parameters(self, sobj: SwaggerObj, tags: list):
        sobj_new = copy.deepcopy(sobj)
        if "parameters" in sobj.obj:
            for parameter in sobj.obj["parameters"]:
                if parameter in tags:
                    sobj_new.obj["parameters"][parameter][
                        self.classification_header
                    ] = self.__get__parameter_tags(tags, parameter)
        return sobj_new

    def __get__parameter_tags(self, tags, parameter_name):
        return tags[parameter_name]

    def _get_matching_tag_for_header(self, tags, dname):
        tag_handling = self.__get__parameter_tags(tags, dname)
        tags_by_type = {}
        for tag_name in tag_handling:
            if tag_name in self.tags_type["tag1"]:
                if "tag1" not in tags_by_type.keys():
                    tags_by_type["tag1"] = []
                    tags_by_type["tag1"].append(tag_name)
                else:
                    tags_by_type["tag1"].append(tag_name)
            if "tag2" in self.tags_type and tag_name in self.tags_type["tag2"]:
                if "tag2" not in tags_by_type.keys():
                    tags_by_type["tag2"] = []
                    tags_by_type["tag2"].append(tag_name)
                else:
                    tags_by_type["tag2"].append(tag_name)
        return tags_by_type
