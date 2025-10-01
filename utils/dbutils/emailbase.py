import os
from loguru import logger
from sqlalchemy import Column, Date, Integer, String, create_engine, Boolean 
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()

class EmailBase(Base):
    __tablename__ = "emails"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
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
        return EmailBase(
            subject = email_instance.get("subject", ""),
            sender = email_instance.get("sender", ""),
            receiver = email_instance.get("receiver", ""),
            cc = email_instance.get("cc", ""),
            bcc = email_instance.get("bcc", ""),
            sent_timestamp = email_instance.get("sent_timestamp", ""),
            received_timestamp = email_instance.get("received_timestamp", ""),
            current_mailbox_location = email_instance.get("mailbox", ""),
            is_read = email_instance.get("is_read", "")
        )

    def drop_db(self):
        Base.metadata.drop_all(self.database_engine)

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
