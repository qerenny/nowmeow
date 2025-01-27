#instructions.py
from telebot import types
from bot.bot_init import bot
from bot.messages import messages
from const.const_bot import (
    INSTRUCTIONS_ANDROID, INSTRUCTIONS_IOS, INSTRUCTIONS_WINDOWS,
    INSTRUCTIONS_MACOS, INSTRUCTIONS_NEKOBOX, LOGGER_PRESET, MAIN_MENU
)
from utils.logging_utils import log_function_call, setup_logger
from utils.config import PHOTO_instructions

logger = setup_logger('instructions', 'bot.log')


@log_function_call(logger)
async def show_instructions(message):
    """
    Builds and sends instructions with inline keyboard for different platforms.
    """
    username = message.from_user.username
    chat_id = message.chat.id
    
    text = messages.get_random_message('device_select')

    try:
        markup = types.InlineKeyboardMarkup()
        btn_android = types.InlineKeyboardButton(f'🤖 {INSTRUCTIONS_ANDROID[0]}', url=INSTRUCTIONS_ANDROID[1])
        btn_ios = types.InlineKeyboardButton(f'🍎 {INSTRUCTIONS_IOS[0]}', url=INSTRUCTIONS_IOS[1])
        btn_windows = types.InlineKeyboardButton(f'🖥️ {INSTRUCTIONS_WINDOWS[0]}', url=INSTRUCTIONS_WINDOWS[1])
        btn_macos = types.InlineKeyboardButton(f'💻 {INSTRUCTIONS_MACOS[0]}', url=INSTRUCTIONS_MACOS[1])
        btn_nekobox = types.InlineKeyboardButton(f'📦 {INSTRUCTIONS_NEKOBOX[0]}', url=INSTRUCTIONS_NEKOBOX[1])

        markup.row(btn_android, btn_ios)
        markup.row(btn_windows, btn_macos)
        markup.row(btn_nekobox)

        btn_main_menu = types.InlineKeyboardButton(MAIN_MENU, callback_data='menu_start')
        markup.add(btn_main_menu)

        await bot.send_photo(chat_id=chat_id, photo=PHOTO_instructions, caption=text, reply_markup=markup)

    except Exception as e:
        logger.error(f"Error in show_instructions_fun: {str(e)}")
        raise