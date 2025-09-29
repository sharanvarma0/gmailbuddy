import os.path
from loguru import logger
from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_USERNAME, DB_PASSWORD = os.getenv("POSTGRESQL_USERNAME", ""), os.getenv("POSTGRESQL_PASSWORD", "")
Base = declarative_base()

def connect_to_database():
    if not DB_USERNAME or not DB_PASSWORD:
        logger.error("Missing DB username or DB password. Not proceeding with login")
        exit()
    engine = create_engine("postgresql+psycopg2://postgresql:password@127.0.0.1/gmailbuddy", echo=True)
    if engine:
        logger.debug("Created Engine connection")
    return engine

class EmailBase(Base):
    __tablename__ = "emails"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    subject = Column(String(512), nullable=False, default="")
    sender = Column(String(512), nullable=False, default="")
    receiver = Column(String(512), nullable=False, default="")
    cc = Column(String(512), nullable=False, default="")
    bcc = Column(String(512), nullable=False, default="")
    sent_timestamp = Column(DateTime(timezone=True), nullable=True)
    received_timestamp = Column(DateTime(timezone=True), nullable=True)

    @staticmethod
    def from_email(email_instance):
        return EmailBase(
            subject = email_instance.get("subject", ""),
            sender = email_instance.get("sender", ""),
            receiver = email_instance.get("receiver", ""),
            cc = email_instance.get("cc", ""),
            bcc = email_instance.get("bcc", ""),
            sent_timestamp = email_instance.get("sent_timestamp", ""),
            received_timestamp = email_instance.get("received_timestamp", "")
        )


def initialize_db_operations(db_engine):
    Base.metadata.create_all(db_engine)



def insert_records_into_db(db_engine, list_of_records):
    try:
        logger.debug(f"Obtained list of records to insert into DB: {len(list_of_records)}")
        session = sessionmaker(bind=db_engine)
        with session() as db_connection:
            db_connection.add_all(list_of_records)
            db_connection.commit()
            logger.debug(f"Insert Committed")
    except Exception as db_insert_exception:
        logger.error(f"Exception when attempting to insert records into Database: {db_insert_exception}")
