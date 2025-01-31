# start.py

from telebot import types
import middleware.connection
import middleware.referrals
import middleware.user

from bot.handlers.instructions import show_instructions
from bot.handlers.profiles import show_profile_options
from bot.handlers.referrals import show_referrals_menu
from bot.handlers.support import send_support_msg
from bot.handlers.referrals import referrals_start
from bot.bot_init import bot
from bot.messages import messages
from const.const_bot import (
    PROFILE, HELP, INSTRUCTIONS, REFERRALS,
    PHOTO_PATH, LOGGER_PRESET, PAYMENT_STATE, SUBSCRIPTIONS
)
from utils.logging_utils import log_function_call, setup_logger
from bot.bot_base_fun import remove_message
from utils.config import PHOTO_menu

logger = setup_logger('start', 'bot.log')


@log_function_call(logger)
@bot.message_handler(commands=['start'])
async def send_start(message):
    """
    Handles the /start command: checks the referral code and displays the main menu.
    """
    username = message.from_user.username
    chat_id = message.chat.id

    try:
        # Parse the referral code from the message
        try:
            referral_code = message.text.split()
            logger.info(f"Processing /start command with referral_code: {referral_code} for chat_id={chat_id}")
        except Exception as e:
            logger.error(f"Error parsing referral_code for chat_id={chat_id}: {str(e)}")
            raise

        try:
            await referrals_start(message, referral_code)
        except Exception as e:
            logger.error(f"Error during referral processing for chat_id={chat_id}: {str(e)}")
            raise

        await send_main_menu(message)

    except Exception as e:
        logger.exception(f"Unhandled error in send_start for chat_id={chat_id}: {str(e)}")
        raise

@log_function_call(logger)
async def send_main_menu(message):
    """
    Отправляет главное меню пользователю без обработки реферальных кодов и удаляет старое меню.
    """
    username = message.from_user.username
    chat_id = message.chat.id
    
    text = messages.get_random_message('greetings')
    try:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_profile = types.InlineKeyboardButton(text=PROFILE, callback_data='menu_profile')
        btn_help = types.InlineKeyboardButton(text=HELP, callback_data='menu_help')
        btn_instructions = types.InlineKeyboardButton(text=INSTRUCTIONS, callback_data='menu_instructions')
        btn_referrals = types.InlineKeyboardButton(text=REFERRALS, callback_data='menu_referrals')
        btn_subscriptions = types.InlineKeyboardButton(text=SUBSCRIPTIONS, callback_data='profile_subscriptions')


        markup.add(btn_subscriptions, btn_profile)
        markup.add(btn_referrals)
        markup.add(btn_help, btn_instructions)

        
        sent_msg = await bot.send_photo(
            chat_id=chat_id,
            photo=PHOTO_menu,
            caption=text,
            reply_markup=markup
        )
    except Exception as e:
        logger.error(f"Error in send_main_menu: {str(e)}")
        raise


@log_function_call(logger)
@bot.callback_query_handler(func=lambda call: call.data in [
    'menu_profile', 'menu_help', 'menu_instructions', 'menu_referrals', 'menu_start'
])
async def handle_menu_callback(call):
    """
    Обрабатываем нажатия на кнопки PROFILE, HELP, INSTRUCTIONS, REFERRALS и MAIN MENU (inline).
    """
    try:
        # Убираем "часики" Telegram
        await bot.answer_callback_query(call.id)
        
        tg_id = call.message.chat.id

        if tg_id in PAYMENT_STATE:
            try:
                invoice_msg_id = PAYMENT_STATE[tg_id].get("invoice_msg_id")
                if invoice_msg_id:
                    await remove_message(tg_id, invoice_msg_id)
                    PAYMENT_STATE[tg_id]["invoice_msg_id"] = None
                    logger.info(f"Invoice {invoice_msg_id} removed because user pressed any inline button.")

                old_prompt = PAYMENT_STATE[tg_id].get("choose_payment_method_id")
                if old_prompt:
                    await remove_message(tg_id, old_prompt)
                    PAYMENT_STATE[tg_id]["choose_payment_method_id"] = None
            except Exception as e:
                logger.error(f"Error handling payment state cleanup: {str(e)}")

        if call.data == 'menu_profile':
            await show_profile_options(call)
        elif call.data == 'menu_help':
            await send_support_msg(call)
        elif call.data == 'menu_instructions':
            await show_instructions(call.message)
        elif call.data == 'menu_referrals':
            await show_referrals_menu(call)
        elif call.data == 'menu_start':
            await send_main_menu(call.message)

            
    except Exception as e:
        logger.error(f"Critical error in handle_menu_callback: {str(e)}")