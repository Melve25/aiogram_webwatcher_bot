from aiogram import Bot
from aiogram.types import FSInputFile
from pathlib import Path

from app.services.dao import get_all_websites
from app.services.scraper import take_screenshot
from app.db.database import AsyncSessionLocal

SCREENSHOTS_PATH = Path(__file__).parent.parent / 'screenshots'
SCREENSHOTS_PATH.mkdir(exist_ok=True)

async def check_websites(bot: Bot):
	"""Основная функция, которую будет запускать планировщик.
    Проверяет все сайты и отправляет уведомления в случае сбоя."""
	async with AsyncSessionLocal() as session:
		websites = await get_all_websites(session=session)
		
		for website in websites:
			screenshot = await take_screenshot(website.url)
			screenshot_path = SCREENSHOTS_PATH / f"{website.id}.png"

			if screenshot is None:
				try:
					if screenshot_path.exists():
						last_good_screenshot = FSInputFile(screenshot_path)
						await bot.send_photo(
							chat_id=website.user.telegram_id,
							photo=last_good_screenshot,
							caption=f'⚠️ Тревога! Сайт {website.url} не отвечает! Это последний удачный скриншот.'
						)
					else:
						await bot.send_message(
							chat_id=website.user.telegram_id,
							text=f'⚠️ Тревога! Сайт {website.url} не отвечает или работает некорректно!'
						)
				except Exception as e:
					print(f"Failed to send alert for {website.url}: {e}")
			else:
				screenshot_to_save = SCREENSHOTS_PATH / f'{website.id}.png'
				with open(screenshot_to_save, 'wb') as f:
					f.write(screenshot)
				print(f'Website {website.url} is OK.')