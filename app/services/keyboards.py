from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.db.models import Website

async def inline_websites(websites: list[Website]):
	keyboard = InlineKeyboardBuilder()
	for website in websites:
		keyboard.add(InlineKeyboardButton(
			text=website.url, 
			callback_data=f'delete:{website.id}'
		)
	)
	return keyboard.adjust(2).as_markup()
