from json import JSONEncoder
import logging

class Definition:
    """
                Used for matching parsed out swagger definitions with provided master dictionary technical names
                as per the rules specified in the dictionary template file
                param root folder supplies the swagger folder path
                param definition supplies definitions from the rules.json file
                """

    def __init__(self,root_folder, definition : {"friendly_name": str, "description": str, "technical_names": list(str.__dict__)}):
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(filename=root_folder + '/data-classification.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
        self.name = definition["friendly_name"]
        self.description = definition["description"]
        self.examples = definition["examples"]
        self.sensitive = definition["sensitive"]
        self.guidelines = definition["guidelines"]
        self.technical_names_set = set(
            n.lower() for n in definition["technical_names"]
        )
        self.exception_names_set = set(
            n.lower() for n in definition["Exception_API_and_Values"]
        )
        if self.name == None:
            logging.error("A friendly name cannot be empty")
            raise TypeError("A friendly name cannot be empty")
        elif self.description == None:
            logging.error("The description of {} cannot be empty".format(self.name))
            raise TypeError("The description of {} cannot be empty".format(self.name))

    def is_tech_name_in_definition(self, api_directory, tech_name):
        if api_directory:
            if self.exception_names_set:
                for exception_names in self.exception_names_set:
                    api_directory_name, exception_technical_name = exception_names.split(":")
                    if api_directory.lower()[:-1] == api_directory_name and tech_name == exception_technical_name:
                        return True
        return tech_name in self.technical_names_set

class DefinitionList:

    def __init__(self,root_folder, definition_list : list(Definition.__dict__)):
        self.definition_list = []
        for definition in definition_list:
            definition_obj = Definition(root_folder,definition)
            self.definition_list.append(definition_obj)

    def get_definition_names(self):
        definition_names = []
        for definition in self.definition_list:
            definition_names.append(definition.name)
        return definition_names
    
    def get_definition_name_by_technical_name(self, api_directory, tech_name):
        tech_name_lower = tech_name.lower()
        for d in self.definition_list:
            if d.exception_names_set:
                if d.is_tech_name_in_definition(api_directory, tech_name_lower):
                    return d.name
        for d in self.definition_list:
            if d.is_tech_name_in_definition(api_directory, tech_name_lower):
                return d.name
        for d in self.definition_list:
            if '/' in tech_name_lower:
                new_tech_name_lower = "*/"+tech_name_lower.split("/")[1]
            else:
                new_tech_name_lower = "*/"+tech_name_lower
            if d.is_tech_name_in_definition(api_directory, new_tech_name_lower):
                return d.name

class Rule:

    def __init__(self,root_folder, rule = {"tags" : list(str.__dict__), "all" : list(str.__dict__), "any" : list(str.__dict__)}):
        self.tags = rule["tags"]
        self.all = rule["all"]
        self.any = rule["any"]
        if len(self.all) == 0 and len(self.any) == 0:
            logging.error("A rule must have technical names in either 'all' or 'any' sections.")
            raise TypeError("A rule must have technical names in either 'all' or 'any' sections.")

    def is_name_in_rule(self, name):
        if name in self.any or name in self.all:
            return True
        return False

class RulesList:

    def __init__(self,root_folder, rules_list = list(Rule.__dict__)):
        self.rules_list = []
        for rule in rules_list:
            rule_obj = Rule(root_folder,rule)
            self.rules_list.append(rule_obj)
    
    def is_name_in_rule_list(self, name):
        for rule in self.rules_list:
            if rule.is_name_in_rule(name):
                return True
        return False