#middleware/user.py
import const.const_bot
import database.user
import utils.timestamp
from api import client as client
from utils.logging_utils import log_function_call, setup_logger

logger = setup_logger('user.middleware', 'middleware.log')

@log_function_call(logger)
def select_all_users():
    """
    Returns all user ids from the local 'users' table.
    """
    try:
        return database.user.select_all_users()
    except Exception as e:
        logger.error(f"Failed to select all users ids: {str(e)}")
        raise
    
def select_all_active_users():
    """
    Returns all active user ids from the local 'users' table.
    """
    users=[]
    try:
        for user in database.user.select_all_users():
            if int(user[3]) > utils.timestamp.current_timestamp():
                users.append(user)
        
        return users
    except Exception as e:
        logger.error(f"Failed to select all active users ids: {str(e)}")
        raise

@log_function_call(logger)
def post_new_user_and_get_vless(tg_id, period, username):
    """
    Creates a new user in 3x-ui and returns the vless profile.
    """
    try:
        vless = client.add_client(tg_id, period, username)
        return vless
    except Exception as e:
        logger.error(f"Failed to add user in 3x-ui: {str(e)}")
        raise


@log_function_call(logger)
def get_user_exists_in_user(tg_id):
    """
    Checks if a user exists in the local 'users' table.
    """
    try:
        return database.user.select_user_exists(tg_id)
    except Exception as e:
        logger.error(f"Failed to get user existence: {str(e)}")
        raise


@log_function_call(logger)
def create_or_update_user(tg_id, period, username):
    """
    Creates or updates a user in 3X-UI, also reflects in local DB.
    """
    try:
        if get_user_exists_in_user(tg_id):
            client.update_client(tg_id, period)
        else:
            return post_new_user_and_get_vless(tg_id, period, username)
    except Exception as e:
        logger.error(f"Failed to create or update user: {str(e)}")
        raise


@log_function_call(logger)
def send_vless(tg_id):
    """
    Retrieves and returns the vless profile if user exists locally.
    """
    try:
        if get_user_exists_in_user(tg_id):
            data = database.user.select_user_vless_profile(tg_id)
            return data
        else:
            return 'Ой, вас, к сожалению нет в системе! Для начала купите подписку или используйте пробный период'
    except Exception as e:
        logger.error(f"Failed to send vless profile: {str(e)}")
        raise


@log_function_call(logger)
def select_user_date(tg_id):
    """
    Returns the expiration date for a user.
    """
    try:
        return database.user.select_user_date(tg_id)
    except Exception as e:
        logger.error(f"Failed to select user date: {str(e)}")
        raise

@log_function_call(logger)
def get_users_expiration_date(tg_id):
    """
    Returns the formatted expiration date for a user's subscription.
    """
    try:
        date_ts = database.user.select_user_date(tg_id)
        date_dt = utils.timestamp.timestamp_to_date(date_ts).replace(microsecond=0, tzinfo=None)
        final_date = date_dt.strftime('%H:%M:%S %d-%m-%Y')
        logger.info(f"Expiration date for tg_id={tg_id}: {final_date}.")
        return final_date
    except Exception as e:
        logger.error(f"Failed to get user expiration date: {str(e)}")
        raise

@log_function_call(logger)
def get_users_expiration_date_to_comfort_format(tg_id):
    """
    Returns user subscription date in a more human-readable format.
    """
    try:
        date_ts = database.user.select_user_date(tg_id)
        date_diff = utils.timestamp.calculate_time_difference(date_ts)

        if const.const_bot.EXPIRED == date_diff:
            logger.info(f"User subscription expired for tg_id={tg_id}.")
            return "муф.. твоя подписка уже закончилась😿"
        if const.const_bot.LESS_THAN_HOUR == date_diff:
            logger.info(f"User subscription less than an hour for tg_id={tg_id}.")
            return "кошечки-божечки, у тебя осталось меньше часа🙀"
        return date_diff
    except Exception as e:
        logger.error(f"Failed to get user expiration date in comfort format: {str(e)}")
        raise
    
@log_function_call(logger)
def insert_trial_date(tg_id):
    """
    Inserts a new user with a trial period.
    """
    trial_date = utils.timestamp.current_timestamp()
    try:
        return database.user.insert_trial_date(tg_id, trial_date)
    except Exception as e:
        logger.error(f"Failed to insert trial user: {str(e)}")
        raise

@log_function_call(logger)
def select_trial_date(tg_id):
    """
    Retrieves the trial date for a user.
    """
    try:
        return database.user.select_trial_date(tg_id)
    except Exception as e:
        logger.error(f"Failed to select trial date: {str(e)}")
        raise