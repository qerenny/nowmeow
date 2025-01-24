#payment.py
from telebot.types import LabeledPrice
import middleware.connection
import middleware.user
from bot.handlers.instructions import show_instructions
from bot.messages import messages
from bot.bot_init import bot
from const.const_bot import CURRENCY, HANDLERS_JSON_PATH, LOGGER_PRESET, PAYMENT_STATE
from utils import json_fun
from utils.logging_utils import retry_on_error, log_function_call, setup_logger
from bot.bot_base_fun import remove_message, expiry_date_view
from utils.config import BOT_TEST_PROVIDER_TOKEN

logger = setup_logger('payments', 'bot.log')


@log_function_call(logger)
async def buy(message, product):
    """
    Sends an invoice to the user for a chosen subscription product.
    """
    try:
        prices = [LabeledPrice(label=product['label'], amount=product['amount'])]
        json_data = json_fun.receipt_creator(f'{HANDLERS_JSON_PATH}json/receipt.json', product['description'], product['amount'])

        msg_invoice = await bot.send_invoice(
            message.chat.id,
            title=product['label'],
            description=product['description'],
            provider_token=BOT_TEST_PROVIDER_TOKEN,
            currency=CURRENCY,
            prices=prices,
            start_parameter='subscription',
            invoice_payload=product['payload'],
            need_email=True,
            send_email_to_provider=True,
            provider_data=json_data,
        )
        logger.info(f"Invoice for {product['label']} sent successfully.")

        return msg_invoice
    except Exception as e:
        logger.error(f"Error in buy: {str(e)}")
        await bot.send_message(
            chat_id=message.chat.id,
            text="❌ Произошла ошибка при создании платежа. Пожалуйста, попробуйте позже или обратитесь в поддержку 😿"
        )
        raise


@log_function_call(logger)
@bot.pre_checkout_query_handler(func=lambda query: True)
async def process_pre_checkout_query(pre_checkout_query):
    """
    Confirms the checkout query before finalizing payment.
    """
    try:
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
        logger.info("Pre-checkout query answered with OK=True.")
    except Exception as e:
        logger.error(f"Error in process_pre_checkout_query: {str(e)}")
        await bot.answer_pre_checkout_query(
            pre_checkout_query.id,
            ok=False,
            error_message="❌ К сожалению, произошла ошибка при проверке платежа. Попробуйте позже 😿"
        )
        raise


@log_function_call(logger)
@bot.message_handler(content_types=['successful_payment'])
async def successful_payment(message):
    """
    Handles a successful payment event.
    """
    tg_id = message.chat.id

    try:
        try:
            payment_info = message.successful_payment
            payment_amount = payment_info.total_amount // 100
            payment_currency = payment_info.currency
        except AttributeError as e:
            logger.error(f"Error retrieving payment information for tg_id={tg_id}: {str(e)}")
            raise

        try:
            if tg_id in PAYMENT_STATE:
                invoice_msg_id = PAYMENT_STATE[tg_id]["invoice_msg_id"]
                bonus_input = PAYMENT_STATE[tg_id]["bonus_input"]
        except KeyError as e:
            logger.error(f"Error accessing PAYMENT_STATE for tg_id={tg_id}: {str(e)}")

        if invoice_msg_id:
            try:
                await remove_message(tg_id, invoice_msg_id)
            except Exception as e:
                logger.error(f"Error removing message with invoice_msg_id={invoice_msg_id} for tg_id={tg_id}: {str(e)}")

        if bonus_input > 0:
            try:
                middleware.referrals.update_balance(tg_id, -bonus_input)
                logger.info(f"Deducted {bonus_input} bonuses from user {tg_id}")
            except Exception as e:
                logger.error(f"Error deducting bonuses for tg_id={tg_id}: {str(e)}")
                await bot.send_message(
                    chat_id=tg_id,
                    text="❌ Произошла ошибка при списании бонусов. Пожалуйста, свяжитесь с поддержкой."
                )
                raise

        await bot.send_message(
            chat_id=tg_id,
            text=f'✅ Мур-мур! Платёж на {payment_amount} {payment_currency} прошёл успешно!\n'
            f'⌛ Сейчас наш котик всё настроит, подожди немножко 😺'
        )

        await give_subscription(message, payment_info.invoice_payload)

        PAYMENT_STATE.pop(tg_id, None)

    except Exception as e:
        logger.error(f"Unhandled error in successful_payment for tg_id={tg_id}: {str(e)}")
        await bot.send_message(
            chat_id=tg_id,
            text="❌ Произошла непредвиденная ошибка. Пожалуйста, попробуйте позже или обратитесь в поддержку."
        )
        raise


