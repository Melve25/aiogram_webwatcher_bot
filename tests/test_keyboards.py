import pytest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.services.keyboards import inline_websites
from app.db.models import Website

pytestmark = pytest.mark.asyncio

async def test_inline_website_keyboards():
	"""
	Проверяем, что функция inline_websites правильно создаёт клавиатуру.
	"""

	mock_website = [
		Website(id=1, url="https://google.com"),
		Website(id=2, url="https://youtube.com")
	]

	keyboard = await inline_websites(mock_website)

	assert isinstance(keyboard, InlineKeyboardMarkup)
	assert len(keyboard.inline_keyboard) == 1
	assert len(keyboard.inline_keyboard[0]) == 2

	button1: InlineKeyboardButton = keyboard.inline_keyboard[0][0]
	assert button1.text == "https://google.com"
	assert button1.callback_data == "delete:1"