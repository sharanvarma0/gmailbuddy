from loguru import logger
from utils.emailutils import gmail
from utils.dbutils import emailbase
from utils import parsing_utils


if __name__ == "__main__":
    email_base_obj = emailbase.EmailBase()
    db_connection = email_base_obj.connect_to_database()
    gmail_credentials = gmail.login_to_gmail()
    service_obj = gmail.initialize_gmail_interaction(gmail_credentials)
    list_of_emails = parsing_utils.get_list_of_emails(service_obj)
    
    list_of_db_records = []

    for email in list_of_emails:
        email_database_record = emailbase.EmailBase.from_email(email)
        logger.debug(f"Converted Email to DB record")
        list_of_db_records.append(email_database_record)
    logger.debug(f"Number of records downloaded: {len(list_of_db_records)}")
    email_base_obj.insert_records_into_db(list_of_db_records)
