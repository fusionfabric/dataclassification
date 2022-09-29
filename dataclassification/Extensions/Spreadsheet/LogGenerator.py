import csv
import os
import sys


class LogGenerator:
    """
    Used for creating statistics and logs for the classification process
    param "product" provides the name of the app/product being classified
    param "path" provides the path for creating the statistics log file for the classificaiton process
    """

    def __init__(self, product, path):
        self.fields = [
            "PRODUCT",
            "API",
            "PERCENT",
            "TOTAL",
            "CLASSIFIED",
            "UNCLASSIFIED",
        ]
        self.product = product
        self.path = path
        self.statisticslog = []

    def WriteProductLog(self, unclassified_technical_fields, all_fields):

        if len(unclassified_technical_fields) > 0:
            print(
                "##vso[task.logissue type=warning;]Unclassified technical fields: {}".format(
                    unclassified_technical_fields
                )
            )
            total_fields = len(all_fields)
            unclassified_fields = len(unclassified_technical_fields)
            classified_fields = total_fields - unclassified_fields
            percentage = (classified_fields / len(all_fields)) * 100
            print(f"classification statistics of repository {self.product}")
            print(f"% of classified fields: {round(percentage, 1)}")
            print(f"total fields:{total_fields}")
            print(f"classified fields: {classified_fields}")
            print(f"unclassified fields: {unclassified_fields}")
            self.statisticslog.append(
                [
                    self.product,
                    "All-APIs",
                    round(percentage, 1),
                    total_fields,
                    classified_fields,
                    unclassified_fields,
                ]
            )

        else:
            classified_fields = len(all_fields) - len(unclassified_technical_fields)
            total_fields = len(all_fields)
            print(f"classification statistics of repository {self.product}")
            print(f"% of classified fields: {100}")
            print(f"total fields: {total_fields}")
            print(f"classified fields: {classified_fields}")
            print(f"unclassified fields: {0}")
            self.statisticslog.append(
                [self.product, "All-APIs", 100, total_fields, classified_fields, 0]
            )

    def WriteLogFile(self, log):
        self.statisticslog += log
        with open(self.path, "w", newline="") as csvFile:
            csvwriter = csv.writer(csvFile)
            csvwriter.writerow(self.fields)
            csvwriter.writerows(self.statisticslog)
