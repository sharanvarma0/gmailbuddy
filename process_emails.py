from loguru import logger
from utils import parsing_utils
from utils.rule_parser import RuleParser
from utils.dbutils import db_funcs
from utils.dbutils import emailbase
from utils.emailutils import gmail
import os

project_dir = os.getenv("PYTHONPATH")
test = os.getenv("TEST", False)

def main():
    email_session = emailbase.EmailBase()
    gmail_credentials = gmail.login_to_gmail()
    service_obj = gmail.initialize_gmail_interaction(gmail_credentials)
    if test:
        email_session = emailbase.EmailBaseTest()
    email_db_engine = email_session.connect_to_database()
    email_session.initialize_db_operations()

    config_file = f"{project_dir}/rules.json"

    json_content = None
    with open(config_file, 'r') as file:
        json_content = file.read()
    rule_parser = RuleParser(json_content)
    sql_statements, select_statements = rule_parser.parse_operations(test=test)
    
    email_ids = []

    for select_statement, kwargs, target_labels in select_statements:
        result = db_funcs.execute_raw_sql_query_and_return_result(email_session.database_engine, select_statement, kwargs)
        for row in result:
            email_ids.append(row[0])
        for mail_id in email_ids:
            gmail.update_email(service_obj, mail_id, target_labels)
            

    for statement, kwargs in sql_statements:
        db_funcs.execute_raw_sql_query(email_session.database_engine, statement, kwargs)


if __name__ == '__main__':
    main()
