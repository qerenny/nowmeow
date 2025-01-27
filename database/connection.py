#databse/connection.py
from utils.config import API_IP, API_PORT_SSH, API_USERNAME_SSH, API_PRIVATE_KEY_SSH, API_PASSWORD_SSH, DB_NAME, DB_USERNAME, DB_PASSWORD, DB_PORT
import psycopg2
from utils.logging_utils import setup_logger, retry_on_error, log_function_call
from sshtunnel import SSHTunnelForwarder

logger = setup_logger('connection.database', 'database.log')


@log_function_call(logger)
def connect_to_db():
    """Установка соединения с локальной базой данных"""
    conn = None
    try:
        # Создание подключения к базе данных
        conn = psycopg2.connect(
            database=DB_NAME,
            user=DB_USERNAME,
            password=DB_PASSWORD,
            host='localhost',  # или '127.0.0.1'
            port=DB_PORT
        )
        conn.autocommit = True

        cur = conn.cursor()
        logger.info("Database connection established successfully")

        return conn, cur

    except Exception as e:
        logger.error(f"Error while connecting to database: {str(e)}")
        if conn:
            conn.close()
        raise


@log_function_call(logger)
def disconnect_from_db(conn):
    """Безопасное закрытие соединения"""
    try:
        if conn:
            conn.close()
        logger.info("Database connection closed successfully")
    except Exception as e:
        logger.error(f"Error while disconnecting from database: {str(e)}")
        raise