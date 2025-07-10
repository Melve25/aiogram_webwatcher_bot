import pytest
from pytest_mock import MockerFixture
from aiogram.types import User as AiogramUser, Message, Chat
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import User, Website
from app.services.dao import create_user, get_or_create_user,add_website_for_user, get_all_websites, get_user_websites, delete_user_website

pytestmark = pytest.mark.asyncio
@pytest.fixture
def mock_message() -> Message:
	"""
	Фикстура, создающая мок объект Message от aiogram.
	"""
	return Message(
		message_id=123,
		date=123456789,
		chat=Chat(id=1, type='private'),
		from_user=AiogramUser(id=1, is_bot=False, first_name='Test'),
		text='https://example.com',
	)

# NOTE: тесты для create_user
async def test_create_user(session: AsyncSession, mock_message: Message):
	user = create_user(session=session, message=mock_message)

	assert user.telegram_id == mock_message.from_user.id

# NOTE: тесты для get_or_create_user
async def test_get_or_create_user_if_not_exists(session: AsyncSession, mock_message: Message):
	result = await session.execute(select(User).where(User.telegram_id == mock_message.from_user.id))
	user = result.scalar_one_or_none()
	assert user is None

	await get_or_create_user(session=session, message=mock_message)

	result = await session.execute(select(User).where(User.telegram_id == mock_message.from_user.id))
	user = result.scalar_one_or_none()

	assert user is not None
	assert user.telegram_id == mock_message.from_user.id

# NOTE: тесты для add_website_for_user
async def test_add_website_for_user(session: AsyncSession, mock_message: Message, mocker: MockerFixture):
	"""
	Проверяем добавление сайта в базу.
	Здесь `session` - это наша фикстура с чистой БД.
	`mocker` - встроенная фикстура из pytest-mock
	"""

	mocker.patch('app.services.dao.is_website_alive', return_value=True)
	await get_or_create_user(session, mock_message)

	success, info = await add_website_for_user(session=session, message=mock_message)

	assert success is True
	assert info == "https://example.com/"

async def test_add_website_with_invalid_url(session: AsyncSession, mocker: MockerFixture):
	mock_message = mocker.Mock()
	mock_message.text = 'это не url'

	success, info = await add_website_for_user(session=session, message=mock_message)

	assert success is False
	assert info == "Некорректный URL. Пожалуйста, введите правильный адрес сайта."

async def test_add_duplicate_website(session: AsyncSession, mock_message: Message, mocker: MockerFixture):
	mocker.patch('app.services.dao.is_website_alive', return_value=True)
	await get_or_create_user(session, mock_message)
	await add_website_for_user(session=session, message=mock_message)

	success, info = await add_website_for_user(session=session, message=mock_message)

	assert success is False
	assert info == "Этот сайт уже добавлен."

async def test_add_dead_website(session: AsyncSession, mock_message: Message, mocker: MockerFixture):
	mocker.patch('app.services.dao.is_website_alive', return_value=False)
	await get_or_create_user(session, mock_message)

	success, info = await add_website_for_user(session=session, message=mock_message)

	assert success is False
	assert info == "Сайт не отвечает. Проверьте URL и попробуйте снова."

# NOTE: тесты get_all_websites
async def test_get_all_websites(session: AsyncSession):
	user1 = User(telegram_id=1)
	user2 = User(telegram_id=2)
	session.add_all([user1, user2])
	await session.commit()
	
	website1 = Website(url='https://example1.com', user_id=user1.id)
	website2 = Website(url='https://example2.com', user_id=user2.id)

	session.add_all([website1, website2])
	await session.commit()

	websites = await get_all_websites(session=session)

	assert isinstance(websites, list)
	assert isinstance(websites[0], Website)
	assert len(websites) == 2

	urls = [w.url for w in websites]
	assert 'https://example1.com' in urls
	assert 'https://example2.com' in urls

# NOTE: тесты get_user_websites
async def test_get_user_websites(session: AsyncSession, mock_message: Message):
	websites = await get_user_websites(session=session, message=mock_message)
	assert len(websites) == 0

	website = Website(url=mock_message.text, user_id=mock_message.from_user.id)
	session.add(website)
	await session.commit()

	websites = await get_user_websites(session=session, message=mock_message)

	assert isinstance(websites, list)
	assert isinstance(websites[0], Website)
	assert len(websites) == 1

	urls = [w.url for w in websites]
	assert 'https://example.com' in urls

# NOTE: тесты delete_user_website
async def test_delete_user_website(session: AsyncSession, mock_message: Message):
	user = create_user(session=session, message=mock_message)
	website = Website(url=mock_message.text, user_id=mock_message.from_user.id)
	session.add(website)
	await session.commit()

	await delete_user_website(session=session, website_to_delete_id=website.id)

	result = await session.execute(select(Website).where(Website.id == website.id))
	website = result.scalar_one_or_none()
	assert website is None
	
	
	