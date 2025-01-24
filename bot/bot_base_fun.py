#bot_base_fun.py
from bot.bot_init import bot
from const.const_bot import PAYMENT_STATE
from utils.logging_utils import setup_logger
import middleware.user
from bot.messages import messages

logger = setup_logger('base_fun', 'bot.log')

async def remove_message(tg_id, msg_id: int):
    try:
        logger.info(f"Removing message with ID {msg_id} for user {tg_id}.")
        await bot.delete_message(tg_id, msg_id)
    except Exception as e:
        logger.error(f"Could not remove message {msg_id} in chat {tg_id}: {e}")
        
async def expiry_date_view(type_of_message, tg_id):
    date = middleware.user.get_users_expiration_date(tg_id)
    comfort_format_expiration_date = middleware.user.get_users_expiration_date_to_comfort_format(tg_id)
    text = (
        f'{messages.get_random_message(type_of_message)}\n'
        f'├─ Осталось: `{comfort_format_expiration_date}` 🐱\n'
        f'└─ Дата истечения: `{date}` ⏰'
        )
            
    return text