# tests/test_bot/test_referrals.py
import pytest
from unittest.mock import patch, AsyncMock
from bot.handlers.referrals import show_referrals_menu, referrals_menu_callback, referrals_start

@pytest.mark.asyncio
async def test_show_referrals_menu(mock_bot):
    """
    Проверяем отображение меню рефералов для пользователя.
    """
    # Настраиваем callback
    call = AsyncMock()
    call.from_user.username = "user"
    call.message.chat.id = 1111

    # Патчим зависимости
    with patch("middleware.connection.login_db"), \
         patch("middleware.referrals.select_active_users_by_referrer", return_value=[]), \
         patch("middleware.referrals.get_balance", return_value=50):

        # Вызываем тестируемую функцию
        await show_referrals_menu(call)

    # Проверяем, что send_photo был вызван один раз
    mock_bot.send_photo.assert_awaited_once()

    # Извлекаем аргументы вызова
    _, kwargs = mock_bot.send_photo.call_args
    assert kwargs["chat_id"] == 1111
    assert "reply_markup" in kwargs
    assert "parse_mode" in kwargs

# tests/test_bot/test_referrals.py

import pytest
from unittest.mock import AsyncMock, patch
from bot.handlers.referrals import referrals_menu_callback

@pytest.mark.asyncio
async def test_referrals_menu_callback_link(mock_bot):
    """
    Проверяем обработку callback 'referrals_link'
    """
    call = AsyncMock()
    call.data = "referrals_link"
    call.id = "callback_query_id"
    call.message.chat.id = 2222

    # Ожидаемый текст или другие действия
    referral_link = "https://example.com/referral?code=9999"

    with patch("bot.handlers.referrals.referral_link", return_value=referral_link):

        await referrals_menu_callback(call)

    mock_bot.send_message.assert_awaited_once_with(chat_id=2222, text=referral_link)

@pytest.mark.asyncio
async def test_referrals_menu_callback_rules(mock_bot):
    call = AsyncMock()
    call.data = "referrals_rules"
    call.message.chat.id = 3333

    with patch("bot.handlers.referrals.referral_rules") as mock_rules:
        await referrals_menu_callback(call)
    mock_rules.assert_called_once()

@pytest.mark.asyncio
async def test_referral_info():
    from bot.handlers.referrals import referral_info
    call = AsyncMock()
    call.message.chat.id = 4444
    with patch("middleware.connection.login_db"), \
         patch("middleware.referrals.select_active_users_by_referrer", return_value=[1001, 1002]), \
         patch("middleware.referrals.get_balance", return_value=150) as mock_balance:
        text = await referral_info(call)
    assert "active=2" not in text  # это лог, а не сам текст
    assert "150" in text

@pytest.mark.asyncio
async def test_referrals_start_new_user_no_refcode(mock_bot):
    """
    Пользователь не существует в users, нет рефкода (или /start без кода), нет в referrals
    """
    from bot.handlers.referrals import referrals_start
    message = AsyncMock()
    message.chat.id = 5555
    referral_code = ["/start"]
    exists_in_users = False
    exists_in_referrals = False

    with patch("middleware.referrals.insert_user_referrals") as mock_insert_ref:
        await referrals_start(message, exists_in_users, exists_in_referrals, referral_code)
    mock_insert_ref.assert_called_once()

@pytest.mark.asyncio
async def test_referrals_start_new_user_with_refcode(mock_bot):
    """
    Пользователь не существует в users, получает рефкод -> ensure_referral_record -> OK
    """
    message = AsyncMock()
    message.chat.id = 6666
    message.text = "/start 9999"
    referral_code = ["/start", "9999"]
    exists_in_users = False
    exists_in_referrals = False

    referrer_chat_id = 7777  # Валидный chat_id реферера
    referrer_text = "Ваш реферальный код активирован!"

    # Патчим зависимости
    with patch("middleware.referrals.ensure_referral_record", return_value=True), \
         patch("middleware.referrals.insert_update_referrer"), \
         patch("middleware.referrals.update_balance"), \
         patch("middleware.referrals.get_referrer_chat_id", return_value=referrer_chat_id):

        await referrals_start(message, exists_in_users, exists_in_referrals, referral_code)

    mock_bot.send_message.assert_awaited_once_with(chat_id=referrer_chat_id, text=referrer_text)

@pytest.mark.asyncio
async def test_referrals_start_existing_user(mock_bot):
    """
    Если пользователь уже есть в users, ничего не делаем
    """
    message = AsyncMock()
    message.chat.id = 7777
    referral_code = ["/start"]
    exists_in_users = True
    exists_in_referrals = False

    with patch("middleware.referrals.insert_user_referrals") as mock_insert:
        await referrals_start(message, exists_in_users, exists_in_referrals, referral_code)
    mock_insert.assert_not_called()

@pytest.mark.asyncio
async def test_referrals_start_invalid_refcode(mock_bot):
    """
    Код не одобрен ensure_referral_record -> отправляется invalid_referral_code
    """
    message = AsyncMock()
    message.chat.id = 8888
    referral_code = ["/start", "1234"]
    exists_in_users = False
    exists_in_referrals = False

    with patch("middleware.referrals.ensure_referral_record", return_value=False), \
         patch("bot.bot_init.bot.send_message") as mock_sm:
        await referrals_start(message, exists_in_users, exists_in_referrals, referral_code)

    mock_sm.assert_called_with(8888, "Мяу! Этот реферальный код не подходит. Попробуй другой! 🐾")