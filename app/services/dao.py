from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from aiogram.types import Message
from pydantic import ValidationError

from app.db.models import User, Website
from app.services.validation import WebsiteUrlModel, is_website_alive


def create_user(session: AsyncSession, message: Message):
	"""Запись пользователя в базу."""
	new_user = User(
		telegram_id=message.from_user.id
	)
	session.add(new_user)
	return new_user

async def get_or_create_user(session: AsyncSession, message: Message) -> None:
	"""Создание/Получение пользователя."""
	result = await session.execute(select(User).where(User.telegram_id == message.from_user.id))
	user = result.scalar_one_or_none()
	if not user:
		create_user(session=session, message=message)
		await session.commit()

async def add_website_for_user(session: AsyncSession, message: Message) -> tuple[bool, str]:
	"""Добавление сайта для пользователя за котором нужно следить."""
	try:
		website_url = WebsiteUrlModel(url=message.text)
	except ValidationError:
		return False, "Некорректный URL. Пожалуйста, введите правильный адрес сайта."
	
	result = await session.execute(select(User).where(User.telegram_id == message.from_user.id))
	user = result.scalar_one_or_none()

	if not user:
		return False, "Пользователь не найден, попробуйте заново."

	result = await session.execute(select(Website).where(Website.user_id == user.id))
	website = result.scalars().all()

	if str(website_url.url) in (w.url for w in website):
		return False, "Этот сайт уже добавлен." 
	
	if not await is_website_alive(str(website_url.url)):
		return False, "Сайт не отвечает. Проверьте URL и попробуйте снова."

	new_website = Website(
		url=str(website_url.url),
		user_id=user.id
	)
	session.add(new_website)
	await session.commit()
	return True, str(website_url.url)

async def get_all_websites(session: AsyncSession) -> list[Website]:
	"""Возвращает список всех сайтов всех пользователей для мониторинга."""
	result = await session.execute(select(Website))
	websites = result.scalars().all()
	return websites
	
async def get_user_websites(message: Message, session: AsyncSession) -> list[Website]:
	"""Возвращает список всех сайтов пользователя."""
	result = await session.execute(select(User).where(User.telegram_id == message.from_user.id))
	user = result.scalar_one_or_none()
	if not user:
		user = create_user(session=session, message=message)
		await session.commit()
		return []
	
	result = await session.execute(select(Website).where(Website.user_id == user.id))
	websites = result.scalars().all()

	return websites


async def delete_user_website(website_to_delete_id: int, session: AsyncSession) -> None:
	"""Удаление сайт пользователя по id сайта."""
	result = await session.execute(select(Website).where(Website.id == website_to_delete_id))
	website = result.scalar_one_or_none()
	
	await session.delete(website)
	await session.commit()
	

