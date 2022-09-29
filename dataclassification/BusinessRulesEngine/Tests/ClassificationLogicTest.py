import collections
import json
import os
import unittest

from dataclassification.BusinessRulesEngine.ClassificationLogic import (
    ClassificationEngine,
)


class ClassificationEngineTest(unittest.TestCase):
    def setUp(self):
        self.ce = ClassificationEngine(
            json_file_name=os.path.join(os.path.dirname(__file__), "rules-test.json")
        )
        with open(
            os.path.join(os.path.dirname(__file__), "rules-test-config.json")
        ) as json_file:
            data = json.load(json_file)
            self.classified = data["classified"]
            self.not_classified = data["not_classified"]
            self.correct_tags = data["correct_tags"]
            self.incorrect_tags = data["incorrect_tags"]
            self.get_tags_for_tech_names = data["get_tags_for_tech_names"]
            self.get_unclassified_tech_names = data["get_unclassified_tech_names"]

    def test_classifications(self):
        for c in self.classified:
            assert self.ce.is_combination_classified(c)

    def test_not_classifications(self):
        for c in self.not_classified:
            assert not self.ce.is_combination_classified(c)

    def test_classification_tags(self):
        for c in self.correct_tags:
            assert collections.Counter(
                self.ce.get_combination_tags(c["list"])
            ) == collections.Counter(c["tags_to_test"])

    def test_incorrect_classification_tags(self):
        for c in self.incorrect_tags:
            assert collections.Counter(
                self.ce.get_combination_tags(c["list"])
            ) != collections.Counter(c["tags_to_test"])

    def test_classification_tags_mapping(self):
        for c in self.get_tags_for_tech_names:
            assert collections.Counter(
                self.ce.get_tags(c["list"])
            ) == collections.Counter(c["result"])

    def test_not_unclassified_tag_names(self):
        for tn in self.get_unclassified_tech_names:
            assert collections.Counter(
                self.ce.get_unslassified_technical_names(tn["list"])
            ) == collections.Counter(tn["result"])

    def test_not_classified_tags_mapping(self):
        for c in self.not_classified:
            assert len(self.ce.get_tags(c)) == 0


if __name__ == "__main__":
    unittest.main()
