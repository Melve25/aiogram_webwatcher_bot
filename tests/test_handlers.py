import pytest
from aiogram.types import Message, User, Chat, CallbackQuery
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession

from app.handlers.states import WebsiteUrl
from app.handlers.handlers import greeting_handler, add_website_handler, exit_state_handler, get_url_handler, delete_website_handler, delete_website_callback, list_websites_handler, help_handler

pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_message(mocker: MockerFixture) -> Message:
	from_user = User(id=123, is_bot=False, first_name='TestUser')
	chat = Chat(id=123, type='private')
	message = mocker.Mock(spec=Message)
	message.from_user = from_user
	message.chat = chat
	message.answer = mocker.AsyncMock()
	return message

@pytest.fixture
def mock_callback(mocker: MockerFixture) -> CallbackQuery:
    callback = mocker.Mock(spec=CallbackQuery)
    callback.data = 'delete:123'
    callback.answer = mocker.AsyncMock()
    callback.message = mocker.Mock(spec=Message)
    callback.message.edit_text = mocker.AsyncMock()
    return callback

async def test_start_command(session: AsyncSession, mock_message: Message, mocker: MockerFixture):
	mocker.patch('app.handlers.handlers.get_or_create_user', return_value=None)

	await greeting_handler(message=mock_message, session=session)

	mock_message.answer.assert_called_once_with('Привет TestUser')

async def test_add_command(mock_message: Message, mocker: MockerFixture):
	mock_state = mocker.AsyncMock()

	await add_website_handler(message=mock_message, state=mock_state)

	mock_message.answer.assert_called_once_with('Отправьте мне URL сайта, который нужно отслеживать')
	mock_state.set_state.assert_called_once_with(WebsiteUrl.url)

async def test_exit_state_none(mock_message: Message, mocker: MockerFixture):
	mock_state = mocker.AsyncMock()
	mock_state.get_state.return_value = None

	await exit_state_handler(message=mock_message, state=mock_state)

	mock_message.answer.assert_called_once_with("Я ничего от вас не жду мне нечего сбрасывать")
	mock_state.clear.assert_not_called()

async def test_exit_state_has_state(mock_message: Message, mocker: MockerFixture):
	mock_state = mocker.AsyncMock()
	mock_state.get_state.return_value = "some state"
	
	await exit_state_handler(message=mock_message, state=mock_state)

	mock_state.clear.assert_called_once()
	mock_message.answer.assert_called_once_with("Чем могу помочь ещё?")

async def test_get_url_handler_success(session: AsyncSession, mock_message: Message, mocker: MockerFixture):
	mock_state = mocker.AsyncMock()
	mocker.patch('app.handlers.handlers.add_website_for_user', return_value=(True, 'https://google.com'))

	await get_url_handler(message=mock_message, session=session, state=mock_state)

	mock_state.update_data.assert_called_once_with(url='https://google.com')
	mock_state.clear.assert_called_once()
	mock_message.answer.assert_called_once_with('Отлично я начал следить за сайтом https://google.com')

async def test_get_url_handler_failure(session: AsyncSession, mock_message: Message, mocker: MockerFixture):
	mock_state = mocker.AsyncMock()
	mocker.patch('app.handlers.handlers.add_website_for_user', return_value=(False, 'Ошибка'))

	await get_url_handler(message=mock_message, session=session, state=mock_state)

	mock_message.answer.assert_called_once_with('Ошибка')

async def test_delete_command_no_websites(session: AsyncSession, mock_message: Message, mocker: MockerFixture):
	mocker.patch('app.handlers.handlers.get_user_websites', return_value=[])

	await delete_website_handler(message=mock_message, session=session)

	mock_message.answer.assert_called_once_with("❌ У тебя пока нет сайтов.")

async def test_delete_command_has_websites(session: AsyncSession, mock_message: Message, mocker: MockerFixture):

	mock_website = mocker.Mock()
	mock_websites = [mock_website]
	mocker.patch('app.handlers.handlers.get_user_websites', return_value=mock_websites)

	mock_keyboard = mocker.Mock()
	mocker.patch('app.handlers.handlers.inline_websites', return_value=mock_keyboard)

	await delete_website_handler(message=mock_message, session=session)

	mock_message.answer.assert_called_once_with("Выбери сайт за которым больше не нужно следить: ", reply_markup=mock_keyboard)

async def test_delete_callback(session: AsyncSession, mock_callback: CallbackQuery, mocker: MockerFixture):
	delete_mock = mocker.patch('app.handlers.handlers.delete_user_website', return_value=None)

	await delete_website_callback(callback=mock_callback, session=session)

	delete_mock.assert_called_once_with(123, session=session)
	mock_callback.answer.assert_called_once_with('🗑️ Сайт удалён.')
	mock_callback.message.edit_text.assert_called_once_with('Сайт успешно удалён ✅')


async def test_list_websites_no_websites(session: AsyncSession, mock_message: Message, mocker: MockerFixture):
	mocker.patch('app.handlers.handlers.get_user_websites', return_value=[])

	await list_websites_handler(message=mock_message, session=session)

	mock_message.answer.assert_called_once_with("❌ У тебя пока нет сайтов.")

async def test_list_websites_has_websites(session: AsyncSession, mock_message: Message, mocker: MockerFixture):
	mock_website = mocker.Mock()
	mock_website.url = 'https://google.com'
	mock_websites = [mock_website]
	mocker.patch('app.handlers.handlers.get_user_websites', return_value=mock_websites)

	await list_websites_handler(message=mock_message, session=session)

	mock_message.answer.assert_called_once()
	args, kwargs = mock_message.answer.call_args
	assert "🌐 Твои сайты:" in args[0]
	assert "https://google\\.com" in args[0]
	assert kwargs.get('parse_mode') == 'Markdown'

async def test_help(mock_message: Message):
	await help_handler(mock_message)

	mock_message.answer.assert_called_once_with("Телеграм-бот, который следит за доступностью и внешним видом сайтов")
