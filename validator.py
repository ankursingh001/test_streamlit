import ast
from abc import ABC, abstractmethod

def is_string(x):
    return isinstance(x, str)

def is_comma_separated_string(x):
    return isinstance(x, str) and len(x.split(",")) > 1 if "," in x else False

def is_dict(x):
    if not isinstance(x, str):
        return False
    try:
        result = ast.literal_eval(s)
        return isinstance(result, list)
    except Exception as e:
        return False

def is_list(x):
    try:
        if not isinstance(x, str):
            return False
        if not x:
            # check x = ""
            return True
        result = ast.literal_eval(s)
        return isinstance(result, list)
    except Exception as e:
        return False

def is_dict_with_list_as_values(x):
    if not is_dict(x):
        return False
    # Converting string to dictionary
    dictionary = ast.literal_eval(x)
    for key, value in dictionary.items():
        if not isinstance(value, list):
            return False
    return True

def search_query_meta_validation_rules():
    return {
        "cluster_id": is_string,
        "synonyms":  is_comma_separated_string,
        "relevant_query_ids": is_dict_with_list_as_values,
        "intended_category_ids": is_string,
        "intended_subcategory_ids": is_string,
        "intended_destinations": is_string,
        "intended_countries": is_string,
        "query_type": is_string,
        "intended_country_codes": is_string,
        "meta_data": is_dict
    }

class Failure:
    def __init__(self, column, rule, message):
        self.message = message
        self.column = column
        self.rule = rule

    def get_failure_response(self):
        return {
            "message": self.message,
            "column": self.column,
            "rule": self.rule.__name__
        }

class ValidationRule:
    def __init__(self):
        self.rules = {}

    def add_rule(self, rule, column):
        self.rules[column] = rule

    def add_rules(self, rules):
        for column, rule in rules.items():
            self.add_rule(rule, column)

    def validate_column(self, column):
        if column not in self.rules:
            return Failure(column, "No rule", f"No rule found for column {column}")
        if not self.rules[column].validate(column):
            return Failure(column, self.rules.__name__, self.rules[column].get_message())

class AbstractValidator(ABC):
    @abstractmethod
    def validate(self, df):
        pass

    @abstractmethod
    def validate_column(self, df,  column):
        pass

class SearchQueryMetaValidator(AbstractValidator):
    def __init__(self, df):
        self.df = df
        self.validation_rules = ValidationRule()
        self.validation_rules.add_rules(search_query_meta_validation_rules())

    def validate(self, df):
        failures = []
        for column in df.columns:
            failure = self.validation_rules.validate_column(column)
            if failure:
                failures.append(failure)
        return failures