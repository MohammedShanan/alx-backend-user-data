#!/usr/bin/env python3
"""A module for filtering logs"""
import os
import re
import logging
import mysql.connector
from typing import List

PII_FIELDS = ("name", "email", "phone", "ssn", "password")


def filter_datum(
    fields: List[str],
    redaction: str,
    message: str,
    separator: str,
) -> str:
    """Filters a log line"""
    pattern = f"({'|'.join(fields)})=[^ {separator}]*"
    return re.sub(pattern, lambda m: f"{m.group(1)}={redaction}", message)


def get_logger() -> logging.Logger:
    """Creates a new logger for user data"""
    logger = logging.getLogger("user_data")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(RedactingFormatter(PII_FIELDS))
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.addHandler(stream_handler)
    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """Creates a connector to a database."""
    db_host = os.getenv("PERSONAL_DATA_DB_HOST", "localhost")
    db_name = os.getenv("PERSONAL_DATA_DB_NAME", "")
    db_user = os.getenv("PERSONAL_DATA_DB_USERNAME", "root")
    db_pwd = os.getenv("PERSONAL_DATA_DB_PASSWORD", "")
    connection = mysql.connector.connect(
        host=db_host,
        port=3306,
        user=db_user,
        password=db_pwd,
        database=db_name,
    )
    return connection


class RedactingFormatter(logging.Formatter):
    """Redacting Formatter class"""

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    FORMAT_FIELDS = ("name", "levelname", "asctime", "message")
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """formats a LogRecord"""
        msg = super(RedactingFormatter, self).format(record)
        txt = filter_datum(self.fields, self.REDACTION, msg, self.SEPARATOR)
        return txt


def main():
    """Logs the information about user records in a table."""
    info_logger = get_logger()
    connection = get_db()

    query = "SELECT name, email, phone, ssn, password, ip, last_login, user_agent FROM users;"
    columns = query.replace("SELECT ", "").replace(" FROM users;", "").split(", ")

    with connection.cursor() as cursor:
        cursor.execute(query)
        for row in cursor.fetchall():
            msg = "; ".join(f"{col}={val}" for col, val in zip(columns, row)) + ";"
            info_logger.info(msg)


if __name__ == "__main__":
    main()
