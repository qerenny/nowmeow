#admin.py
import os

from telebot import types
from telebot import types
import middleware.connection
from utils.logging_utils import log_function_call, setup_logger
import middleware.user
from bot.handlers.instructions import show_instructions
from bot.handlers.bonus_payment import prompt_payment_method
from bot.bot_base_fun import expiry_date_view
from bot.messages import messages
from const.const_bot import (
    TRIAL, MONTH1, MONTH3, MONTH6, YEAR1, DAY_3_TIMESTAMP,
    LOGGER_PRESET, PHOTO_subscriptions, MAIN_MENU
)
from bot.bot_init import bot
from utils.config import BOT_ADMIN_IDS

logger = setup_logger('admin', 'bot.log')

# Хранилище "название_файла -> file_id"
photos_db = {}


@log_function_call(logger)
@bot.message_handler(commands=['upload_photos'])
async def upload_photos(message: types.Message):
    """
    Admin-only function that sends all photos from a local folder
    to Telegram and collects their file_id (hash).
    """
    if message.chat.id not in BOT_ADMIN_IDS:
        await bot.send_message(chat_id=message.chat.id, text="У вас нет прав для использования этой команды.")
        return

    folder_path = "bot/handlers/photo"  # Папка, где лежат ваши изображения
    if not os.path.exists(folder_path):
        await bot.send_message(chat_id=message.chat.id, text=f"Папка '{folder_path}' не найдена.")
        return

    file_list = [f for f in os.listdir(folder_path) if not f.startswith(".")]
    if not file_list:
        await bot.send_message(chat_id=message.chat.id, text=f"В папке '{folder_path}' нет изображений.")
        return

    await bot.send_message(chat_id=message.chat.id, text=f"Загружаю {len(file_list)} фото...")

    count = 0
    for filename in file_list:
        full_path = os.path.join(folder_path, filename)


        if not os.path.isfile(full_path):
            continue

        try:
            with open(full_path, 'rb') as photo:
                msg = await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=photo,
                    caption=filename
                )
                # 4. Сохраняем file_id в словарь
                file_id = msg.photo[-1].file_id
                photos_db[filename] = file_id
                count += 1
        except Exception as e:
            await bot.send_message(
                chat_id=message.chat.id,
                text=f"Не удалось загрузить {filename}: {e}"
            )

    await bot.send_message(
        chat_id=message.chat.id,
        text=f"✅ Загружено {count} изображений. Все file_id сохранены локально."
    )


@bot.message_handler(commands=['show_photos'])
async def show_photos(message: types.Message):
    if message.chat.id not in BOT_ADMIN_IDS:
        await bot.send_message(chat_id=message.chat.id, text="У вас нет прав для использования этой команды.")
        return

    if not photos_db:
        await bot.send_message(chat_id=message.chat.id, text="Ни одно изображение не загружено.")
        return

    text_lines = [f"{name} -> {file_id}" for name, file_id in photos_db.items()]
    full_text = "\n".join(text_lines)
    await bot.send_message(chat_id=message.chat.id, text=f"Имеются записи:\n\n{full_text}")
        
        
@log_function_call(logger)
@bot.message_handler(commands=['message'])
async def send_to_everyone_message(message: types.Message):
    """
    Admin-only function that sends a message to all users.
    """
    args = message.text.split()
    if len(args) < 2:
        await bot.send_message(
            chat_id=message.chat.id,
            text="Использование: /message <сообщение>"
        )
        return

    text = " ".join(args[1:])
    logger.info(f"Sending message to all users: {text}")
    users = middleware.user.select_all_users()
    for user in users:
        try:
            logger.info(f"Sending message to user {user[0]}")
            await bot.send_message(chat_id=user[0], text=text)
        except Exception as e:
            logger.error(f"Failed to send message to user {user[0]}: {str(e)}")

    await bot.send_message(chat_id=message.chat.id, text=f"Сообщение отправлено всем пользователям.\n\n{len(users)}")
    
    
@log_function_call(logger)
@bot.message_handler(commands=['message_active'])
async def send_to_active_users_message(message: types.Message):
    """
    Admin-only function that sends a message to all active users.
    """
    args = message.text.split()
    if len(args) < 2:
        await bot.send_message(
            chat_id=message.chat.id,
            text="Использование: /message_active <сообщение>"
        )
        return

    text = " ".join(args[1:])
    users = middleware.user.select_all_active_users()
    for user in users:
        try:
            await bot.send_message(chat_id=user[0], text=text)
        except Exception as e:
            logger.error(f"Failed to send message to user {user[0]}: {str(e)}")

    await bot.send_message(chat_id=message.chat.id, text=f"Сообщение отправлено всем активным пользователям.\n\n{len(users)}")

# @log_function_call(logger) 
# @bot.message_handler(commands=['renew'])
# async def renew_subscription(message: types.Message):
#     args = message.text.split()

#     chat_id = args[1]
#     period = args[2]
#     my_tg_id = message.chat.id
#     username = message.from_user.username

#     try:
        
#         # Разделяем текст сообщения по пробелам        
#         # Проверяем, что пользователь передал достаточно аргументов
#         if len(args) < 3:
#             await bot.send_message(
#                 chat_id=message.chat.id, 
#                 text="Использование: /renew <tg_id> <period>"
#             )
#             return
        
#         middleware.connection.login_3x()
#         middleware.connection.login_db()

#         data = middleware.user.create_or_update_user(chat_id, period, username)

#         text2 = await expiry_date_view("expiration", chat_id)
#         await bot.send_message(chat_id=chat_id, text=text2, parse_mode='Markdown')

        
#         text1 = f'🔑 {messages.get_random_message("trial_subscription")}'
#         await bot.send_message(
#             chat_id=chat_id,
#             text=f'{text1}\n```{data}```',
#             parse_mode='Markdown'
#         )

#         logger.info(f"Trial subscription granted to user {chat_id}.")

#     except Exception as e:
#         logger.error(f"Error in get_trial: {str(e)}")
#         raise