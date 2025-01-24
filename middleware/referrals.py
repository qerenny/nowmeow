#middleware/referrals.py
import database.referrals
from utils.logging_utils import log_function_call, setup_logger
from utils.timestamp import current_timestamp
import middleware.user

logger = setup_logger('referrals.middleware', 'middleware.log')

@log_function_call(logger)
def ensure_referral_record(tg_id, referrer_id):
    """
    Ensures a user has a referral record, optionally tied to a referrer.
    """
    try:
        return database.referrals.ensure_referral_record(tg_id, referrer_id)
    except Exception as e:
        logger.error(f"Error ensuring referral record: {e}")

@log_function_call(logger)
def insert_user_referrals(tg_id):
    """
    Inserts a user into referrals table if not present.
    """
    try:
        database.referrals.insert_user_referrals(tg_id)
    except Exception as e:
        logger.error(f"Error inserting user referrals: {e}")

@log_function_call(logger)
def select_user_exists(tg_id):
    """
    Checks if a user record exists in referrals table.
    """
    try:
        return database.referrals.select_user_exists(tg_id)
    except Exception as e:
        logger.error(f"Error checking user existence: {e}")

@log_function_call(logger)
def insert_update_referrer(tg_id, referrer_id):
    """
    Sets or updates the referrer for a user in referrals.
    """
    try:
        return database.referrals.insert_update_referrer(tg_id, referrer_id)
    except Exception as e:
        logger.error(f"Error updating referrer: {e}")

@log_function_call(logger)
def select_users_by_referrer(referrer_id):
    """
    Retrieves a list of tg_ids referred by referrer_id.
    """
    try:
        return database.referrals.select_users_by_referrer(referrer_id)
    except Exception as e:
        logger.error(f"Error selecting users by referrer: {e}")

@log_function_call(logger)
def select_active_users_by_referrer(referrer_id):
    """
    Retrieves a list of active users referred by referrer_id.
    """
    try:
        active_users = []
        users = select_users_by_referrer(referrer_id)
        for user_id in users:
            try:
                date = middleware.user.select_user_date(user_id)
                date = int(date) if date else None
                if date and date > current_timestamp():
                    active_users.append(user_id)
            except Exception as e:
                logger.error(f"Error processing user {user_id}: {e}")
        logger.info(f"Retrieving all users referred by {referrer_id}.")
        return active_users
    except Exception as e:
        logger.error(f"Error selecting active users: {e}")

@log_function_call(logger)
def get_balance(tg_id):
    """
    Retrieves meow-coins balance for the user in referrals.
    """
    try:
        return database.referrals.get_balance(tg_id)
    except Exception as e:
        logger.error(f"Error getting balance: {e}")

@log_function_call(logger)
def update_balance(tg_id, amount):
    """
    Adds meow-coins to user's balance in referrals.
    """
    try:
        database.referrals.update_balance(tg_id, amount)
    except Exception as e:
        logger.error(f"Error updating balance: {e}")
