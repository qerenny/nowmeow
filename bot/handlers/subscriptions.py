#subscriptions.py
from telebot import types
import middleware.connection
import middleware.user
from bot.bot_init import bot
from bot.handlers.instructions import show_instructions
from bot.handlers.bonus_payment import prompt_payment_method
from bot.bot_base_fun import expiry_date_view
from bot.messages import messages
from const.const_bot import (
    TRIAL, MONTH1, MONTH3, MONTH6, YEAR1, DAY_3_TIMESTAMP,
    LOGGER_PRESET, MAIN_MENU
)
from utils.logging_utils import log_function_call, setup_logger
from utils.config import PHOTO_subscriptions

logger = setup_logger('subscriptions', 'bot.log')


@log_function_call(logger)
async def get_trial(call):
    """
    Выдаём пробную подписку (1 раз).
    """
    username = call.from_user.username
    chat_id = call.message.chat.id

    try:
        middleware.connection.login_3x()
        middleware.connection.login_db()

        if not middleware.user.get_user_exists_in_user(chat_id):
            data = middleware.user.create_or_update_user(chat_id, DAY_3_TIMESTAMP, username)
            middleware.user.insert_trial_date(chat_id)

            text2 = await expiry_date_view("trial_expiration", chat_id)
            await bot.send_message(chat_id=chat_id, text=text2, parse_mode='Markdown')
            
            text1 = f'🔑 {messages.get_random_message("trial_subscription")}'
            await bot.send_message(
                chat_id=chat_id,
                text=f'{text1}\n```{data}```',
                parse_mode='Markdown'
            )

            await show_instructions(call.message)
            logger.info(f"Trial subscription granted to user {chat_id}.")
        else:
            text = f'❌ {messages.get_random_message("trial_exists")}'
            await bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')
            logger.info(f"User already has a subscription or trial. tg_id={chat_id}")
    except Exception as e:
        logger.error(f"Error in get_trial: {str(e)}")
        raise



@log_function_call(logger)
async def show_subscription_options(call):
    """
    Предлагаем выбрать подписку, используя inline-кнопки, + "В главное меню".
    """
    username = call.from_user.username
    chat_id = call.message.chat.id

    try:
        middleware.connection.login_db()
        exists = middleware.user.get_user_exists_in_user(chat_id)
        text2 = messages.get_random_message('subscription_select')

        markup = types.InlineKeyboardMarkup(row_width=1)
        if not exists:
            btn_trial = types.InlineKeyboardButton(text=TRIAL, callback_data='sub_trial')
            markup.add(btn_trial)

        btn_month1 = types.InlineKeyboardButton(text=MONTH1['label'], callback_data='sub_month1')
        btn_month3 = types.InlineKeyboardButton(text=MONTH3['label'], callback_data='sub_month3')
        btn_month6 = types.InlineKeyboardButton(text=MONTH6['label'], callback_data='sub_month6')
        btn_year1 = types.InlineKeyboardButton(text=YEAR1['label'], callback_data='sub_year1')
        
        markup.add(btn_month1)
        markup.add(btn_month3)
        markup.add(btn_month6)
        markup.add(btn_year1)

        btn_main_menu = types.InlineKeyboardButton(text=MAIN_MENU, callback_data='menu_start')
        markup.add(btn_main_menu)

        await bot.send_photo(chat_id=chat_id, photo=PHOTO_subscriptions, caption=text2, reply_markup=markup, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error in show_subscription_options: {str(e)}")
        raise


@bot.callback_query_handler(func=lambda call: call.data.startswith('sub_'))
async def handle_sub_callback(call):
    """
    Обрабатываем выбор подписки (inline).
    """
    await bot.answer_callback_query(call.id)
    data = call.data

    if data == 'sub_trial':
        await get_trial(call)
    elif data == 'sub_month1':
        await prompt_payment_method(call, MONTH1)
    elif data == 'sub_month3':
        await prompt_payment_method(call, MONTH3)
    elif data == 'sub_month6':
        await prompt_payment_method(call, MONTH6)
    elif data == 'sub_year1':
        await prompt_payment_method(call, YEAR1)