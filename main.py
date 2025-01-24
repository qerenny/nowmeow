#main.py
import asyncio

import middleware.connection
from bot.bot_init import bot
import utils.config
from bot.bot_base_fun import remove_message
from bot.tasks import reminder_task, setup_scheduler
from utils.logging_utils import setup_logger
from bot.handlers import instructions, payments, profiles, referrals, start, subscriptions, support, admin, bonus_payment

logger = setup_logger('main', 'main.log')

async def run_bot():
    """
    Runs the Telegram bot with automatic reconnection and reminder task.
    """
    logger.info("Starting reminder_task in background.")
    asyncio.create_task(reminder_task())
    setup_scheduler()

    # Подключаемся к 3X-UI и БД один раз
    try:
        logger.info("Logging in to 3X-UI and DB at bot startup.")
        middleware.connection.login_3x()
        middleware.connection.login_db()
        logger.info("Connections to 3X-UI and DB established successfully.")
    except Exception as e:
        logger.error(f"Failed initial login: {str(e)}")
        raise

    while True:
        try:
            logger.info("Starting bot polling...")
            await bot.polling()
        except Exception as e:
            logger.error(f"Bot polling error: {str(e)}")
            logger.info("Attempting to restart bot in 5 seconds...")
            await asyncio.sleep(5)
        finally:
            try:
                middleware.connection.logout()
            except Exception as e:
                logger.error(f"Error during logout: {str(e)}")

def main():
    """
    Main entry point to run the asynchronous bot.
    """
    logger.info("Bot main function started.")
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (KeyboardInterrupt).")
    except Exception as e:
        logger.error(f"Critical error in main: {str(e)}")
        raise
    logger.info("Bot main function ended.")

if __name__ == '__main__':
    main()