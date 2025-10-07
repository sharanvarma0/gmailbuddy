import json
import pathlib
import shutil
import os
import datetime
from loguru import logger
from utils.dbutils import emailbase, db_funcs
from utils.emailutils import gmail
from utils.rule_parser import RuleParser
from sqlalchemy.orm import Session
from sqlalchemy import text
import process_emails, download_and_store_emails

root_project_dir = os.getenv("PYTHONPATH", "")
email_obj = emailbase.EmailBaseTest()
db_engine = email_obj.connect_to_database()
date_today = datetime.datetime.now().date()

def get_count_of_records():
    select_statement = 'SELECT count(*) from emails_test'
    count = 0
    with Session(db_engine) as conn:
        result = conn.execute(text(select_statement))
        for row in result:
            count = row[0]
    return count


def get_email_labels_by_id(message_id):
    """
    Fetch an email by its Gmail ID and return details and labels.
    """
    creds = gmail.login_to_gmail()
    service = gmail.initialize_gmail_interaction(creds)
    
    msg = service.users().messages().get(userId="me", id=message_id, format="raw").execute()
    
    # Extract labels
    labels = msg.get("labelIds", [])
    return labels


def run_downloads_tests():
    download_and_store_emails.main()
    count = get_count_of_records()
    expected_number_of_results = 5
    
    if count != expected_number_of_results:
        logger.error("Download and Store: Test Failed")
    else:
        logger.error("Download and Store: Test Successful")


def run_processing_tests():
    test_file = f"{root_project_dir}/tests/test_rules.json"
    test_file_content = None
    with open(test_file, 'r') as file:
        test_file_content = file.read()
    test_file_json_content = json.loads(test_file_content)
    tests = test_file_json_content.get("tests", [])
    original_rules_file = os.path.join(root_project_dir, "rules.json")
    backup_rules_file = os.path.join(root_project_dir, "rules.json.bak")
    shutil.move(original_rules_file, backup_rules_file)
    test_result = False

    for test in tests:
        operations = test.get("operations", [{}])
        for operation in operations:
            with open(f"{root_project_dir}/rules.json", "w") as rules_file:
                rules_file.write(json.dumps(test))
            process_emails.main()
            os.remove(f"{root_project_dir}/rules.json")
            logger.error("Finished")

            rp = RuleParser(json.dumps(test))
            query, query_args = rp._parse_rules_and_form_where_query(operation.get('rules', []), operation.get('rule_predicate', ""))
            get_query, kwargs = rp.get_query_for_email_ids(operation, test)
            expected_labels = operation.get("expected_labels", [])
            email_ids = []
            result = db_funcs.execute_raw_sql_query_and_return_result(db_engine, get_query, kwargs)
            for row in result:
                email_ids.append(row[0])
            
            for email_id in email_ids:
                labels = get_email_labels_by_id(email_id)
                for el in expected_labels:
                    if el in labels:
                        test_result = test and True
            sql_verification_statement = test.get("verification_select_statement")
            sql_verification_statement = sql_verification_statement.format(where_subquery=query)
            expected_result = test.get("expected_result")
            with Session(db_engine) as conn:
                result = conn.execute(text(sql_verification_statement), {**query_args})
                if not result and not expected_result:
                    test_result = False
                if result and expected_result:
                    test_result = test and True
                if (result and not expected_result) or (not result and expected_result):
                    test_result = False
            if test:
                logger.error("Test Passed")
            else:
                logger.error("Test Failed")

    shutil.move(backup_rules_file, original_rules_file)


if __name__ == '__main__':
    run_downloads_tests()
    get_count_of_records()
    run_processing_tests()
    email_obj.drop_table()
