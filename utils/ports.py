import random
from utils.logging_utils import setup_logger, log_function_call

logger = setup_logger('ports', 'utils.log')

@log_function_call(logger)
def random_port():
    return random.randint(29401, 29599)