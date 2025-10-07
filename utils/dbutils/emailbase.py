import os
from loguru import logger
from sqlalchemy import Column, Date, Integer, String, create_engine, Boolean, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session


Base = declarative_base()

class EmailBase(Base):
    """This is the class which is used as a table template by the ORM to create and manipulate tables
    in the DB.

    For all DB manipulation purposes of the Email table, this class can be used if the interface is intended
    via an ORM"""

    __tablename__ = "emails"
    
    id = Column(String(512), primary_key=True)
    subject = Column(String(512), nullable=False, default="")
    sender = Column(String(512), nullable=False, default="")
    receiver = Column(String(512), nullable=False, default="")
    cc = Column(String(512), nullable=False, default="")
    bcc = Column(String(512), nullable=False, default="")
    sent_timestamp = Column(Date, nullable=True)
    received_timestamp = Column(Date, nullable=True)
    current_mailbox_location = Column(String(512), nullable=False, default="inbox")
    is_read = Column(Boolean, nullable=False, default=False)
    database_engine = None
    db_username, db_password = os.getenv("POSTGRESQL_USERNAME"), os.getenv("POSTGRESQL_PASSWORD")

    """The following static method is used to construct an EmailBase object from a passed dictionary
    containing all the details"""
    @staticmethod
    def from_email(email_instance):
        return EmailBase(
            id=email_instance.get("id", ""),
            subject = email_instance.get("subject", ""),
            sender = email_instance.get("sender", ""),
            receiver = email_instance.get("receiver", ""),
            cc = email_instance.get("cc", ""),
            bcc = email_instance.get("bcc", ""),
            sent_timestamp = email_instance.get("sent_timestamp", None),
            received_timestamp = email_instance.get("received_timestamp", None),
            current_mailbox_location = email_instance.get("mailbox", ""),
            is_read = email_instance.get("is_read", False)
        )

    def drop_table(self):
        with Session(self.database_engine) as conn:
            conn.execute(text("TRUNCATE emails"))


    def initialize_db_operations(self):
        Base.metadata.create_all(self.database_engine)

    def connect_to_database(self):
        if not self.db_username or not self.db_password:
            logger.error("Missing DB username or DB password. Not proceeding with login")
            exit()
        self.database_engine = create_engine("postgresql+psycopg2://postgresql:password@127.0.0.1/gmailbuddy", echo=True)
        if self.database_engine:
            logger.debug("Created Engine connection")
        return self.database_engine

    def insert_records_into_db(self, list_of_records):
        try:
            logger.debug(f"Obtained list of records to insert into DB: {len(list_of_records)}")
            session = sessionmaker(bind=self.database_engine)
            with session() as db_connection:
                db_connection.add_all(list_of_records)
                db_connection.commit()
                logger.debug(f"Insert Committed")
        except Exception as db_insert_exception:
            logger.error(f"Exception when attempting to insert records into Database: {db_insert_exception}")


class EmailBaseTest(Base):

    """This class is for the test table. The tests run in a different table to make sure that
    updates/inserts made during tests are not present in the real table. The recommended use
    is to use this for unit tests and then truncate the table post the tests to make sure disk space
    is not used unnecessarily"""

    __tablename__ = 'emails_test'

    id = Column(String(512), primary_key=True)
    subject = Column(String(512), nullable=False, default="")
    sender = Column(String(512), nullable=False, default="")
    receiver = Column(String(512), nullable=False, default="")
    cc = Column(String(512), nullable=False, default="")
    bcc = Column(String(512), nullable=False, default="")
    sent_timestamp = Column(Date, nullable=True)
    received_timestamp = Column(Date, nullable=True)
    current_mailbox_location = Column(String(512), nullable=False, default="inbox")
    is_read = Column(Boolean, nullable=False, default=False)
    database_engine = None
    db_username, db_password = os.getenv("POSTGRESQL_USERNAME"), os.getenv("POSTGRESQL_PASSWORD")

    @staticmethod
    def from_email(email_instance):
        return EmailBaseTest(
            id = email_instance.get("id", ""),
            subject = email_instance.get("subject", ""),
            sender = email_instance.get("sender", ""),
            receiver = email_instance.get("receiver", ""),
            cc = email_instance.get("cc", ""),
            bcc = email_instance.get("bcc", ""),
            sent_timestamp = email_instance.get("sent_timestamp", None),
            received_timestamp = email_instance.get("received_timestamp", None),
            current_mailbox_location = email_instance.get("mailbox", ""),
            is_read = email_instance.get("is_read", False)
        )

    def drop_table(self):
        logger.error("Truncating")
        with Session(self.database_engine) as conn:
            conn.execute(text("TRUNCATE emails_test"))
            conn.commit()

    def initialize_db_operations(self):
        Base.metadata.create_all(self.database_engine)

    def connect_to_database(self):
        if not self.db_username or not self.db_password:
            logger.error("Missing DB username or DB password. Not proceeding with login")
            exit()
        self.database_engine = create_engine("postgresql+psycopg2://postgresql:password@127.0.0.1/gmailbuddy", echo=True)
        if self.database_engine:
            logger.debug("Created Engine connection")
        return self.database_engine

    def insert_records_into_db(self, list_of_records):
        try:
            logger.debug(f"Obtained list of records to insert into DB: {len(list_of_records)}")
            session = sessionmaker(bind=self.database_engine)
            with session() as db_connection:
                db_connection.add_all(list_of_records)
                db_connection.commit()
                logger.debug(f"Insert Committed")
        except Exception as db_insert_exception:
            logger.error(f"Exception when attempting to insert records into Database: {db_insert_exception}")

