#database/referrals.py
import const.const_db
from utils.logging_utils import setup_logger, retry_on_error, log_function_call

logger = setup_logger('referrals.database', 'database.log')


@log_function_call(logger)
def ensure_referral_record(tg_id, referrer_id):
    """
    Ensures a referral record exists for the given user (tg_id) and referrer (referrer_id):
      1) Referrer must exist in users table.
      2) referrer_id != tg_id.
      3) No symmetrical exchange (i.e., if (B->A) exists, we can't do (A->B)).
    Inserts a new record (referrer_id -> tg_id) if everything is fine.
    """
    logger.info(f"Attempting to ensure referral record for tg_id={tg_id}, referrer_id={referrer_id}.")

    # Check if the referrer_id is the same sas tg_id
    try:
        if not referrer_id.isdigit():
            logger.info(f"Invalid referral: referrer_id={referrer_id} in not a digit.")
            return False
        
        referrer_id, tg_id = int(referrer_id), int(tg_id)
        if referrer_id == tg_id:
            logger.info(f"Invalid referral: tg_id={tg_id} cannot refer themselves as referrer_id={referrer_id}.")
            return False
    except Exception as e:
        logger.exception(f"Error comparing tg_id and referrer_id: {str(e)}")
        raise

    # Verify that the referrer exists in the referrals table
    try:
        check_referrer_query = "SELECT 1 FROM referrals WHERE tg_id = %s"
        const.const_db.CUR.execute(check_referrer_query, (referrer_id,))
        referrer_exists = const.const_db.CUR.fetchone()
        if not referrer_exists:
            logger.info(f"Referrer does not exist: referrer_id={referrer_id}.")
            return False
    except Exception as e:
        logger.exception(f"Error checking if referrer exists for referrer_id={referrer_id}: {str(e)}")
        raise

    # Check for symmetrical referrals to prevent reciprocal referrals
    try:
        symmetrical_check_query = """
            SELECT 1
            FROM referrals
            WHERE referrer_tg_id = %s
              AND tg_id = %s
            LIMIT 1
        """
        const.const_db.CUR.execute(symmetrical_check_query, (tg_id, referrer_id))
        symmetrical_row = const.const_db.CUR.fetchone()
        if symmetrical_row:
            logger.info(f"Symmetrical referral detected between tg_id={tg_id} and referrer_id={referrer_id}.")
            return False
    except Exception as e:
        logger.exception(f"Error checking for symmetrical referrals between tg_id={tg_id} and referrer_id={referrer_id}: {str(e)}")
        raise

    # If all checks pass, the referral record is valid
    try:
        logger.info(f"Referral record is valid for tg_id={tg_id} with referrer_id={referrer_id}.")
        return True
    except Exception as e:
        logger.exception(f"Error finalizing referral record for tg_id={tg_id} and referrer_id={referrer_id}: {str(e)}")
        raise
    
@log_function_call(logger)
def insert_update_referrer(tg_id, referrer_id):
    """
    Sets or updates the referrer for a given user in referrals.
    """
    logger.info(f"Setting referrer {referrer_id} for tg_id={tg_id}.")
    try:
        query = """
        INSERT INTO referrals (tg_id, referrer_tg_id)
        VALUES (%s, %s)
        ON CONFLICT (tg_id)
        DO UPDATE SET referrer_tg_id = EXCLUDED.referrer_tg_id;
        """
        const.const_db.CUR.execute(query, (tg_id, referrer_id))
        logger.info(f"Successfully set referrer_id={referrer_id} for tg_id={tg_id}.")

        return True
    except Exception as e:
        logger.error(f"Error setting referrer_id: {str(e)}")
        raise

@log_function_call(logger)
def insert_user_referrals(tg_id):
    """
    Inserts a user into referrals table without a referrer.
    """
    try:
        insert_query = "INSERT INTO referrals (tg_id) VALUES (%s)"
        const.const_db.CUR.execute(insert_query, (tg_id,))
        logger.info(f"Successfully inserted user with tg_id={tg_id} into referrals.")
    except Exception as e:
        logger.error(f"Error in insert_user_referrals: {str(e)}")
        raise


@log_function_call(logger)
def get_balance(tg_id):
    """
    Retrieves the user's meow-coins balance from referrals table.
    """
    try:
        query = "SELECT meow_coins_balance FROM referrals WHERE tg_id = %s"
        const.const_db.CUR.execute(query, (tg_id,))
        row = const.const_db.CUR.fetchone()
        balance = row[0] if row else 0
        logger.info(f"Balance for tg_id={tg_id} is {balance}.")
        return balance
    except Exception as e:
        logger.error(f"Error in get_balance: {str(e)}")
        raise


@log_function_call(logger)
def select_users_by_referrer(referrer_tg_id):
    """
    Returns a list of tg_ids that were referred by the given referrer_tg_id.
    """
    try:
        query = """
        SELECT tg_id
        FROM referrals
        WHERE referrer_tg_id = %s
        """
        const.const_db.CUR.execute(query, (referrer_tg_id,))
        users = const.const_db.CUR.fetchall()
        result = [user[0] for user in users]
        logger.info(f"Found {result} users referred by {referrer_tg_id}.")
        return result
    except Exception as e:
        logger.error(f"Error in get_users_by_referrer: {str(e)}")
        raise


@log_function_call(logger)
def update_balance(tg_id, amount):
    """
    Updates (adds to) meow-coins balance for the specified tg_id.
    """
    try:
        query = "UPDATE referrals SET meow_coins_balance = meow_coins_balance + %s WHERE tg_id = %s"
        const.const_db.CUR.execute(query, (amount, tg_id))
        logger.info(f"Updated meow_coins_balance by {amount} for tg_id={tg_id}.")
    except Exception as e:
        logger.error(f"Error in update_balance: {str(e)}")
        raise


@log_function_call(logger)
def select_all_referrals_with_every_user():
    """
    Returns a list of (referrer_tg_id, array_of_referred_users).
    """
    try:
        const.const_db.CUR.execute("""
        SELECT referrer_tg_id, ARRAY_AGG(tg_id) AS referred_users
        FROM referrals
        WHERE referrer_tg_id IS NOT NULL
        GROUP BY referrer_tg_id
        """)
        results = const.const_db.CUR.fetchall()
        logger.info(f"Fetched {results} referrer records.")
        return results
    except Exception as e:
        logger.error(f"Error in get_all_referrals_with_every_user: {str(e)}")
        raise


@log_function_call(logger)
def select_user_exists(tg_id):
    """
    Checks if a record for tg_id exists in the referrals table.
    """
    try:
        query = "SELECT EXISTS(SELECT 1 FROM referrals WHERE tg_id = %s)"
        const.const_db.CUR.execute(query, (tg_id,))
        exists = const.const_db.CUR.fetchone()[0]
        logger.info(f"Referrals existence for tg_id={tg_id}: {exists}")
        return exists
    except Exception as e:
        logger.error(f"Error while checking user existence in referrals: {str(e)}")
        raise

