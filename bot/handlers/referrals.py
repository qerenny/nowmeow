#handlers/referrals.py
from telebot import types
import middleware.connection
import middleware.referrals
from bot.messages import messages
from bot.bot_init import bot
from const.const_bot import (
    REFERRALS, REFERRAL_INFO, REFERRAL_LINK, REFERRAL_RULES,
    LOGGER_PRESET, PHOTO_referral_program, MEOW_COINS_REFERRER_BONUS, MEOW_COINS_FIRST_USE_REF_CODE, MAIN_MENU
)
from utils.config import BOT_TG_ID
from utils.logging_utils import setup_logger, log_function_call

logger = setup_logger('referrals.handlers', 'bot.log')


@log_function_call(logger)
async def show_referrals_menu(call):
    """
    Показывает меню реферальной программы (inline).
    """
    username = call.from_user.username
    chat_id = call.message.chat.id

    try:
        markup = types.InlineKeyboardMarkup()
        btn_link = types.InlineKeyboardButton(text=REFERRAL_LINK, callback_data='referrals_link')
        btn_rules = types.InlineKeyboardButton(text=REFERRAL_RULES, callback_data='referrals_rules')
        btn_main_menu = types.InlineKeyboardButton(text=MAIN_MENU, callback_data='menu_start')

        markup.add(btn_link, btn_rules)
        markup.add(btn_main_menu)
        referral_info_text = await referral_info(call)
        
        text = messages.get_random_message('referral_greetings') + "\n" + referral_info_text
        await bot.send_photo(chat_id=chat_id, photo=PHOTO_referral_program, caption=text, reply_markup=markup, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Error in show_referrals_menu: {str(e)}")
        raise


# Обработка нажатий на кнопки referrals_info, referrals_link, referrals_rules
@bot.callback_query_handler(func=lambda call: call.data in ['referrals_info', 'referrals_link', 'referrals_rules'])
async def referrals_menu_callback(call):
    """
    Обрабатывает нажатия на кнопки REFERRAL_INFO, REFERRAL_LINK, REFERRAL_RULES.
    """
    await bot.answer_callback_query(call.id)
    data = call.data

    if data == 'referrals_info':
        await referral_info(call)
    elif data == 'referrals_link':
        await referral_link(call)
    elif data == 'referrals_rules':
        await referral_rules(call)


@log_function_call(logger)
async def referral_info(call):
    """
    Shows user's referral stats: active referrals count and current balance.
    """
    username = call.from_user.username
    chat_id = call.message.chat.id

    try:
        middleware.connection.login_db()
        
        num_of_users = middleware.referrals.select_active_users_by_referrer(chat_id)
        if not num_of_users:
            num = 0
        else:
            num = len(num_of_users)
        balance = middleware.referrals.get_balance(chat_id)
        
        text = messages.get_random_message('referral_info')
        formatted_text = text.format(num_of_users=num, balance=balance, bonus=MEOW_COINS_REFERRER_BONUS*num)
        logger.info(f"Referral info sent: active={num}, balance={balance}.")

        return formatted_text

    except Exception as e:
        logger.error(f"Error in referral_info: {str(e)}")
        raise

@log_function_call(logger)
async def referral_link(call):
    """
    Provides user with a personal referral link.
    """
    username = call.from_user.username
    chat_id = call.message.chat.id
    
    try:
        link = f"https://t.me/{BOT_TG_ID}?start={chat_id}"
        text = messages.get_random_message('referral_link') + f"\n{link}"
        await bot.send_message(chat_id=chat_id, text=text)
        logger.info(f"Referral link sent to user: {link}")
    except Exception as e:
        logger.error(f"Error in referral_link: {str(e)}")
        raise

@log_function_call(logger)
async def referral_rules(call):
    """
    Sends referral usage rules or instructions.
    """
    username = call.from_user.username
    chat_id = call.message.chat.id

    try:
        text = messages.get_random_message('referral_rules')
        await bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in referral_rules: {str(e)}")
        raise

@log_function_call(logger)
async def referrals_start(message, referral_code):
    """
    Processes referral code usage or updating for a new or existing user.
    """
    username = message.from_user.username
    chat_id = message.chat.id
    try:
        middleware.connection.login_db()
        exists_in_users = middleware.user.get_user_exists_in_user(chat_id)
        exists_in_referrals = middleware.referrals.select_user_exists(chat_id)
        code_applied = middleware.referrals.get_refferer(chat_id)
    except Exception as e:
        logger.error(f"Error checking user existence for chat_id={chat_id}: {str(e)}")
        raise
    try:
        if not exists_in_users:
            referrer_text = messages.get_random_message('referral_code_used')
            ref_code_length = len(referral_code)

            if ref_code_length > 1:
                # Ensure referral record
                try:
                    approved = middleware.referrals.ensure_referral_record(chat_id, referral_code[1])
                except Exception as e:
                    logger.error(f"Unexpected error ensuring referral record for chat_id={chat_id}: {str(e)}")
                    raise

                if approved:
                    code = referral_code[1]
                    
                    if not exists_in_referrals or (exists_in_referrals and not code_applied):
                        logger.info(f"User does not exist and is using referral code: {code}")
                        try:
                            middleware.referrals.insert_update_referrer(chat_id, code)
                        except Exception as e:
                            logger.error(f"Error inserting/updating referrer for chat_id={chat_id} with code={code}: {str(e)}")
                            raise

                        user_text = messages.get_random_message('referral_code_activated')

                        try:
                            middleware.referrals.update_balance(chat_id, MEOW_COINS_FIRST_USE_REF_CODE)
                            logger.info(f"Referral code activated: {code} for chat_id={chat_id}")
                        except Exception as e:
                            logger.error(f"Error updating balance for chat_id={chat_id} with referral_code={code}: {str(e)}")
                            raise

                    else:
                        logger.info(f"User exists and is using referral code: {code}")
                        try:
                            middleware.referrals.insert_update_referrer(chat_id, code)
                        except Exception as e:
                            logger.error(f"Error updating referrer for chat_id={chat_id} with code={code}: {str(e)}")
                            raise

                        user_text = messages.get_random_message('referral_code_changed')

                        logger.info(f"Referral code changed to: {code} for chat_id={chat_id}")

                    await bot.send_message(chat_id=code, text=referrer_text, parse_mode="Markdown")
                    await bot.send_message(chat_id=chat_id, text=user_text, parse_mode="Markdown")

                else:
                    await inser_user_referrals(chat_id, exists_in_referrals)
                    user_text = messages.get_random_message('invalid_referral_code')
                    await bot.send_message(chat_id=chat_id, text=user_text)

            elif not exists_in_referrals:
                await inser_user_referrals(chat_id, exists_in_referrals)
            else:
                logger.info(f"User already exists in referrals table for chat_id={chat_id}.")

        else:
            logger.info(f"User already exists in users table for chat_id={chat_id}.")

    except Exception as e:
        logger.error(f"Unhandled error in referrals_start for chat_id={chat_id}: {str(e)}")
        raise
    
    
async def inser_user_referrals(chat_id, exists_in_referrals):
    if not exists_in_referrals:
        try:
            middleware.referrals.insert_user_referrals(chat_id)
            logger.info(f"Inserted user into referrals without a referrer code for chat_id={chat_id}.")
        except Exception as e:
            logger.error(f"Error inserting user into referrals for chat_id={chat_id}: {str(e)}")
            raise