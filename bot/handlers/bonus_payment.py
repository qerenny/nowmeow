#bonus_payment.py - обработчики для оплаты бонусами
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Update
from utils.logging_utils import log_function_call, setup_logger
from bot.bot_init import bot
from bot.handlers.payments import buy
from const.const_bot import PAYMENT_STATE, MINMUM_BONUS_PAYMENT
from bot.bot_base_fun import remove_message
import middleware.referrals

logger = setup_logger('bonus_payment', 'bot.log')


@log_function_call(logger)
async def prompt_payment_method(call, product):
    try:
        username = call.from_user.username
        chat_id = call.message.chat.id

        if chat_id in PAYMENT_STATE:
            old_invoice = PAYMENT_STATE[chat_id].get("invoice_msg_id")
            if old_invoice:
                await remove_message(chat_id, old_invoice)
                PAYMENT_STATE[chat_id]["invoice_msg_id"] = None
            old_prompt = PAYMENT_STATE[chat_id].get("choose_payment_method_id")
            if old_prompt:
                await remove_message(chat_id, old_prompt)
                PAYMENT_STATE[chat_id]["choose_payment_method_id"] = None
        else:
            PAYMENT_STATE[chat_id] = {}

        PAYMENT_STATE[chat_id] = {
            "state": None,
            "full_price": product["amount"],  
            "description": product["label"],
            "bonus_input": 0,
            "invoice_msg_id": None,
            "choose_payment_method_id": None,
            "invoice_created_at": time.time(),
            "payload": product["payload"]
        }

        balance = middleware.referrals.get_balance(chat_id)

        text = (
            f"{product['label']}\n"
            f"├─ Цена: `{product['amount'] // 100}` руб.\n"
            f"└─ На вашем бонусном счёте: `{balance}` коинов.\n\n"
            "Выберите способ оплаты:"
        )

        markup = InlineKeyboardMarkup()
        btn_full = InlineKeyboardButton("Оплатить полную сумму", callback_data="pay_full")
        btn_bonus = InlineKeyboardButton("Использовать бонусы", callback_data="pay_bonus")
        markup.add(btn_full, btn_bonus)

        sent_msg = await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        PAYMENT_STATE[chat_id]["choose_payment_method_id"] = sent_msg.message_id
    except Exception as e:
        logger.error(f"Error in prompt_payment_method: {str(e)}")

@log_function_call(logger)
@bot.callback_query_handler(func=lambda call: call.data in ["pay_full", "pay_bonus"])
async def callback_choose_payment_method(call):
    try:
        username = call.from_user.username
        chat_id = call.message.chat.id

        await bot.answer_callback_query(call.id)

        if chat_id not in PAYMENT_STATE:
            logger.warning(f"Payment session not found for user {chat_id}.")
            await bot.send_message(chat_id=chat_id, text="Сессия оплаты не найдена. Попробуйте сначала выбрать подписку.")
            return

        user_state = PAYMENT_STATE[chat_id]

        try:
            choose_payment_method_id = user_state.get("choose_payment_method_id")
            if choose_payment_method_id:
                await remove_message(chat_id, choose_payment_method_id)
                user_state["choose_payment_method_id"] = None

            invoice_msg_id = user_state.get("invoice_msg_id")
            if invoice_msg_id:
                await remove_message(chat_id, invoice_msg_id)
                user_state["invoice_msg_id"] = None
        except Exception as e:
            logger.error(f"Error removing messages: {str(e)}")

        if call.data == "pay_full":
            user_state["state"] = "WAITING_PAYMENT"
            user_state["bonus_input"] = 0
            await send_invoice_with_bonus(call.message)
            
        elif call.data == "pay_bonus":
            user_state["state"] = "CHOOSE_BONUS_AMOUNT"
            
            full_price = user_state.get("full_price")//100
            balance = middleware.referrals.get_balance(chat_id)
            max_bonus_to_pay = full_price - MINMUM_BONUS_PAYMENT
            if max_bonus_to_pay > balance:
                max_bonus_to_pay = balance

            text = (
                f"├─ *Минимальная сумма оплаты: >=* `{MINMUM_BONUS_PAYMENT}` руб.\n"
                f"├─ У вас на счету: `{balance}` мяу-коинов\n"
                f"└─ Можете потратить максимум: `{max_bonus_to_pay}` коинов\n\n"
                "Введите, сколько бонусов хотите потратить (числом)."
            )
            await bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in callback_choose_payment_method: {str(e)}")

