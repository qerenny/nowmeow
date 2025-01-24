#auth.py
import requests
import urllib3
from utils.logging_utils import setup_logger, retry_on_error, log_function_call
from utils.config import API_USERNAME, API_PASSWORD, API_IP, API_PORT, API_PATH

# Настраиваем логгер
logger = setup_logger('auth', 'api.log')

# Отключаем предупреждения о сертификате
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@retry_on_error(retries=3, delay=5)
@log_function_call(logger)
def login():
    """Авторизация в панели управления с автоматическими попытками переподключения"""
    try:
        url = f"https://{API_IP}:{API_PORT}/{API_PATH}/login"

        payload = {
            'username': API_USERNAME,
            'password': API_PASSWORD
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        session = requests.Session()
        response = session.post(url, headers=headers, data=payload, verify=False)

        if not response.ok:
            logger.error(f"Login failed with status code: {response.status_code}")
            raise Exception(f"Failed to login. Status code: {response.status_code}")

        logger.info("Successfully logged in")
        return session

    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error during login: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise


@log_function_call(logger)
def logout(session):
    """Безопасное завершение сессии"""
    try:
        session.close()
        logger.info("Successfully logged out")
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        raise