@log_function_call(logger)
@bot.message_handler(content_types=['unsuccessful_payment'])
async def unsuccessful_payment(message):
    """
    Handles an unsuccessful payment event.
    """
    tg_id = message.chat.id

    try:
        try:
            if tg_id in PAYMENT_STATE:
                invoice_msg_id = PAYMENT_STATE[tg_id].get("invoice_msg_id")
        except KeyError as e:
            logger.error(f"Error accessing invoice_msg_id in PAYMENT_STATE for tg_id={tg_id}: {str(e)}")
        if invoice_msg_id:
            try:
                await remove_message(tg_id, invoice_msg_id)
            except Exception as e:
                logger.error(f"Error removing message with invoice_msg_id={invoice_msg_id} for tg_id={tg_id}: {str(e)}")
        PAYMENT_STATE.pop(tg_id, None)

        await bot.send_message(
            chat_id=tg_id,
            text="❌ К сожалению, платёж не удался. Это может произойти по нескольким причинам:\n\n"
            "• Недостаточно средств на карте\n"
            "• Банк отклонил операцию\n"
            "• Технические проблемы на стороне платёжной системы\n\n"
            "Попробуйте использовать другую карту или повторите попытку позже. "
            "Если проблема сохраняется, обратитесь в поддержку."
        )
        logger.info(f"Unsuccessful payment message sent to user tg_id={tg_id}.")

    except Exception as e:
        logger.error(f"Unhandled error in unsuccessful_payment for tg_id={tg_id}: {str(e)}")
        raise


@log_function_call(logger)
async def give_subscription(message, period):
    """
    Applies subscription logic after successful or trial request.
    """
    tg_id = message.chat.id

    try:
        middleware.connection.login_3x()
        middleware.connection.login_db()
    except Exception as e:
        logger.error(f"Error during login_db for tg_id={tg_id}: {str(e)}")
        raise

    try:
        user_exists = middleware.user.get_user_exists_in_user(tg_id)
    except Exception as e:
        logger.error(f"Error checking if user exists for tg_id={tg_id}: {str(e)}")
        raise

    if user_exists:
        try:
            logger.info(f"Updating existing user tg_id={tg_id}.")
            middleware.user.create_or_update_user(tg_id, period, message.from_user.username)
        except Exception as e:
            logger.error(f"Error updating user tg_id={tg_id}: {str(e)}")
            raise

        try:
            text = f'✅ {messages.get_random_message("subscription_updated")}'
            await bot.send_message(chat_id=tg_id, text=text, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error sending subscription update message to tg_id={tg_id}: {str(e)}")

        try:
            text = await expiry_date_view("subscription_update_date", tg_id)
            await bot.send_message(chat_id=tg_id, text=text, parse_mode='Markdown')
            logger.info(f"Subscription updated for tg_id={tg_id}.")
        except Exception as e:
            logger.error(f"Error displaying subscription expiry date for tg_id={tg_id}: {str(e)}")

    else:
        try:
            logger.info(f"Creating new user tg_id={tg_id}.")
            data = middleware.user.create_or_update_user(tg_id, period, message.from_user.username)
        except Exception as e:
            logger.error(f"Error creating user tg_id={tg_id}: {str(e)}")
            raise

        try:
            text = await expiry_date_view("expiration", tg_id)
            await bot.send_message(chat_id=tg_id, text=text, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error sending subscription expiry date to new user tg_id={tg_id}: {str(e)}")

        try:
            text = f'🔑 {messages.get_random_message("new_subscription_key")} 🐾'
            await bot.send_message(chat_id=tg_id, text=f'{text}\n```{data}```', parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error sending subscription key to tg_id={tg_id}: {str(e)}")

        try:
            await show_instructions(message)
        except Exception as e:
            logger.error(f"Error showing instructions to tg_id={tg_id}: {str(e)}")

        logger.info(f"New user created with tg_id={tg_id}.")