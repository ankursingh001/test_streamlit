import ast
import functools
from abc import ABC, abstractmethod


def nullable_true(x):
    if not x:
        return True
    return True


def allow_empty_value(func):
    @functools.wraps(func)
    def wrapper(value):
        # Check if the value is None or empty
        if not value:
            return True
        return func(value)  # Call the original function if valid

    return wrapper  # Return the wrapped function


def is_string(x):
    return isinstance(x, str)


def is_comma_separated_string(x):
    return isinstance(x, str) and len(x.split(",")) > 1 if "," in x else False


def is_dict(x):
    if not isinstance(x, str):
        return False
    try:
        result = ast.literal_eval(x)
        return isinstance(result, dict)
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
        "_id": is_string,
        "cluster_id": is_string,
        "query_expansion": is_string,
        "synonyms":  allow_empty_value(is_comma_separated_string),
        "relevant_product_ids": allow_empty_value(is_dict_with_list_as_values),
        "intended_category_ids": is_string,
        "intended_subcategory_ids": is_string,
        "intended_destinations": is_string,
        "intended_countries": is_string,
        "query_type": is_string,
        "intended_country_codes": is_string,
        "meta_data": allow_empty_value(is_dict)
    }


class Failure:
    def __init__(self, column, rule_name, message):
        self.message = message
        self.column = column
        self.rule_name = rule_name

    def get_failure_response(self):
        return {
            "message": self.message,
            "column": self.column,
            "rule": self.rule_name
        }


class ValidationRule:
    def __init__(self):
        self.rules = {}

    def add_rule(self, rule, column):
        self.rules[column] = rule

    def add_rules(self, rules):
        for column, rule in rules.items():
            self.add_rule(rule, column)

    def validate_column(self, column, value):
        if column not in self.rules:
            return Failure(column, "No rule", f"No rule found for column {column}")
        if not self.rules[column](value):
            return Failure(column, self.rules[column].__name__, "")
        return None


class AbstractValidator(ABC):
    @abstractmethod
    def validate(self, df):
        pass


class SearchQueryMetaValidator(AbstractValidator):
    def __init__(self, df):
        self.df = df
        self.validation_rules = ValidationRule()
        self.validation_rules.add_rules(search_query_meta_validation_rules())

    def validate(self):
        failures = {}
        for index, row in self.df.iterrows():
            for column_name, value in row.items():
                failure = self.validation_rules.validate_column(column_name, value)
                if failure:
                    failures[column_name] = failure.get_failure_response()
        return failures