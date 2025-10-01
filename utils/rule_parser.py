import email
import json
from loguru import logger
from email.utils import parsedate_to_datetime
from datetime import datetime 
from dateutil.relativedelta import relativedelta


class RuleParser:

    final_expression = ""
    config_file = "rules.json"
    raw_config_file_content = None
    parsed_config_file_content = None
    required_operations = []
    parsed_sql_statements = []
    operations = []

    rule_conversion_map = {
        "less than": "<",
        "greater than": ">",
        "less than": "<",
        "less than or equal to": "<=",
        "greater than or equal to": ">=",
        "contains": "LIKE",
        "not contains": "NOT LIKE",
        "equals": "=",
        "not equals": "!=",
    }

    field_db_record_map = {
        'Subject': 'subject',
        'From': 'sender',
        'To': 'receiver',
        'Date Received': 'received_timestamp',
        'Date Sent': 'sent_timestamp',
        'is_read': 'is_read',
        'current_mailbox': 'current_mailbox'
    }

    rule_predicate_map = {
        'All': 'AND',
        'Any': 'OR'
    }

    action_db_field_map = {
        "move": "current_mailbox_location",
        "mark": "is_read"
    }

    def __init__(self, json_file_content):
        self.parsed_config_file_content = json.loads(json_file_content)
        self.operations = self.parsed_config_file_content.get("operations", [])
        logger.debug("Initialized Rule Parsing Engine")

    def _parse_input_datetime(self, raw_date):
        number, string_modifier = raw_date.split(' ')[0], raw_date.split(' ')[1]
        final_time = None
        delta = None
        number = int(number)
        if string_modifier == "days":
            delta = relativedelta(days=number)
        if string_modifier == "months":
            delta = relativedelta(months=number)
        final_time = datetime.now() - delta
        logger.debug(f"Parsed time: {final_time}")
        return final_time.date().isoformat()

    
    def _parse_rules_and_form_where_query(self, rules, rule_predicate):
        where_expressions = []
        kwargs = {}
        for rule in rules:
            field_name, predicate, value = rule.get("field_name"), rule.get("predicate"), rule.get("value")
            db_fieldname = self.field_db_record_map.get(field_name)
            sql_predicate = self.rule_conversion_map.get(predicate)
            if sql_predicate in ["LIKE", "NOT LIKE"]:
                value = f"%{value}%"
            if field_name in ["Date Sent", "Date Received"]:
                value = self._parse_input_datetime(value)
            value_pattern = f":{db_fieldname}"
            print(' '.join([db_fieldname, sql_predicate, value_pattern]))
            kwargs[f"{db_fieldname}"] = value
            where_expressions.append(' '.join([db_fieldname, sql_predicate, value_pattern]))
        conditional_modifier = self.rule_predicate_map.get(rule_predicate)
        return f" {conditional_modifier} ".join(where_expressions), kwargs
    
    def _parse_operation_and_form_set_query(self, operation):
        actions = operation.get("actions", [])
        kwargs = {}
        set_expressions = []
        for action in actions:
            query_action = action.get("action")
            if query_action == "move":
                db_fieldname = "current_mailbox_location"
            if query_action == "mark":
                db_fieldname = "is_read"
            if query_action in self.action_db_field_map:
                db_fieldname = self.action_db_field_map.get(query_action)
                value = action.get("value", "")
                if db_fieldname == "is_read":
                    if value == "read":
                        value = True
                    if value == "unread":
                        value = False
                value_pattern = f":{query_action}"
                kwargs[f"{query_action}"] = value
            temp_set_expression = f"{db_fieldname} = {value_pattern}"
            set_expressions.append(temp_set_expression)
        return "SET " + ','.join(set_expressions), kwargs


    def parse_operation(self, operation):
        sql_query_template = 'UPDATE emails {sub_set_query} WHERE {where_query}'
        rule_predicate = operation.get("rule_predicate", "")
        rules = operation.get("rules", [])
        set_query, set_kwargs = self._parse_operation_and_form_set_query(operation)
        where_query, where_kwargs = self._parse_rules_and_form_where_query(rules, rule_predicate)
        final_sql_query = sql_query_template.format(sub_set_query=set_query, where_query=where_query)
        kwargs = {**set_kwargs, **where_kwargs}
        logger.debug(f"Final SQL Query: {final_sql_query}")
        return final_sql_query, kwargs
    
    def parse_operations(self):
        sql_statements = []
        for operation in self.operations:
            op, kwargs = self.parse_operation(operation)
            sql_statements.append([op, kwargs])
        return sql_statements
