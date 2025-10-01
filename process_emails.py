from loguru import logger
from utils import parsing_utils
from utils.rule_parser import RuleParser
from utils.dbutils import db_funcs
from utils.dbutils import emailbase
import os

project_dir = os.getenv("PYTHONPATH")
test = os.getenv("TEST", False)

def main():
    email_session = emailbase.EmailBase()
    if test:
        email_session = emailbase.EmailBaseTest()
    email_db_engine = email_session.connect_to_database()
    email_session.initialize_db_operations()

    config_file = f"{project_dir}/rules.json"

    json_content = None
    with open(config_file, 'r') as file:
        json_content = file.read()
    rule_parser = RuleParser(json_content)
    sql_statements = rule_parser.parse_operations()

    for statement, kwargs in sql_statements:
        db_funcs.execute_raw_sql_query(email_session.database_engine, statement, kwargs)


if __name__ == '__main__':
    main()
