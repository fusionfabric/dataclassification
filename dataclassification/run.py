import logging
import os
import sys

import pandas as pd
from dataclassification.Extensions.Spreadsheet.ConfigGenerator import (
    JSONGenerator,
    SpreadsheetGenerator,
)
from dataclassification.Extensions.Spreadsheet.LogGenerator import LogGenerator
from dataclassification.Extensions.Swaggers.SwaggerClassifier import SwaggerClassifier

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


class RunClassificationEngine:
    """
    This gathers user inputs and execution of different functions in all files.
    cg aka config generator is used for building the rules file
    sc aka swagger classifier works through all the swagger files to parse-
    params using the swagger handler files and then uses the different
    swagger-classifier files to classify each individual swagger file
    sg aka spreadsheet generator creates the generated dictionary file which
    gives us a holistic view of the swagger classifications
    lg aka log generator creates stats and logs for the classification process
    param swagger_folder_path is used to supply the location of the swagger files
    param config_folder_path is used to supply the location of the config file,
    master dictionary and template dictionary
    param app_name is used to give the name of the product/api whose swagger
    is being classified
    param filetypes defaults to ['swagger','events'] as the tool only classifies
    swaggers and datasets
    """

    def __init__(
        self,
        swagger_folder_path,
        config_folder_path,
        app_name,
        filetypes=["swagger", "events"],
    ):

        template_file_path = os.path.join(config_folder_path + "/Data Dictionary.xlsx")
        dictionary_details_file_path = os.path.join(
            config_folder_path + "/Dictionary Details.csv"
        )
        rules_file_path = os.path.join(config_folder_path + "/rules.json")
        swaggers_folder = swagger_folder_path
        new_dictionary_file_name = os.path.join(
            swaggers_folder + "/Generated Dictionary.xlsx"
        )
        df = pd.read_excel(
            template_file_path, sheet_name="config_sheet", index_col=None
        )
        classification_header = df["classification_header"][0]
        encryption_header = df["encryption_header"][0]
        maturity_status = df["maturity_status"][0]
        try:
            parameter_exclusion_list = (df["parameter_exclusion_list"][0]).split(",")
        except:
            parameter_exclusion_list = []

        # Generates rule.json file from a dictionary supplied by product/privacy/data teams
        cg = JSONGenerator(
            swaggers_folder, dictionary_details_file_path, filetypes, template_file_path
        )
        cg.generate_json_files(rules_file_path)

        # Generates classified swaggers in a folder named 'swaggers' (default)
        sc = SwaggerClassifier(
            swaggers_folder,
            classification_header,
            encryption_header,
            maturity_status,
            parameter_exclusion_list,
            rules_file_path,
            filetypes,
            cg.tag_list,
        )
        sc.execute(swaggers_folder)

        # Generates a fresh dictionary file based on the current swaggers
        # Use it to identify newly unclessified fields,
        # which will be sent to product/privacy/data to review and complete
        sg = SpreadsheetGenerator(
            swaggers_folder,
            sc,
            cg,
            new_dictionary_file_name,
            app_name,
            template_file_path,
        )
        sg.generate_dictionary(swaggers_folder)
        self.classification_report = sg.classification_report

        # The classification engine has a function to pull all unclassified technical names
        # Since everything is already in the spreadsheet, we can get it from here as well
        path = swaggers_folder + "/statistics-log.csv"
        self.lg = LogGenerator(app_name, path)
        self.lg.WriteProductLog(sg.unclassified_technical_fields, sg.all_fields)
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(
            filename=swaggers_folder + "/data-classification.log",
            format="%(asctime)s - %(levelname)s - %(message)s",
            level=logging.INFO,
        )
        logging.info("statistics-log.csv file has been generated")

    def WriteLog(self, statisticslog):
        self.lg.WriteLogFile(statisticslog)
