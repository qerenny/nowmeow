#tasks.py
import asyncio
from telebot import types
import middleware.user
from datetime import datetime, timedelta
from bot.bot_init import bot
from database.user import select_all_users
from utils import timestamp
from utils.logging_utils import setup_logger, log_function_call
import database.referrals
import database.user
from bot.bot_base_fun import expiry_date_view
import const.const_bot  # где лежит MEOW_COINS_REFERRER_BONUS (или любое другое значение)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from bot.bot_init import bot



logger = setup_logger('tasks', 'bot.log')

@log_function_call(logger)
async def send_reminer_button(tg_id):
    """
    Sends a reminder button to user.
    """
    try:
        markup = types.InlineKeyboardMarkup()
        btn_renew = types.InlineKeyboardButton(text="🆙 Обновить подписку", callback_data="profile_subscriptions")
        markup.add(btn_renew)
        text = await expiry_date_view("renewal_reminder", tg_id)

        await bot.send_message(chat_id=tg_id, text=text, parse_mode='Markdown', reply_markup=markup)

    except Exception as e:
        logger.error(f"Error in send_reminer_button: {str(e)}")
    
    
@log_function_call(logger)
async def reminder_task():
    """
    Background task that checks expiring subscriptions and reminds users to renew.
    """
    while True:
        await asyncio.sleep(3540)
        try:
            boundary_ts_minus_hour, boundary_ts = timestamp.get_timestamp_with_reminder_time()
            users = select_all_users()

            for user in users:
                tg_id = user[0]
                expiry_ts = user[3]
                if boundary_ts_minus_hour < expiry_ts <= boundary_ts:
                    await send_reminer_button(tg_id)
                    logger.info(f"Renewal reminder sent to tg_id={tg_id}.")
        except Exception as e:
            logger.error(f"Error in reminder_task: {str(e)}")



THREE_DAYS_MS = 3 * 24 * 60 * 60 * 1000  # 3 дня в миллисекундах

@log_function_call(logger)
def monthly_referral_bonus():
    """
    Function to credit bonuses to referrers for each active user.
    A user is NOT considered active if the difference (date - trial_date) <= 3 days.
    Called at the beginning of the month (or according to your schedule).
    """
    logger.info("Starting monthly referral bonus credits")

    try:
        referrals_info = database.referrals.select_all_referrals_with_every_user()
        logger.info(f"Total referrers in the system: {len(referrals_info)}")

        now_ts = timestamp.current_timestamp()
        total_bonuses_given = 0

        for row in referrals_info:
            if not row:
                continue
            referrer_tg_id = row[0]
            referred_users = row[1] or []

            # Count how many users are considered "active" and "not trial"
            active_valid_users_count = 0

            for user_tg_id in referred_users:
                # Get the subscription end date (date) and the trial start date (trial_date)
                user_date = database.user.select_user_date(user_tg_id)       # returns int or None
                user_trial_date = database.user.select_trial_date(user_tg_id)  # also int or None

                # If there is no subscription at all:
                if not user_date:
                    continue

                # If the subscription (date) has already expired:
                if user_date <= now_ts:
                    continue

                # If the user has a trial_date, check the difference
                # If (date - trial_date) <= THREE_DAYS_MS -> user remained on trial
                if user_trial_date and (user_date - user_trial_date) <= THREE_DAYS_MS:
                    continue

                # Otherwise, the user is active and not on trial
                active_valid_users_count += 1

            # Credit the bonus if applicable
            if active_valid_users_count > 0:
                # Suppose, for each active paid user, the referrer receives MEOW_COINS_REFERRER_BONUS
                bonus_amount = active_valid_users_count * const.const_bot.MEOW_COINS_REFERRER_BONUS
                database.referrals.update_balance(referrer_tg_id, bonus_amount)
                logger.info(
                    f"Referrer {referrer_tg_id} credited {bonus_amount} coins "
                    f"for {active_valid_users_count} active users."
                )
                total_bonuses_given += bonus_amount

        logger.info(f"Bonus credits completed. Total credited: {total_bonuses_given} coins.")

    except Exception as e:
        logger.error(f"monthly_referral_bonus: An error occurred while crediting bonuses: {str(e)}")

# Background task for monthly referral bonus credits
def setup_scheduler():
    """
    Sets up and starts the APScheduler task scheduler.
    """
    try:
        scheduler = AsyncIOScheduler()
        
        # Set up trigger: first day of each month at 01:00
        trigger = CronTrigger(day=1, hour=1, minute=0)

        # Add task to scheduler
        scheduler.add_job(
            monthly_referral_bonus,
            trigger=trigger,
            name="Monthly Referral Bonus",
            replace_existing=True
        )

        # Start scheduler
        scheduler.start()
        logger.info("Task scheduler started. 'Monthly Referral Bonus' task scheduled for the first day of each month at 01:00.")
    except Exception as e:
        logger.error(f"Failed to setup scheduler: {str(e)}")
