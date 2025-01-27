#profiles.py
from telebot import types
import middleware.connection
import middleware.user
from bot.bot_base_fun import expiry_date_view
from bot.handlers.subscriptions import show_subscription_options
from bot.bot_init import bot
from bot.messages import messages
from const.const_bot import (
    SUBSCRIPTIONS, GET_VLESS, LOGGER_PRESET, MAIN_MENU
)
from utils.logging_utils import log_function_call, setup_logger
from utils.config import PHOTO_my_subscription

logger = setup_logger('profile', 'bot.log')


@log_function_call(logger)
async def show_profile_options(call):
    """
    Показываем опции профиля (inline).
    """
    username = call.from_user.username
    chat_id = call.message.chat.id

    try:
        middleware.connection.login_db()
        exists = middleware.user.get_user_exists_in_user(chat_id)

        if exists:
            text = await expiry_date_view("expiration", chat_id)
        else:
            text = messages.get_random_message('profile_options')

        # Inline-кнопки
        markup = types.InlineKeyboardMarkup()
        btn_get_vless = types.InlineKeyboardButton(text=GET_VLESS, callback_data='profile_get_vless')
        btn_subscriptions = types.InlineKeyboardButton(text=SUBSCRIPTIONS, callback_data='profile_subscriptions')
        btn_main_menu = types.InlineKeyboardButton(MAIN_MENU, callback_data='menu_start')

        markup.add(btn_get_vless, btn_subscriptions)
        markup.add(btn_main_menu)

        await bot.send_photo(chat_id=chat_id, photo=PHOTO_my_subscription, caption=text, reply_markup=markup, parse_mode='Markdown')


    except Exception as e:
        logger.error(f"Error in show_profile_options: {str(e)}")
        raise


@log_function_call(logger)
@bot.callback_query_handler(func=lambda call: call.data.startswith('profile_'))
async def handle_profile_choice(call):
    """
    Обрабатываем нажатия на кнопки профиля.
    """
    data = call.data

    if data == 'profile_get_vless':
        await get_vless(call)
    elif data == 'profile_subscriptions':
        await show_subscription_options(call)
        
        
@log_function_call(logger)
async def get_vless(call):
    """
    Retrieves the user's VLESS profile if they have a subscription.
    """
    username = call.from_user.username
    chat_id = call.message.chat.id
    
    try:
        middleware.connection.login_db()
        if middleware.user.get_user_exists_in_user(chat_id):
            logger.info(f"User {username} found in DB.")
            
            data = middleware.user.send_vless(chat_id)
            text = f'🔑 {messages.get_random_message("vless_profile")}'
            await bot.send_message(chat_id=chat_id, text=f'{text}\n```{data}```', parse_mode='Markdown')
            
            logger.info("VLESS profile sent to user.")
        else:
            text = f'❌ {messages.get_random_message("no_profile")} 🐾'
            await bot.send_message(chat_id=chat_id, text=text)
            
            logger.info("User has no VLESS profile to send.")
            
    except Exception as e:
        logger.error(f"Error in get_vless: {str(e)}")
        raise
