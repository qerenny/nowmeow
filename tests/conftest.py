# tests/conftest.py

import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from telebot.async_telebot import AsyncTeleBot
import sys
import os

# Добавляем корневую папку в путь, если нужно
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

@pytest.fixture(scope="function")
def event_loop():
    """
    Переопределяем event_loop, если нужно.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_db_cursor():
    """
    Пример фикстуры, которая подменяет const.const_db.CUR, чтобы он не был None.
    """
    with patch("const.const_db.CUR", autospec=True) as mock_cur:
        yield mock_cur


@pytest.fixture
def mock_bot():
    """
    Подменяем все ключевые методы бота, чтобы они не ходили в реальный Telegram.
    """
    with patch("bot.bot_init.bot", autospec=True) as bot_mock:
        # делаем методы async
        bot_mock.send_message = AsyncMock()
        bot_mock.send_photo = AsyncMock()
        bot_mock.answer_callback_query = AsyncMock()
        bot_mock.delete_message = AsyncMock()
        bot_mock.buy = AsyncMock()  # Добавьте все необходимые методы

        yield bot_mock