#database/user.py
import const.const_db
from utils.logging_utils import setup_logger, retry_on_error, log_function_call

logger = setup_logger('user.database', 'database.log')

@log_function_call(logger)
def insert_user(tg_id, user_id, email, date, sub_id, vless_profile, login_date):
    """
    Inserts a new user record into the users table.
    """
    try:
        insert_query = """
        INSERT INTO users (tg_id, user_id, email, date, sub_id, vless_profile, login_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        const.const_db.CUR.execute(insert_query, (tg_id, user_id, email, date, sub_id, vless_profile, login_date))
        logger.info(f"Successfully inserted user with tg_id={tg_id}.")
    except Exception as e:
        logger.error(f"Error while inserting user: {str(e)}")
        raise

@log_function_call(logger)
def insert_trial_date(tg_id, trial_date):
    """
    Inserts a trial date for a user in the users table.
    """
    try:
        update_query = """
        UPDATE users
        SET trial_date = %s
        WHERE tg_id = %s
        """
        const.const_db.CUR.execute(update_query, (trial_date, tg_id))
        logger.info(f"Successfully inserted trial date for tg_id={tg_id}.")
    except Exception as e:
        logger.error(f"Error while inserting trial date: {str(e)}")
        raise
    
@log_function_call(logger)
def select_trial_date(tg_id):
    """
    Retrieves the trial date for a user.
    """
    try:
        query = "SELECT trial_date FROM users WHERE tg_id = %s;"
        const.const_db.CUR.execute(query, (tg_id,))
        trial_date = const.const_db.CUR.fetchone()
        logger.info(f"Retrieved ({trial_date}) from the database.")
        return trial_date[0] if trial_date else None
    except Exception as e:
        logger.error(f"Error while selecting trial date: {str(e)}")
        raise

@log_function_call(logger)
def select_user(tg_id):
    """
    Retrieves user data from the users table by tg_id.
    """
    try:
        query = "SELECT * FROM users WHERE tg_id = %s"
        const.const_db.CUR.execute(query, (tg_id,))
        data = const.const_db.CUR.fetchall()
        if not data:
            logger.warning(f"User with tg_id={tg_id} not found.")
            return None
        logger.info(f"Successfully retrieved user data for tg_id={tg_id}.")
        return data[0]
    except Exception as e:
        logger.error(f"Error while selecting user: {str(e)}")
        raise


@log_function_call(logger)
def update_user_date(date, tg_id):
    """
    Updates the 'date' field (subscription expiry) for a user.
    """
    try:
        update_query = """
        UPDATE users
        SET date = %s
        WHERE tg_id = %s
        """
        const.const_db.CUR.execute(update_query, (date, tg_id))
        logger.info(f"Successfully updated date for user with tg_id={tg_id}.")
    except Exception as e:
        logger.error(f"Error while updating user date: {str(e)}")
        raise


@log_function_call(logger)
def select_user_exists(tg_id):
    """
    Checks if a user exists in the users table.
    """
    try:
        query = "SELECT EXISTS(SELECT 1 FROM users WHERE tg_id = %s)"
        const.const_db.CUR.execute(query, (tg_id,))
        exists = const.const_db.CUR.fetchone()[0]
        logger.info(f"User existence for tg_id={tg_id}: {exists}.")
        return exists
    except Exception as e:
        logger.error(f"Error while checking user existence: {str(e)}")
        raise


@log_function_call(logger)
def select_user_vless_profile(tg_id):
    """
    Retrieves the vless_profile field for a user.
    """
    try:
        query = "SELECT vless_profile FROM users WHERE tg_id = %s;"
        const.const_db.CUR.execute(query, (tg_id,))
        vless = const.const_db.CUR.fetchone()
        logger.info(f"Retrieved ({vless}) from the database.")
        return vless[0] if vless else None
    except Exception as e:
        logger.error(f"Error while selecting vless profile: {str(e)}")
        raise


@log_function_call(logger)
def select_user_date(tg_id):
    """
    Retrieves the date (subscription expiry) for a user.
    """
    try:
        query = "SELECT date FROM users WHERE tg_id = %s;"
        const.const_db.CUR.execute(query, (tg_id,))
        date = const.const_db.CUR.fetchone()
        logger.info(f"Retrieved ({date}) from the database.")
        return date[0] if date else None
    except Exception as e:
        logger.error(f"Error while selecting date: {str(e)}")
        raise


@log_function_call(logger)
def select_all_users():
    """
    Retrieves all users from the users table.
    """
    try:
        query = "SELECT * FROM users"
        const.const_db.CUR.execute(query)
        data = const.const_db.CUR.fetchall()
        logger.info(f"Retrieved {len(data)} users from the database.")
        return data
    except Exception as e:
        logger.error(f"Error while retrieving all users: {str(e)}")
        raise