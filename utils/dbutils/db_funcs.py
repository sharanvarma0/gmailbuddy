from loguru import logger
from sqlalchemy import text
from sqlalchemy.orm import Session

def execute_raw_sql_query(db_engine, query, query_kwargs):
    try:
        logger.debug(f"Received Query: {query}")
        with Session(db_engine) as conn:
            conn.execute(text(query), {**query_kwargs})
            conn.commit()
    except Exception as sql_query_exec_exception:
        logger.error(f"Exception when attempting to execute raw sql query: {sql_query_exec_exception}")
