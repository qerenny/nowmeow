#support.py
from telebot import types
from bot.bot_init import bot

from bot.messages import messages
from const.const_bot import HELP, PHOTO_help, LOGGER_PRESET, MAIN_MENU
from utils.logging_utils import log_function_call, setup_logger

logger = setup_logger('support', 'bot.log')


@log_function_call(logger)
@bot.message_handler(func=lambda message: message.text in [HELP, 'help'], commands=['help'])
async def send_support_msg(call):
    """
    Отправка информации о поддержке + кнопка "В главное меню".
    """
    username = call.from_user.username
    chat_id = call.message.chat.id

    text = messages.get_random_message('support')
    try:
        markup = types.InlineKeyboardMarkup()
        btn_main_menu = types.InlineKeyboardButton(text=MAIN_MENU, callback_data='menu_start')
        markup.add(btn_main_menu)

        await bot.send_photo(chat_id=chat_id, photo=PHOTO_help, caption=text, reply_markup=markup)

    except Exception as e:
        logger.error(f"Error in send_support_msg: {str(e)}")
        raise