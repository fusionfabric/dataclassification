import json
import logging
import os
import sys
from collections import namedtuple

from DataClassification.BusinessRulesEngine.DataContracts import (
    Definition,
    DefinitionList,
    Rule,
    RulesList,
)

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


class ClassificationEngine:
    """
    Used for validating rules and aligning the parsed out technical definitions from the various swagger files
    to the defined dictionary technical names so that comparison can be done for classification
    param root folder supplies swagger folder path
    param json_file_name supplies path to rules.json
    """

    def __init__(self, root_folder, json_file_name):
        with open(json_file_name) as json_file:
            data = json.load(json_file)
            self.dl = DefinitionList(root_folder, data["definitions"])
            self.rl = RulesList(root_folder, data["rules"])
            self.__validate_rules(root_folder)
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(
            filename=root_folder + "/data-classification.log",
            format="%(asctime)s - %(levelname)s - %(message)s",
            level=logging.INFO,
        )

    def __validate_rules(self, root_folder):
        incorrect_rules = []
        definition_names = self.dl.get_definition_names()
        for rule in self.rl.rules_list:
            for name in rule.all:
                if name not in definition_names:
                    incorrect_rules.append(name)
            for name in rule.any:
                if name not in definition_names:
                    incorrect_rules.append(name)
        if len(incorrect_rules) > 0:
            logging.exception(
                "The following names in the rules section don't have a definition: {}".format(
                    incorrect_rules
                )
            )
            raise TypeError(
                "The following names in the rules section don't have a definition: {}".format(
                    incorrect_rules
                )
            )
        logging.info("Definitions and Rules have been validated")

    def __convert_technical_names_to_definintion_names(self, tech_names_list):
        definition_names = []
        api_directory = []
        for tn in tech_names_list:
            definition_names.append(
                self.dl.get_definition_name_by_technical_name(api_directory, tn)
            )
        return definition_names

    def get_combination_tags(self, combination_list=[]):
        tags = []
        combination_names_list = self.__convert_technical_names_to_definintion_names(
            combination_list
        )
        for rule in self.rl.rules_list:
            match_all_list = []
            match_any_list = []
            for c in combination_names_list:
                if c in rule.all:
                    match_all_list.append(c)
                elif c in rule.any:
                    match_any_list.append(c)
            if (
                len(match_all_list) == len(rule.all)
                and len(match_any_list) <= len(rule.any)
                and (len(match_all_list) > 0 or len(match_any_list) > 0)
            ):
                for tag in rule.tags:
                    if tag not in tags:
                        tags.append(tag)
        return tags

    def map_technical_names_to_definintion_names(self, api_directory, tech_names_list):
        definition_map = {}
        for tn in tech_names_list:
            if ":" in tn:
                api_directory_new, tn = tn.split(":")
                dn = self.dl.get_definition_name_by_technical_name(
                    api_directory_new, tn
                )
                if dn != None:
                    definition_map[tn] = self.dl.get_definition_name_by_technical_name(
                        api_directory_new, tn
                    )
            else:
                dn = self.dl.get_definition_name_by_technical_name(api_directory, tn)
                if dn != None:
                    definition_map[tn] = self.dl.get_definition_name_by_technical_name(
                        api_directory, tn
                    )
        return definition_map

    def get_tags(self, api_directory, combination_list=[]):
        mapped_tags = {}
        combination_names_list = self.map_technical_names_to_definintion_names(
            api_directory, combination_list
        )
        for rule in self.rl.rules_list:
            match_all_list = []
            match_any_list = []
            match_all_dict = {}
            match_any_dict = {}
            rule_all_items = list(set(rule.all))
            rule_any_items = list(set(rule.any))
            for tn, dn in combination_names_list.items():
                if dn in rule_all_items:
                    match_all_list.append(tn)
                    match_all_dict[dn] = 1
                elif dn in rule_any_items:
                    match_any_list.append(tn)
                    match_any_dict[dn] = 1
            match_all_list = list(set(match_all_list))
            match_any_list = list(set(match_any_list))
            if (
                len(match_all_dict) == len(rule.all)
                and len(match_any_dict) <= len(rule.any)
                and (len(match_any_dict) > 0 or len(match_all_dict) > 0)
            ):
                for matched_tn in match_all_list + match_any_list:
                    if matched_tn not in mapped_tags.keys():
                        mapped_tags[matched_tn] = []
                        for item in rule.tags:
                            mapped_tags[matched_tn].append(item)
                    else:
                        for item in rule.tags:
                            if item not in mapped_tags[matched_tn]:
                                mapped_tags[matched_tn].append(item)

        return mapped_tags

    def is_combination_classified(self, combination_list=[]):
        if len(self.get_combination_tags(combination_list)) > 0:
            return True
        return False

    def get_unslassified_technical_names(self, combination_list=[]):
        unclassified_list = []
        api_directory = []
        definition_names = self.map_technical_names_to_definintion_names(
            api_directory, combination_list
        )
        for c in combination_list:
            if c not in definition_names.keys():
                unclassified_list.append(c)
        return unclassified_list
