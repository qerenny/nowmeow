#timestamp.py
from datetime import datetime, timedelta
import pytz
from dateutil.relativedelta import relativedelta
import const.const_bot
from utils.logging_utils import setup_logger, log_function_call

logger = setup_logger('json_fun', 'utils.log')

moscow = pytz.timezone('Europe/Moscow')
milliseconds = 1000


def str_to_relativedelta(period):
    try:
        if period == 'day3':
            return relativedelta(days=3)
        elif period == 'month1':
            return relativedelta(months=1)
        elif period == 'month3':
            return relativedelta(months=3)
        elif period == 'month6':
            return relativedelta(months=6)
        elif period == 'year1':
            return relativedelta(years=1)
        raise ValueError(f"Invalid period: {period}")
    except Exception as e:
        logger.error(f"Error in str_to_relativedelta: {e}")
        raise

def current_timestamp():
    try:
        return int(datetime.now(moscow).timestamp() * milliseconds)
    except Exception as e:
        logger.error(f"Error in current_timestamp: {e}")
        raise

def get_timestamp_with_reminder_time():
    try:
        boundry_ts = int((datetime.now(moscow) + timedelta(days=1)).timestamp() * 1000)
        boundary_ts_minus_hour = int((datetime.now(moscow) + timedelta(hours=23)).timestamp() * 1000)
        return boundary_ts_minus_hour, boundry_ts
    except Exception as e:
        logger.error(f"Error in get_timestamp_with_reminder_time: {e}")
        raise

def current_time():
    try:
        return datetime.now(moscow)
    except Exception as e:
        logger.error(f"Error in current_time: {e}")
        raise

def date_to_timestamp(date):
    try:
        return int(date.timestamp() * milliseconds)
    except Exception as e:
        logger.error(f"Error in date_to_timestamp: {e}")
        raise

def timestamp_to_date(timestamp):
    try:
        return datetime.fromtimestamp(timestamp / milliseconds, moscow)
    except Exception as e:
        logger.error(f"Error in timestamp_to_date: {e}")
        raise

def set_date(period):
    try:
        date = datetime.now(moscow) + str_to_relativedelta(period)
        return date_to_timestamp(date)
    except Exception as e:
        logger.error(f"Error in set_date: {e}")
        raise

def update_date(previous_expiry_date, period):
    try:
        previous_expiry_date_dt = datetime.fromtimestamp(previous_expiry_date / milliseconds, tz=moscow)
        if previous_expiry_date_dt <= current_time():
            previous_expiry_date_dt = current_time()
        updated_date = previous_expiry_date_dt + str_to_relativedelta(period)
        return date_to_timestamp(updated_date)
    except Exception as e:
        logger.error(f"Error in update_date: {e}")
        raise

def get_word_form(number, forms):
    try:
        n = abs(number) % 100
        n1 = n % 10
        if 10 < n < 20:
            return forms[2]
        if n1 == 1:
            return forms[0]
        if 2 <= n1 <= 4:
            return forms[1]
        return forms[2]
    except Exception as e:
        logger.error(f"Error in get_word_form: {e}")
        raise

def calculate_time_difference(user_date):
    try:
        user_date = timestamp_to_date(user_date)
        current_date = current_time()

        if user_date < current_date:
            return const.const_bot.EXPIRED

        diff = relativedelta(user_date, current_date)
        hours_diff = diff.hours

        result_parts = []
        if diff.years > 0:
            years_str = f"{diff.years} " + get_word_form(diff.years, ("год", "года", "лет"))
            result_parts.append(years_str)

        if diff.months > 0:
            months_str = f"{diff.months} " + get_word_form(diff.months, ("месяц", "месяца", "месяцев"))
            result_parts.append(months_str)

        if diff.days > 0:
            days_str = f"{diff.days} " + get_word_form(diff.days, ("день", "дня", "дней"))
            result_parts.append(days_str)

        if hours_diff > 0:
            hours_str = f"{hours_diff} " + get_word_form(hours_diff, ("час", "часа", "часов"))
            result_parts.append(hours_str)

        if not result_parts:
            return const.const_bot.LESS_THAN_HOUR

        return ", ".join(result_parts)
    except Exception as e:
        logger.error(f"Error in calculate_time_difference: {e}")
        raise