def in_payment_process(message) -> bool:
    try:
        chat_id = message.chat.id
        if chat_id not in PAYMENT_STATE:
            return False
        return PAYMENT_STATE[chat_id]["state"] in ("CHOOSE_BONUS_AMOUNT", "WAITING_PAYMENT")
    except Exception as e:
        logger.error(f"Error in in_payment_process: {str(e)}")
        return False

@log_function_call(logger)
@bot.message_handler(func=in_payment_process, content_types=['text'])
async def bonus_input_handler(message):
    try:
        username = message.from_user.username
        chat_id = message.chat.id
        
        if chat_id not in PAYMENT_STATE:
            return

        st = PAYMENT_STATE[chat_id]
        user_state = st["state"]
        invoice_msg_id = st["invoice_msg_id"]
        choose_payment_method_id = st["choose_payment_method_id"]
        full_price = st["full_price"]

        if not message.text.isdigit():
            try:
                if choose_payment_method_id:
                    await remove_message(chat_id, choose_payment_method_id)
                if invoice_msg_id:
                    await remove_message(chat_id, invoice_msg_id)
            except Exception as e:
                logger.error(f"Error removing messages: {str(e)}")
            PAYMENT_STATE.pop(chat_id, None)
            logger.info(f"User {chat_id} sent invalid input. Payment state cleared.")
            await bot.send_message(chat_id=chat_id, text="Вы ввели некорректное значение. Сессия оплаты сброшена.")
            return

        if user_state == "WAITING_PAYMENT":
            try:
                if invoice_msg_id:
                    await remove_message(chat_id, invoice_msg_id)
            except Exception as e:
                logger.error(f"Error removing invoice message: {str(e)}")
            PAYMENT_STATE.pop(chat_id, None)
            logger.info(f"User {chat_id} sent input while WAITING_PAYMENT. Payment state cleared.")
            await bot.send_message(chat_id=chat_id, text="Счёт аннулирован. Повторите покупку заново.")
            return

        bonus_requested = int(message.text.strip())
        balance = middleware.referrals.get_balance(chat_id)
        price_to_pay = full_price//100 - bonus_requested
        
        if bonus_requested > balance:
            await bot.send_message(chat_id=chat_id, text="У вас недостаточно бонусов. Введите меньшее число.")
            logger.info(f"User {chat_id} tried to pay more than they have. Requested: {bonus_requested}.")
            return

        if price_to_pay < MINMUM_BONUS_PAYMENT:
            await bot.send_message(chat_id=chat_id, text=f"Минимальная сумма оплаты должна быть >= `{MINMUM_BONUS_PAYMENT}` руб.", parse_mode='Markdown')
            logger.info(f"User {chat_id} tried to pay less than minimum. Minimum: {bonus_requested}.")
            return

        st["bonus_input"] = bonus_requested
        st["state"] = "WAITING_PAYMENT"
        await send_invoice_with_bonus(message)
    except Exception as e:
        logger.error(f"Error in bonus_input_handler: {str(e)}")



@log_function_call(logger)
async def send_invoice_with_bonus(message):
    """
    Формируем invoice (buy) с учётом бонусов и удаляем старые сообщения (invoice, prompt).
    """
    tg_id = message.chat.id
    if tg_id not in PAYMENT_STATE:
        return

    st = PAYMENT_STATE[tg_id]
    full_price = st["full_price"]
    description = st["description"]
    bonus_used = st["bonus_input"]
    payload = st["payload"]

    discount = bonus_used * 100
    price_to_pay = max(full_price - discount, 0)

    old_invoice_id = st.get("invoice_msg_id")
    if old_invoice_id:
        await remove_message(tg_id, old_invoice_id)
        st["invoice_msg_id"] = None

    if bonus_used > 0:
        product_description = f"Скидка {bonus_used} бонусов"
    else:
        product_description = f"Полная стоимость"

    product = {
        "label": description,
        "amount": price_to_pay,
        "description": product_description,
        "payload": payload
    }

    choose_msg_id = st.get("choose_payment_method_id")
    if choose_msg_id:
        await remove_message(tg_id, choose_msg_id)
        st["choose_payment_method_id"] = None

    try:
        invoice_msg = await buy(message, product)
        if invoice_msg:
            st["invoice_msg_id"] = invoice_msg.message_id
    except Exception as e:
        logger.error(f"Error sending invoice to user {tg_id}: {str(e)}")