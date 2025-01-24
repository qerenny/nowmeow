#gen_uuid.py
import string
import uuid
import random
from utils.logging_utils import setup_logger, log_function_call

logger = setup_logger('gen_uuid', 'utils.log')

@log_function_call(logger)
def generate_id():
    try:
        return str(uuid.uuid4())
    except Exception as e:
        logger.error(f"Error generating UUID: {e}")

@log_function_call(logger)
def generate_email():
    try:
        characters = string.ascii_lowercase + string.digits
        return ''.join(random.choices(characters, k=8))
    except Exception as e:
        logger.error(f"Error generating email: {e}")

@log_function_call(logger)
def generate_sub_id(length=16):
    try:
        characters = string.ascii_lowercase + string.digits
        random_string = ''.join(random.choice(characters) for _ in range(length))
        return random_string
    except Exception as e:
        logger.error(f"Error generating sub ID: {e}")
